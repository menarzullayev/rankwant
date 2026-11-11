package main

import (
	"math"
	"regexp"
	"strconv"
	"strings"
)

// Checker types this judge grades. A job naming any other type is refused
// (IE): before ADR-0060 an unknown type fell through to the exact
// comparison, so a `real` job reaching an older build gave a correct
// `2.0` against the jury's `2` a WA instead of an error.
const (
	CheckerStandard    = "standard"
	CheckerSpecial     = "special"
	CheckerInteractive = "interactive"
	CheckerScorer      = "scorer"
	// CheckerReal compares numbers with a tolerance, inside the judge
	// (ADR-0060). It needs no checker program.
	CheckerReal = "real"
)

// DefaultEpsilon is the tolerance of a `real` job that does not name one:
// the 1e-6 of the Robocontest checker the Abramyan problems came with.
const DefaultEpsilon = 1e-6

func knownChecker(kind string) bool {
	switch kind {
	case "", CheckerStandard, CheckerSpecial, CheckerInteractive, CheckerScorer, CheckerReal:
		return true
	}
	return false
}

// Compare is how the output of a program that ran to the end is held
// against the jury's answer. The zero value is the exact comparison of
// normalised lines, which is what every job had before ADR-0060.
type Compare struct {
	// Epsilon > 0: numbers are equal within this tolerance, relative to
	// the jury's value and never tighter than absolute.
	Epsilon float64
}

// compareFor — the comparison a job asks for.
func compareFor(job *Job) Compare {
	if job.Checker.Type != CheckerReal {
		return Compare{}
	}
	eps := job.Checker.Epsilon
	if eps <= 0 {
		eps = DefaultEpsilon
	}
	return Compare{Epsilon: eps}
}

// compareAnswer — the verdict of a finished program's output.
func compareAnswer(got, want string, cmp Compare) string {
	if cmp.Epsilon > 0 {
		// Token by token, as the Robocontest checker read it: the layout
		// of the numbers is not the problem's question, so there is no PE.
		if realTokensMatch(got, want, cmp.Epsilon) {
			return VAC
		}
		return VWA
	}
	if normalise(got) == normalise(want) {
		return VAC
	}
	// Tokenlar mos, joylashuvi boshqa → algoritm to'g'ri, format xato.
	// `normalise` faqat QATOR OXIRIDAGI bo'shliqni kechiradi; bu yerda
	// esa qator uzilishi o'rniga probel qo'yilgan holat ham ushlanadi.
	if sameTokens(got, want) {
		return VPE
	}
	return VWA
}

// realToken is a decimal number as programs print it: `2`, `-0.5`, `.5`,
// `3.`, `1e-07`. Go's ParseFloat also reads `inf`, `nan`, `0x1p-2` and
// underscores; none of them is an answer, so they never reach it.
var realToken = regexp.MustCompile(`^[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$`)

func parseReal(token string) (float64, bool) {
	if !realToken.MatchString(token) {
		return 0, false
	}
	value, err := strconv.ParseFloat(token, 64)
	if err != nil || math.IsInf(value, 0) || math.IsNaN(value) {
		return 0, false
	}
	return value, true
}

// realTokensMatch — the same number of tokens, and each one right: where
// the jury wrote a number, the program's token is a number within
// eps·max(1, |jury|) of it; anywhere else the tokens are equal as text.
func realTokensMatch(got, want string, eps float64) bool {
	have, need := strings.Fields(got), strings.Fields(want)
	if len(have) != len(need) {
		return false
	}
	for i, token := range need {
		jury, isNumber := parseReal(token)
		if !isNumber {
			if have[i] != token {
				return false
			}
			continue
		}
		value, ok := parseReal(have[i])
		if !ok || math.Abs(value-jury) > eps*math.Max(1, math.Abs(jury)) {
			return false
		}
	}
	return true
}
