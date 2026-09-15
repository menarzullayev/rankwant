package main

import (
	"context"
	"testing"
)

// Judge hack mantig'ini BILMAYDI — u faqat marshrutni qaytaradi.
//
// Bir hack uchta ish ochadi (generator, etalon yechim, himoyachi) va
// ular navbatda aralashib keladi. `hack_id` yoki `hack_stage` yo'qolsa,
// API javobni qaysi hackka bog'lashni bilmaydi va hack abadiy
// «tekshirilmoqda» bo'lib qolardi.
func TestJudgeEchoesHackRouting(t *testing.T) {
	fakeSandbox(t, rejectsZero)
	job := validatedJob("1 2\n")
	job.ValidateInput = false
	job.HackID = 42
	job.HackStage = "reference"

	res := judge(context.Background(), job, nil)

	if res.HackID != 42 || res.HackStage != "reference" {
		t.Fatalf("natijada hack_id=%d hack_stage=%q — 42/\"reference\" kutilgan",
			res.HackID, res.HackStage)
	}
}

// Oddiy submission hack maydonlarisiz keladi: natijada ular bo'sh
// qolishi kerak, aks holda `omitempty` ishlamay har javobga begona
// maydon qo'shilardi.
func TestJudgeLeavesHackRoutingEmptyForPlainJob(t *testing.T) {
	fakeSandbox(t, rejectsZero)
	job := validatedJob("1 2\n")
	job.ValidateInput = false

	res := judge(context.Background(), job, nil)

	if res.HackID != 0 || res.HackStage != "" {
		t.Fatalf("hack maydonlari to'ldirilgan: %d %q", res.HackID, res.HackStage)
	}
}
