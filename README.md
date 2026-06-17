# SkillBridge

SkillBridge is a multilingual career assessment platform built with React,
Flutter, FastAPI, and OpenAI.

## Features

- Phone OTP authentication with JWT access and refresh tokens
- Uzbek, Russian, and English interfaces
- Interest selection and 25 assessment questions
- Top 3 personalized career recommendations
- Beginner, intermediate, and advanced roadmaps
- Books, courses, video sources, and official learning links
- Server-side assessment history, saved learning paths, and module progress
- Module lessons, practical projects, resources, and quizzes
- Context-aware AI tutor chat inside every module
- Local fallback recommendations when no OpenAI API key is configured

## Application Flow

```text
React web or Flutter mobile
    -> phone OTP login
    -> POST /api/v1/guide/analyze
    -> OpenAI career analysis or local fallback
    -> saved user history
    -> top 3 careers, roadmaps, and resources
```

## Local Development

Install backend dependencies and start FastAPI:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Install frontend dependencies and start Vite in another terminal:

```bash
npm install
npm run dev
```

Frontend: `http://localhost:5173`

Backend: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

Run the Flutter client from `mobile/`:

```bash
cd mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Android emulators use `http://10.0.2.2:8000/api/v1` by default. Physical
devices must use the development machine's LAN address or an HTTPS deployment.
See `mobile/README.md` for signing and release configuration.

## Environment

Create `.env` from `.env.example`:

```env
APP_NAME=SkillBridge
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./career_assessment.db
SECRET_KEY=replace-with-a-long-random-secret
SMS_PROVIDER=console
ESKIZ_EMAIL=
ESKIZ_PASSWORD=
ESKIZ_FROM=4546
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CORS_ORIGIN_REGEX=^https?://(localhost|127\.0\.0\.1)(:\d+)?$
```

When `OPENAI_API_KEY` is empty, the API returns deterministic local
recommendations so the application remains usable.

With `SMS_PROVIDER=console`, the OTP is printed in the backend terminal and is
not sent to the user. To enable real SMS delivery, set `SMS_PROVIDER=eskiz` and
provide the Eskiz credentials.

## API

### `POST /api/v1/auth/request-otp`

Creates a short-lived OTP challenge. The OTP is never returned by the API.

### `POST /api/v1/auth/verify-otp`

Verifies the OTP and returns JWT access and refresh tokens. Guide and history
endpoints require the access token as a Bearer token.

### `POST /api/v1/guide/analyze`

The request must contain:

- `language`: `uz`, `ru`, or `en`
- `interests`: 1 to 5 supported interest IDs
- `answers`: exactly 25 answers with a score from 1 to 5

The response contains a profile summary, strengths, development areas, and
exactly three career recommendations.

### `POST /api/v1/guide/learning-path`

Builds a detailed curriculum for the career selected from the top three.
The response contains at least six ordered modules. Every module includes
objectives, lessons, a portfolio project, direct resources, and quiz questions.

### `POST /api/v1/guide/chat`

Answers learner questions using the selected career and current module as
context. When no OpenAI key is configured, a local tutor fallback remains
available.

Assessment results, selected learning paths, progress, and tutor conversations
are stored in the database for the authenticated user. The frontend also keeps
a local cache for fast refreshes.

## Verification

```bash
npx tsc --noEmit
npm run build
./venv/bin/python -m pytest app/tests -q
cd mobile && flutter analyze && flutter test
```
# ai_career
