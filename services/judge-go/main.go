// judge-go — bake-off nomzod A: Go worker + nsjail.
//
// PULL protokoli (ADR-0004): navbatdan ish tortadi, kiruvchi port ochmaydi.
// DB credential OLMAYDI — faqat REDIS_URL.
package main

import (
	"context"
	"encoding/json"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/redis/go-redis/v9"
)

const (
	jobsKey    = "rankwant:judge:jobs"
	resultsKey = "rankwant:judge:results"
)

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	if os.Getenv("DATABASE_URL") != "" {
		// 06-architecture xavfsizlik chegarasi: judge host'da DB credential bo'lmaydi.
		log.Error("DATABASE_URL berilgan — judge host'da DB credential bo'lmasligi shart")
		os.Exit(1)
	}

	url := os.Getenv("REDIS_URL")
	if url == "" {
		url = "redis://localhost:6379/0"
	}
	opt, err := redis.ParseURL(url)
	if err != nil {
		log.Error("REDIS_URL noto'g'ri", "err", err)
		os.Exit(1)
	}
	rdb := redis.NewClient(opt)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Error("Redis ga ulanib bo'lmadi", "err", err)
		os.Exit(1)
	}
	// PREFLIGHT: cgroup limitlarini qo'ya olmasak, ishlamaymiz.
	// Cheklovsiz judge foydalanuvchi kodini host'ga qo'yib yuboradi —
	// bu 2026-09-06 da mashinani ikki marta yiqitgan.
	if err := PreflightCgroup(); err != nil {
		log.Error("cgroup preflight muvaffaqiyatsiz — worker ishga tushmaydi", "err", err)
		log.Error("konteyner --privileged --cgroupns=host bilan ishlashi va " +
			"/sys/fs/cgroup yozilishi mumkin bo'lishi kerak")
		os.Exit(1)
	}
	log.Info("cgroup preflight o'tdi — pids va memory limitlari ishlaydi")

	log.Info("judge-go ishga tushdi", "sandbox", "nsjail", "queue", jobsKey)

	for {
		// BRPOP — bloklab kutadi; SIGTERM kelganda navbatni bo'shatib chiqadi
		// (graceful drain, 10-operations deploy qoidasi).
		vals, err := rdb.BRPop(ctx, 2*time.Second, jobsKey).Result()
		if err != nil {
			if ctx.Err() != nil {
				log.Info("to'xtatilmoqda — navbat bo'shatildi")
				return
			}
			if err != redis.Nil {
				log.Warn("BRPOP xatosi", "err", err)
				time.Sleep(time.Second)
			}
			continue
		}

		received := time.Now()
		var job Job
		if err := json.Unmarshal([]byte(vals[1]), &job); err != nil {
			log.Error("job parse qilinmadi", "err", err)
			continue
		}

		res := judge(ctx, &job)
		res.Meta.QueueWaitMS = time.Since(received).Milliseconds() - res.Meta.TotalMS
		if res.Meta.QueueWaitMS < 0 {
			res.Meta.QueueWaitMS = 0
		}

		payload, err := json.Marshal(res)
		if err != nil {
			log.Error("natija serialize qilinmadi", "err", err)
			continue
		}
		if err := rdb.LPush(context.Background(), resultsKey, payload).Err(); err != nil {
			log.Error("natija yuborilmadi", "job", job.JobID, "err", err)
			continue
		}
		log.Info("bajarildi", "job", job.JobID, "verdict", res.Verdict,
			"cpu_ms", res.TimeMS, "mem_kb", res.MemoryKB, "total_ms", res.Meta.TotalMS)
	}
}
