# Тестовый стенд открытого Canvas

Ответственный: Узаков И. Это **не копия Canvas Narxoz**. Стенд нужен, чтобы проверить LTI 1.3 на вымышленных пользователях.

## 1. Развернуть Canvas

Используйте официальную инструкцию open-source Canvas LMS (Docker): https://github.com/instructure/canvas-lms/wiki

Записывайте в журнал трудоёмкости: дату, часы, проблему, решение. Это пойдёт в отчёт для руководителя.

## 2. Создать тестовые данные

- 1 преподаватель, 5–10 студентов (вымышленные имена и почты)
- курс «Технологическое предпринимательство»
- задание «Питч стартапа»

## 3. Зарегистрировать LTI 1.3 ключ

В Canvas: **Admin → Developer Keys → + Developer Key → + LTI Key**.

| Поле | Значение |
|---|---|
| Redirect URIs | `http://localhost:8000/lti/launch/` |
| Target Link URI | `http://localhost:8000/lti/launch/` |
| OpenID Connect Initiation URL | `http://localhost:8000/lti/login/` |
| JWK Method | Public JWK URL → `http://localhost:8000/lti/jwks/` |

Включите ключ (ON) и установите приложение в курс: **Settings → Apps → + App → By Client ID**.

## 4. Добавить платформу в наше приложение

В `/admin/` → **Lti platforms** → добавить:

| Поле | Пример для локального Canvas |
|---|---|
| Issuer | `https://canvas.instructure.com` (проверьте в настройках вашего стенда) |
| Client ID | ID ключа из Developer Keys |
| Deployment ID | из настроек установленного приложения |
| Auth login URL | `http://localhost:3000/api/lti/authorize_redirect` |
| Auth token URL | `http://localhost:3000/login/oauth2/token` |
| JWKS URL | `http://localhost:3000/api/lti/security/jwks` |

## 5. Проверить

- Запуск от имени студента → открывается страница студента
- Запуск от имени преподавателя → открывается страница преподавателя
- В `/admin/` → Audit logs появилась запись `lti.launch`

Для работы в iframe Canvas по HTTPS установите в `.env`: `COOKIE_SAMESITE=None` и `COOKIE_SECURE=1`.
