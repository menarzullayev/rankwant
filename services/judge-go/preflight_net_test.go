package main

// PreflightNetwork testlari — ADR-0028 fail-closed kontrakti.
//
// Testlar HAQIQIY socketlar bilan ishlaydi (mock yo'q): ochiq listener
// «ulanish muvaffaqiyatli» = chegara buzilgan; yopiq port = refused;
// mavjud bo'lmagan DNS nomi = yechilmagan. Uchala holat real Docker
// tarmoqlarida kuzatiladigan xatolar sifatida qamrab olingan.

import (
	"net"
	"os"
	"strconv"
	"strings"
	"testing"
)

// freePort — OS'dan erkin port olib, darhol qaytaradi (listener YO'Q —
// ulanish refused bo'lishi kutiladi).
func freePort(t *testing.T) int {
	t.Helper()
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("erkin port olinmadi: %v", err)
	}
	closed := l.Addr().(*net.TCPAddr).Port
	_ = l.Close()
	return closed
}

// startListener — ochiq (qabul qiluvchi) port; ulanish MUVAFFAQIYATLI
// bo'lishi kerak bo'lgan case'lar uchun.
func startListener(t *testing.T) (host string, port int) {
	t.Helper()
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listener ochilmadi: %v", err)
	}
	t.Cleanup(func() { _ = l.Close() })
	go func() {
		for {
			c, err := l.Accept()
			if err != nil {
				return
			}
			_ = c.Close()
		}
	}()
	return l.Addr().(*net.TCPAddr).IP.String(), l.Addr().(*net.TCPAddr).Port
}

func setPreflightEnv(t *testing.T, postgresHost string, postgresPort int, forbidden string) {
	t.Helper()
	t.Setenv("POSTGRES_HOST", postgresHost)
	t.Setenv("POSTGRES_PORT", strconv.Itoa(postgresPort))
	t.Setenv("JUDGE_FORBIDDEN_HOSTS", forbidden)
}

func TestPreflightNetworkFailsClosed(t *testing.T) {
	closedPort := freePort(t)
	lh, lp := startListener(t)

	cases := []struct {
		name         string
		postgresHost string
		postgresPort int
		wantErr      bool
	}{
		{name: "listener ochiq — chegara buzilgan, xato", postgresHost: lh, postgresPort: lp, wantErr: true},
		{name: "refused — chegara yopiq, o'tadi", postgresHost: "127.0.0.1", postgresPort: closedPort, wantErr: false},
		{name: "DNS yechilmadi — chegara yopiq, o'tadi", postgresHost: "preflight-net-test.invalid", postgresPort: 5432, wantErr: false},
	}

	for _, tc := range cases {
		tc := tc
		t.Run(tc.name, func(t *testing.T) {
			// api targeti har case'da kafolatlangan «yopiq» holatda.
			// ⚠️ IKKITA tuzoq: (1) «api» NOMI ishlatilmaydi — testlar hostda
			// yuradi, nom DNS'da yo'q, yechilmagan nom «yopiq» bo'lardi;
			// (2) 127.0.0.2 ishlatiladi, 127.0.0.1 EMAS — targets MAPIDA
			// kalitlar host bo'ylab: forbidden 127.0.0.1 bo'lsa ochiq
			// listener maqsadini (127.0.0.1:lp) USTIDAN YOZIB TASHLAB,
			// test yolg'on yiqilardi (o'lchandi 2026-09-24).
			setPreflightEnv(t, tc.postgresHost, tc.postgresPort, "127.0.0.2:"+strconv.Itoa(closedPort))
			err := PreflightNetwork()
			if tc.wantErr && err == nil {
				t.Fatalf("xato kutilgandi, yo'q (target %s)", tc.postgresHost)
			}
			if !tc.wantErr && err != nil {
				t.Fatalf("o'tishi kutilgandi, xato: %v", err)
			}
			if err != nil {
				// Xato MATNI chegara buzilganini aytishi shart — operator
				// qayerda qidirishni bilishi uchun.
				if !strings.Contains(err.Error(), "ulanish MUVAFFAQIYATLI") {
					t.Fatalf("xato matnida «ulanish MUVAFFAQIYATLI» yo'q: %v", err)
				}
			}
		})
	}
}

func TestPreflightNetworkForbiddenHosts(t *testing.T) {
	lh, lp := startListener(t)
	_ = lp

	t.Run("taqiqlangan ro'yxatdagi ochiq manzil — xato", func(t *testing.T) {
		// postgres 127.0.0.2 da yopiq, ochiq listener 127.0.0.1 da — kalitlar
		// TO'QNASHUVSIZ (map ustma-ust yozish tuzaog'iga qarang yuqorida).
		setPreflightEnv(t, "127.0.0.2", closedPort2(t), lh+":"+strconv.Itoa(lp))
		if err := PreflightNetwork(); err == nil {
			t.Fatal("taqiqlangan ochiq manzil ushlanmadi")
		}
	})

	t.Run("buzuq yozuv — xato (fail closed)", func(t *testing.T) {
		setPreflightEnv(t, "127.0.0.1", closedPort2(t), "api-port-isiz")
		if err := PreflightNetwork(); err == nil {
			t.Fatal("port bo'lmagan yozuv jimgina o'tdi")
		}
	})

	t.Run("noto'g'ri port — xato (fail closed)", func(t *testing.T) {
		setPreflightEnv(t, "127.0.0.1", closedPort2(t), "api:99999")
		if err := PreflightNetwork(); err == nil {
			t.Fatal("oraliqdan tashqari port jimgina o'tdi")
		}
	})
}

// closedPort2 — ikkinchi «yopiq» port (freePort taxallusi, o'qilishi uchun).
func closedPort2(t *testing.T) int { return freePort(t) }

// Test asosiy faylga uzatilgan gate xatti-harakatini hujjatlashtiradi:
// JUDGE_NET_PREFLIGHT=1 bo'lmasa main PreflightNetwork ni CHAQIRMAYDI.
// Bu yerning o'zida test qilinmaydi — main.go ni yuritish kerak; guard
// static wiring sifatida qo'riqlanadi (compose'da env=1 bilan ishlaydi,
// lokal `go run` da yo'q).
var _ = os.Getenv
