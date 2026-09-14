# Admin panel i18n — browser verification

**Date:** 2026-09-14 · **Status:** verified

## Why this file exists

Every check in this repository is static: it reads source text. The admin
panel was made translatable by turning `label` into `labelKey` and wrapping
JSX text in `t()`, and none of that can be confirmed by reading files —
`curl` returns 200 for the SSR shell even when the client tree fails to
render.

That is not a theoretical concern here. Two of the defects found while doing
this work were invisible to every check and to `curl`:

- `t(DEFAULT_LOCALE, …)` in a client component. The server registers all ten
  dictionaries, the client receives only the active one, so the call throws
  for every other language — and `t()` throws in dev, which takes the whole
  React tree down. The page still answered 200.
- String ternaries only had their first branch checked. `: "yashirin"` sat
  unseen beside a flagged `? "ommaviy"`, so the status column stayed Uzbek
  in every language.

So the panel was opened in a real browser and the rendered DOM read back.

## How it was run

The running `next dev` has `NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1`
inlined, and nothing listens on 8000. The API is published on 8301, but
`DJANGO_ALLOWED_HOSTS` accepts `localhost` and not `127.0.0.1`, and
`CORS_ALLOWED_ORIGINS` is `https://rankwant.uz` — so a page served from
`http://localhost:3000` is refused.

A throwaway proxy on 8000 rewrote the `Host` header and answered the CORS
handshake. The dev server, the containers and the public site were left
untouched; the proxy was stopped afterwards.

Locale was switched by setting `rw_locale` — the cookie `getLocale()` reads.

## What was seen

### `en` — `/admin/problems`

| Element | Rendered |
| --- | --- |
| `<title>` | `Manage · Problems · RankWant` |
| `<h1>` | `Manage` |
| Table headers | `#`, `Slug`, `Title`, `Difficulty`, `Topics`, `Tests`, `Status`, `Actions` |
| Second table | `Slug`, `Name`, `Parent`, `Actions` |
| Status badges | `public`, `hidden` |
| Buttons | `Create`, `Edit`, `Delete` |
| Search | `Search…` |

### `ru` — `/admin/shop`

| Element | Rendered |
| --- | --- |
| `<title>` | `Управление · Магазин · RankWant` |
| Headings | `Управление`, `Магазин` |
| Table headers | `Код`, `Категория`, `Название`, `Цена`, `Повторяемый`, `Владельцы`, `Статус`, `Действия` |
| Buttons | `Создать`, `Изменить`, `Удалить`, `Выйти` |
| Search | `Поиск…` |
| Row data | `Заморозка серии`, `Рамка аватара`, `Обложка профиля`, `Квант` |

Admin navigation, all 19 sections, in `ru`:

`Задачи`, `Сообщения о дефектах`, `Соревнования`, `Банк вопросов`, `Тесты`,
`Арена`, `Турниры`, `Хакатоны`, `Дуэли`, `Статьи`, `Траектория`, `Новости`,
`Изменения`, `Дорожная карта`, `Комментарии к карте`, `Квесты`, `Магазин`,
`Пользователи`, `Аналитика`

Cyrillic is the useful part: it rules out the result being English by
accident of a fallback. Every string above comes from `admin.label.*`,
`admin.title.*` or `admin.section.*` resolved through `t(locale, …)`.

## Screenshots

Not attached. The browser tooling available in this environment refuses to
write outside its own workspace root, so the images could not be saved to
disk. The tables above are the same evidence in a form that can be diffed:
they are the rendered DOM, read back with `document.querySelectorAll`, not a
transcription of a picture.

## Reproducing

1. Start a proxy on 8000 forwarding to the API on 8301 with
   `Host: rankwant.uz`, answering CORS for `http://localhost:3000`.
2. Log in as a staff user at `http://localhost:3000/login`.
3. Set `rw_locale` to a non-Uzbek locale and open `/admin/problems` or
   `/admin/shop`.
4. Read `document.querySelectorAll('th')` and compare with
   `apps/web/src/i18n/locales/<lang>.ts`.
