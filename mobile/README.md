# SkillBridge Mobile

Flutter client for the SkillBridge FastAPI backend. The mobile app uses the
same OTP/JWT authentication, assessment, career recommendations, learning
paths, module quizzes, tutor chat, progress, and history APIs as the web app.

## API URL

Android emulator defaults to:

```text
http://10.0.2.2:8000/api/v1
```

For iOS simulator, a physical device, staging, or production, provide the API
URL at build time:

```bash
flutter run \
  --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1

flutter build apk --release \
  --dart-define=API_BASE_URL=https://api.example.com/api/v1
```

A physical phone cannot use the computer's `127.0.0.1`. Use the computer's LAN
IP address or an HTTPS deployment.

## Run

```bash
flutter pub get
flutter analyze
flutter test
flutter run
```

JWT access and refresh tokens are stored with `flutter_secure_storage`.
Expired access tokens are refreshed automatically. During local development,
the backend prints OTP codes to its terminal when `SMS_PROVIDER=console`.

## Release

Android application ID and namespace are `uz.skillbridge.mobile`. Before store
release, copy `android/key.properties.example` to `android/key.properties`,
configure a private signing key, and set the final iOS signing team.
Production builds should always use an HTTPS API URL.
