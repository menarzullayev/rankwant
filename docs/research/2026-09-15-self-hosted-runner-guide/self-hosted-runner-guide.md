# GitHub Actions self-hosted runner — Ubuntu va Windows uchun to'liq qo'llanma

Tayyorlangan: 2026-09-15 · Runner versiyasi: **v2.337.0** (2026-08-26) ·
Manba: GitHub rasmiy hujjati + `actions/runner` repozitoriyasi.

---

## 1. Qisqa javob

**Ha, Ubuntu'da self-hosted runner o'rnatish mumkin** — u hatto eng keng tarqalgan
variant. Ubuntu 20.04+ rasmiy qo'llab-quvvatlanadi.

Windows'da ikki yo'l bor:

| Yo'l | Qanday ishlaydi | Qachon tanlash |
|---|---|---|
| **A. Native Windows service** | `C:\actions-runner` ichida `config.cmd --runasservice`, Windows xizmati sifatida | Windows-only build (MSBuild, .NET, Windows container) kerak bo'lsa |
| **B. WSL Ubuntu ichida** | Linux'dagidek, lekin WSL distro ichida (`svc.sh` + systemd) | Linux build muhiti kerak bo'lsa — RankWant hozir shunday |

> ⚠️ B yo'lida bitta tuzoq: WSL distro to'xtasa, runner `offline` bo'ladi va
> GitHub'dagi run'lar `queued` → `cancelled` bo'lib ketadi.

Ikkala holatda ham **inbound port ochish shart emas** — runner o'zi GitHub'ga
chiqadi (outbound HTTPS/443), xuddi pochta kabineti kabi: konvertni tashlab
ketasiz, javobni o'zingiz borib olasiz.

---

## 2. Tizim talablari

### Operatsion tizim (rasmiy)

| OS | Qo'llab-quvvatlanadigan versiya |
|---|---|
| Ubuntu | **20.04+** |
| Debian | 10+ |
| RHEL / CentOS / Oracle Linux | 8+ |
| Fedora | 29+ |
| openSUSE | 15.2+ · SLES 15 SP2+ |
| Windows | **10 / 11 (64-bit)**, Server **2016 / 2019 / 2022** |
| macOS | 11.0 (Big Sur)+ |

### Arxitektura

| Arxitektura | Linux | macOS | Windows |
|---|---|---|---|
| `x64` | ✅ | ✅ | ✅ |
| `arm64` | ✅ | ✅ | ⚠️ public preview |
| `arm` (32-bit) | ✅ | — | — |

### Uskuna

GitHub **rasmiy minimum (CPU/RAM/disk) e'lon qilmaydi** — "workflow'ingiz uchun
yetarli bo'lsin" deydi, runner'ning o'zi kam yeydi. Amaliy tavsiya:

| Resurs | Oddiy CI (lint/test) | Og'ir CI (Docker build, e2e) |
|---|---|---|
| vCPU | 2 | 4+ |
| RAM | 4 GB | 8–16 GB |
| Disk | 10 GB bo'sh | 30 GB+ (image'lar shishiradi) |
| Tarmoq | 70 kbps (rasmiy minimum) | 10+ Mbps |

Hajm haqiqati: `actions-runner-linux-x64-2.337.0.tar.gz` — **226 MB**,
ochilganda ~400 MB. Keyin `_work/` (har job'ning checkout'i) va
`_work/_temp` (artifact/cache) o'sib boradi — **doimiy tozalash kerak**.

### Tarmoq (faqat outbound 443)

Ruxsat berilishi kerak bo'lgan domenlar:

```
github.com, api.github.com, *.actions.githubusercontent.com   # asosiy ish
codeload.github.com                                          # action'larni yuklash
results-receiver.actions.githubusercontent.com               # log, artifact, cache
*.blob.core.windows.net
objects.githubusercontent.com, objects-origin.githubusercontent.com
github-releases.githubusercontent.com                         # runner yangilanishi
github-registry-files.githubusercontent.com
*.pkg.github.com, pkg-containers.githubusercontent.com, ghcr.io
github-cloud.githubusercontent.com, github-cloud.s3.amazonaws.com   # Git LFS
dependabot-actions.githubapp.com
release-assets.githubusercontent.com
```

Agar tashkilotda **IP allowlist** yoqilgan bo'lsa, runner'ning o'z IP manzilini
ham ro'yxatga qo'shish kerak.

### Dasturiy bog'liqliklar (Linux)

`.NET` o'rnatish shart emas — runner **self-contained**. Lekin kutubxonalar kerak:
`libicu`, `libssl`, `libkrb5`, `zlib`, `liblttng-ust`. Yetishmasa:

```bash
sudo ./bin/installdependencies.sh
```

Windows'da esa faqat **PowerShell** (5.1+ yetarli) va administrator huquqi
(service sifatida o'rnatish uchun).

---

## 3. 0-qadam: registratsiya tokenini olish

Ikki usul:

**UI orqali:** `Settings → Actions → Runners → New self-hosted runner` —
bu yerda OS va arxitekturani tanlasangiz, GitHub tayyor buyruqlarni ko'rsatadi.

**REST API orqali** (avtomatlashtirish uchun):

```bash
# repo uchun
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <PAT>" \
  https://api.github.com/repos/<OWNER>/<REPO>/actions/runners/registration-token

# tashkilot uchun
curl -X POST ... https://api.github.com/orgs/<ORG>/actions/runners/registration-token
```

- Token **1 soat** yashaydi — eskirsa yangisini oling.
- PAT: klassik `repo` (yoki org uchun `admin:org`) scope; fine-grained bo'lsa
  "Administration: read/write".

---

## 4. Ubuntu — bosqichma-bosqich

### 4.1. Alohida foydalanuvchi (root emas!)

```bash
sudo useradd -m -s /bin/bash runner
sudo usermod -aG docker runner        # Docker kerak bo'lsa
sudo -iu runner
```

### 4.2. Yuklash va ochish

```bash
mkdir -p ~/actions-runner && cd ~/actions-runner

curl -o actions-runner-linux-x64-2.337.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-linux-x64-2.337.0.tar.gz

# ixtiyoriy: xeshni GitHub ko'rsatgan qiymat bilan solishtiring
shasum -a 256 actions-runner-linux-x64-2.337.0.tar.gz

tar xzf ./actions-runner-linux-x64-2.337.0.tar.gz
```

> ⚠️ `must not run with sudo` xatosi chiqsa — `RUNNER_ALLOW_RUNASROOT=1` kerak.
> Lekin to'g'ri yechim: alohida foydalanuvchi.

### 4.3. Konfiguratsiya

```bash
./config.sh \
  --url https://github.com/<OWNER>/<REPO> \
  --token <REG_TOKEN> \
  --name ubuntu-runner-01 \
  --labels self-hosted,linux,x64,rankwant \
  --work _work \
  --unattended
```

Interaktiv rejim (`./config.sh` argsiz) ham ishlaydi: guruh → nom → work papkasi
so'raydi. `--unattended` hammasini javobsiz qiladi.

### 4.4. Ishga tushirish

```bash
./run.sh          # terminalda (sinov uchun)
```

Muvaffaqiyat belgisi:

```
√ Connected to GitHub

2026-09-15 12:00:00Z: Listening for Jobs
```

### 4.5. systemd service sifatida

```bash
sudo ./svc.sh install          # yoki: sudo ./svc.sh install runner
sudo ./svc.sh start
sudo ./svc.sh status
sudo ./svc.sh stop
sudo ./svc.sh uninstall        # olib tashlash
```

Unit nomi: `actions.runner.<owner>-<repo>.<name>.service`.

> ⚠️ **Ubuntu tuzog'i — `needrestart`:** unattended-upgrades ishga tushganda
> `needrestart` runner servisini **job o'rtasida** qayta ishga tushirishi mumkin.
> Oldini olish:
>
> ```bash
> echo '$nrconf{override_rc}{qr(^actions\.runner\..+\.service$)} = 0;' \
>   | sudo tee /etc/needrestart/conf.d/actions_runner_services.conf
> ```

### 4.6. O'chirish

```bash
sudo ./svc.sh stop && sudo ./svc.sh uninstall
./config.sh remove --token <YANGI_TOKEN>
```

---

## 5. Windows — bosqichma-bosqich (native service)

### 5.1. PowerShell — **Administrator** sifatida

> ⚠️ Administrator bo'lmasa `--runasservice` ishlamaydi.

```powershell
mkdir C:\actions-runner ; cd C:\actions-runner
```

> Papka aynan `C:\actions-runner` bo'lishi tavsiya etiladi — Windows tizim
> akkauntlari (`NETWORK SERVICE`) shu yerga yetib oladi.

### 5.2. Yuklash va ochish

```powershell
Invoke-WebRequest -Uri `
  https://github.com/actions/runner/releases/download/v2.337.0/actions-runner-win-x64-2.337.0.zip `
  -OutFile actions-runner-win-x64-2.337.0.zip

# ixtiyoriy: xesh tekshiruvi
(Get-FileHash actions-runner-win-x64-2.337.0.zip -Algorithm SHA256).Hash.ToUpper()

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory(
  "$PWD\actions-runner-win-x64-2.337.0.zip", "$PWD")
```

### 5.3. Konfiguratsiya + service

```powershell
.\config.cmd `
  --url https://github.com/<OWNER>/<REPO> `
  --token <REG_TOKEN> `
  --name windows-runner-01 `
  --labels self-hosted,windows,x64 `
  --work _work `
  --runasservice `
  --windowslogonaccount "NT AUTHORITY\NETWORK SERVICE" `
  --unattended
```

- `--runasservice` → Windows xizmati yaratiladi; sukut bo'yicha hisob —
  `NT AUTHORITY\NETWORK SERVICE`. Domain akkaunt kerak bo'lsa
  `--windowslogonaccount "DOMAIN\user" --windowslogonpassword "***"` qo'shing.
- Xizmat nomi `actions.runner.<owner>-<repo>.<name>`, ko'rinadigan nom
  "GitHub Actions Runner (<name>)".

### 5.4. Xizmatni boshqarish

```powershell
Get-Service | Where-Object { $_.DisplayName -like 'GitHub Actions Runner*' }

Restart-Service "actions.runner.<owner>-<repo>.<name>"
Stop-Service    "actions.runner.<owner>-<repo>.<name>"
Start-Service   "actions.runner.<owner>-<repo>.<name>"
```

Muhit o'zgaruvchilarini qo'shganingizdan keyin **xizmatni qayta ishga
tushirish shart** — aks holda ular ko'rinmaydi.

### 5.5. O'chirish

```powershell
.\config.cmd remove --token <YANGI_TOKEN>
```

---

## 6. WSL (Ubuntu) varianti — RankWant holati

WSL ichida hammasi 4-bo'limdagidek, faqat ikkita farq:

1. **systemd** yoqilgan bo'lishi kerak (`/etc/wsl.conf`: `[boot] systemd=true`),
   aks holda `svc.sh install` ishlamaydi.
2. **WSL to'xtasa — runner o'ladi.** Windows ishga tushganda avto-start
   (Scheduled Task: `wsl -d Ubuntu-24.04 --exec systemctl start ...`) yoki
   native Windows runner'ga o'tish kerak.

Hozirgi holat: `/opt/actions-runner`, unit
`actions.runner.menarzullayev-rankwant.nsn-pc-rankwant`.
⚠️ 2026-09-14 da foydalanuvchi qarori bilan **CI ishlari to'xtatilgan** —
yangi o'rnatish boshlanmaydi.

---

## 7. `config` parametrlari (to'liq, manbadan tekshirilgan)

| Parametr | Turi | Ma'nosi |
|---|---|---|
| `--url` | arg | `https://github.com/<owner>/<repo>` yoki org/enterprise |
| `--token` | arg (secret) | Registratsiya tokeni (1 soat) |
| `--name` | arg | Runner nomi (unique bo'lsin) |
| `--labels` | arg | Vergul bilan: `self-hosted,linux,x64,gpu` |
| `--runnergroup` | arg | Runner guruh nomi (default: `Default`) |
| `--work` | arg | Ish papkasi (default: `_work`) |
| `--unattended` | flag | Savol bermasdan sozlash |
| `--replace` | flag | Shu nomdagi mavjud runner'ni almashtirish |
| `--ephemeral` | flag | **Bitta job** bajarib, o'zini ro'yxatdan chiqaradi |
| `--disableupdate` | flag | Avto-yangilanishni o'chirish |
| `--local` | flag | Runner'ni `config` fayliga yozmasdan ishga tushirish |
| `--no-default-labels` | flag | `self-hosted`, OS, arxitektura yorliqlarini qo'shmaslik |
| `--runasservice` | flag | **Faqat Windows** — xizmat sifatida |
| `--windowslogonaccount` / `--windowslogonpassword` | arg (secret) | Xizmat hisobi |
| `--jitconfig` | arg (secret) | JIT config (ephemeral, avtomatlashtirish) |
| `--pat` / `--auth` | arg (secret) | Muqobil autentifikatsiya |

Muhit o'zgaruvchilari (runner papkasidagi `.env` fayli yoki tizim env):

```
RUNNER_ALLOW_RUNASROOT=1     # sudo bilan ishga tushirish uchun
RUNNER_TEMP=/tmp/runner      # vaqtinchalik fayllar
RUNNER_TOOL_CACHE=/opt/tools # setup-* action'larining cache'i
https_proxy=http://proxy:3128
no_proxy=localhost,127.0.0.1
```

`.env` o'zgargandan keyin: Linux'da `sudo ./svc.sh stop && sudo ./svc.sh start`,
Windows'da `Restart-Service`.

---

## 8. Ephemeral / JIT runner (tavsiya etilgan, xavfsizroq)

```bash
# 1. JIT config olish
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <PAT>" \
  https://api.github.com/repos/<OWNER>/<REPO>/actions/runners/generate-jitconfig \
  -d '{"name":"jit-001","runner_group_id":1,"labels":["self-hosted","linux","x64"]}'

# 2. To'g'ridan-to'g'ri ishga tushirish (config.sh KERAK EMAS)
./run.sh --jitconfig "$ENCODED_JIT_CONFIG"
```

Bunday runner **ko'pi bilan bitta job** bajaradi va o'zi o'chib ketadi —
avtomatlashtirish (Kubernetes, ARC) uchun asos.

---

## 9. Yangilanish siyosati

- Sukut bo'yicha runner **o'zini avto-yangilaydi** — job tayinlanganda yoki
  yangi release'dan keyin **1 hafta** ichida.
- `--disableupdate` bilan o'chirilsa, yangi versiya chiqqandan keyin **30 kun**
  ichida qo'lda yangilash kerak — aks holda GitHub bu runner'ga job yubormaydi
  (xavfsizlik yangilanishlarida — darhol to'xtatadi).

---

## 10. Cheklovlar

| Narsa | Qiymat |
|---|---|
| Job'ni olish | 60 s ichida olmasa → boshqa runner'ga qayta navbat |
| Navbatda turish | > 24 soat → job `failed` |
| Ephemeral | 1 job, keyin avto-o'chirish |
| Token yashash vaqti | 1 soat |
| Yangilash muddati (`--disableupdate`) | 30 kun |

---

## 11. Xavfsizlik — ⚠️ muhim

GitHub'ning rasmiy ogohlantirishi: *"self-hosted runner'lar toza va vaqtinchalik
VM kafolatiga ega emas, ishonchsiz kod ularni doimiy buzishi mumkin."*

- ❌ **Public repo uchun deyarli hech qachon** ishlatmang — istalgan odam PR ochib
  mashinangizda kod ishga tushirishi mumkin.
- ⚠️ **Private repo ham xavfsiz emas** — read huquqi bor odam fork + PR orqali
  secret va `GITHUB_TOKEN` ga yetib oladi.
- ✅ **Ephemeral/JIT runner** ishlating.
- ✅ **Runner guruhlari** bilan izolyatsiya qiling.
- ✅ `GITHUB_TOKEN` — default `contents: read`, kerakli job'da oshiring.
- ✅ Bulut uchun **OIDC** (qisqa muddatli token), uzoq yashovchi secret emas.
- ✅ Mashinada ortiqcha SSH kalit / API token saqlamang;
  169.254.169.254 (metadata service) ga kirishni cheklang.
- ⚠️ "Har job'dan keyin o'chiraman" usuli ishonchsiz — bir runner ketma-ket
  bir necha job olishi va `ps x -w` orqali boshqasining secret'ini ko'rishi mumkin.

---

## 12. Workflow'da ishlatish

```yaml
jobs:
  test:
    runs-on: [self-hosted, linux, x64]     # yoki windows / arm64
    steps:
      - uses: actions/checkout@v4
      - run: docker compose -p rankwant build
```

Linux'da `docker` talab qiladigan action'lar ishlaydi; **Windows'da Linux
konteyner ishlatib bo'lmaydi** (faqat Windows container).

---

## 13. Tez-tez uchraydigan xatolar

| Xato / alomat | Sabab | Yechim |
|---|---|---|
| `must not run with sudo` | root bilan ishga tushirish | `RUNNER_ALLOW_RUNASROOT=1` yoki alohida user |
| `libunwind.so.8 => not found` | .NET bog'liqliklari yetishmayapti | `sudo ./bin/installdependencies.sh` |
| `A runner exists with the same name` | Nomi band | `--replace` yoki boshqa nom |
| Token ishlamayapti | 1 soat o'tgan | Yangi token oling |
| `Listening for Jobs` chiqmayapti | Proxy / firewall | `.env` ga `https_proxy`, 443 chiqishini tekshiring |
| Job `queued` da qotib qoldi | Yorliq mos kelmadi yoki runner offline | `runs-on` yorliqlarini va runner holatini tekshiring |
| WSL'da runner o'lik | Distro to'xtagan | WSL auto-start yoki native Windows runner |
| `svc.sh: command not found` | WSL'da systemd o'chiq | `/etc/wsl.conf` → `[boot] systemd=true` |

---

## 14. Tezkor ro'yxat

- [ ] Alohida foydalanuvchi / `C:\actions-runner`
- [ ] Runner yuklandi, xesh tekshirildi
- [ ] Bog'liqliklar (`installdependencies.sh`)
- [ ] Token olindi (1 soat ichida ishlatildi)
- [ ] `config.sh` / `config.cmd` + `--labels`
- [ ] `Listening for Jobs` ko'rindi
- [ ] Service: `svc.sh install` yoki `--runasservice`
- [ ] `needrestart` tuzog'i yopildi (Ubuntu)
- [ ] `.env` (proxy) — va service restart
- [ ] `runs-on: [self-hosted, ...]` workflow'da yozildi
- [ ] Disk tozalash (`_work/_temp`) avtomatlashtirildi
