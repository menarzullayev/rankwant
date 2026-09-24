package main

// PreflightNetwork — ADR-0028 ning kod qatlami: tarmoq chegarasi ishga
// tushishda TEKSHIRILADI, hujjat matni emas.
//
// Qoida (fail closed): judge POSTGRES_HOST va JUDGE_FORBIDDEN_HOSTS
// ro'yxatidagi manzarlarga TCP ulana olsa — CHEGARA BUZILGAN — worker
// ishga tushmaydi (exit 1). Ulanish xatosi (refused/timeout/unknown host)
// — muvaffaqiyat.
//
// Bu DATABASE_URL-ni-rad-etish (main.go) va PreflightCgroup (sandbox.go)
// bilan bir sulola: limitni/chegarani majburlay olmaydigan worker
// UMUMAN ishga tushmaydi.
//
// Gate: JUDGE_NET_PREFLIGHT=1 bo'lmasa preflight o'tkazib yuboriladi.
//compose'da judge-net (internal: true) bilan birga yoqiladi; lokal `go run`
// bilan ishga tushirilganda majburiy bo'lmasligi uchun.
//
// Nega har bir manzarga ALOHIDA ulanish: docker DNS bitta nomni
// resolve qilib, boshqasini qoldirishi mumkin emas — lekin SOZLAMA
// (tarmoq majmuasi) bir nechta manzarni bir vaqtda buzishi mumkin.
// Har biri alohida tekshiriladi, birortasi ochiq — yetarli.

import (
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"time"
)

// envPort — butun sonli env, noto'g'ri/bo'sh qiymatda standart.
func envPort(name string, def int) int {
	if v := os.Getenv(name); v != "" {
		if p, err := strconv.Atoi(v); err == nil && p > 0 && p <= 65535 {
			return p
		}
	}
	return def
}

// unreachable — bitta host:port ga ulanish xatosi kutilgan natijami?
//
//	err == nil      → ulanish MUVAFFAQIYATLI bo'ldi (yomon) → false
//	timeout/refused/unknown → chegara yopiq (yaxshi) → true
//
// boshqa xato → diagnoz noaniq; fail closed tamoyili bo'yicha «yaxshi»
// hisoblanmaydi — chaqiruvchi tomonidan muhim xato sifatida qaytariladi
// (err o'zi qaytadi).
func unreachable(host string, port int) (bool, error) {
	addr := net.JoinHostPort(host, strconv.Itoa(port))
	conn, err := net.DialTimeout("tcp", addr, 2*time.Second)
	if err == nil {
		_ = conn.Close()
		return false, nil
	}
	// Davom etish mumkin bo'lgan xatolar — chegara yopiq degan belgi.
	if oe, ok := err.(*net.OpError); ok {
		if oe.Timeout() {
			return true, nil
		}
		if se, ok := oe.Err.(*net.AddrError); ok && se.Err == "unknown host" {
			return true, nil
		}
		// DNS yechilmadi (compose tarmog'idagi nom yo'q) — bu ham «yopiq».
		if _, ok := oe.Err.(*net.DNSError); ok {
			return true, nil
		}
	}
	if strings.Contains(strings.ToLower(err.Error()), "connection refused") {
		return true, nil
	}
	return false, err
}

// PreflightNetwork — judge uchun TAQIQLANGAN manzarlarga ulanishni sinaydi.
// Bitta manzarga ham ulanish MUVAFFAQIYATLI bo'lsa — xato qaytaradi
// (chaqiruvchi main.go da os.Exit(1) qiladi).
func PreflightNetwork() error {
	// Standart: ADR-0028 bo'yicha taqiqlangan ikki manzarning portlari.
	// POSTGRES_HOST / POSTGRES_PORT / API_PORT compose'da o'rnatilmagan bo'lsa
	// — standartlar (`postgres`, 5432, 8000). Port env'lari testlarga ham
	// toza seam beradi (tasodifiy portlarda listener bilan).
	postgresHost := os.Getenv("POSTGRES_HOST")
	if postgresHost == "" {
		postgresHost = "postgres"
	}
	targets := map[string]int{
		postgresHost: envPort("POSTGRES_PORT", 5432), // DB — ADR-0004: judge → DB YO'Q
		"api":        envPort("API_PORT", 8000),      // API — ADR-0004: judge → API YO'Q
	}
	if extra := os.Getenv("JUDGE_FORBIDDEN_HOSTS"); extra != "" {
		for _, spec := range strings.Split(extra, ",") {
			spec = strings.TrimSpace(spec)
			if spec == "" {
				continue
			}
			host, portStr, found := strings.Cut(spec, ":")
			port := 0
			if found {
				p, err := strconv.Atoi(portStr)
				if err != nil || p <= 0 || p > 65535 {
					return fmt.Errorf("JUDGE_FORBIDDEN_HOSTS: noto'g'ri port: %q", spec)
				}
				port = p
			} else {
				return fmt.Errorf("JUDGE_FORBIDDEN_HOSTS: port bo'lmagan yozuv: %q (host:port kutilgan)", spec)
			}
			targets[host] = port
		}
	}

	for host, port := range targets {
		ok, err := unreachable(host, port)
		if err != nil {
			// Diagnoz noaniq (masalan, lokal qurilmada stack yo'q emas,
			// boshqa tarmoq muammosi) — «o'tdi» deb hisoblamaymiz.
			return fmt.Errorf("preflight: %s ulanish holati noaniq: %w", host, err)
		}
		if !ok {
			return fmt.Errorf(
				"preflight: %s:%d ga ulanish MUVAFFAQIYATLI — tarmoq chegarasi buzilgan "+
					"(judge %s tarmog'ida bo'lmasligi kerak; ADR-0028: judge-net, internal: true)",
				host, port, host)
		}
	}
	return nil
}
