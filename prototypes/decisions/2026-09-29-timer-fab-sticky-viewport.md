# DECISION: Vaqt chipi — pane-a scroll pastida doim ko‘rinadi

**Sana:** 2026-09-29  
**Kontekst:** `timer-stopwatch-gallery #6` — chip statement oxirida edi, yuqorida o‘qiyotganda yo‘qolardi.

## Qaror

Chip `pane-a` **boshiga** ko‘chirildi; `position: sticky; bottom: 12px` + `height: 0` overlay — scroll paytida o‘ng pastda qoladi.

## Trade-off

Kontent ustiga biroz qoplanadi (pointer-events faqat chipda).

## Ta’sir

- `prototypes/statement-builder.html` — HTML joylashuv, `.pane-a`, `.rw-time-fab-anchor` CSS.
