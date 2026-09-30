package main

import (
	"os"
	"path/filepath"
)

const (
	defaultInputFile  = "input.txt"
	defaultOutputFile = "output.txt"
)

func ioMode(io IO) string {
	if io.Mode == "" {
		return "stdio"
	}
	return io.Mode
}

func outputFileName(io IO) string {
	if io.OutputFile != "" {
		return io.OutputFile
	}
	return defaultOutputFile
}

func inputFileName(io IO) string {
	if io.InputFile != "" {
		return io.InputFile
	}
	return defaultInputFile
}

// resetIOArtifacts removes stale output from the previous test so an old
// output.txt cannot mask a wrong stdout answer.
func resetIOArtifacts(work string, io IO) {
	mode := ioMode(io)
	if mode == "stdio" {
		return
	}
	_ = os.Remove(filepath.Join(work, outputFileName(io)))
}

func writeTestInputFile(work string, test Test, io IO) error {
	mode := ioMode(io)
	if mode != "both" && mode != "file" {
		return nil
	}
	return os.WriteFile(filepath.Join(work, inputFileName(io)), []byte(test.Input), 0o644)
}

// classifyAnswer applies stdout comparison and, when the job allows file I/O,
// also accepts a matching output.txt (Robocontest-style dual acceptance).
func classifyAnswer(out *runOutcome, test Test, lim Limits, work string, io IO) string {
	mode := ioMode(io)
	if mode == "stdio" {
		return classify(out, test, lim)
	}
	base := classify(out, test, lim)
	if base != VAC && base != VWA && base != VPE {
		return base
	}
	data, err := os.ReadFile(filepath.Join(work, outputFileName(io)))
	if err != nil {
		if mode == "file" {
			return VWA
		}
		return base
	}
	synth := *out
	synth.Stdout = string(data)
	fileV := classify(&synth, test, lim)
	if mode == "file" {
		return fileV
	}
	if base == VAC || fileV == VAC {
		return VAC
	}
	if base == VPE || fileV == VPE {
		return VPE
	}
	return VWA
}
