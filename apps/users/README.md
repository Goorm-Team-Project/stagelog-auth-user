# Users App

Django 기반 사용자 인증 및 프로필 관리 앱

## 개요

사용자 프로필 조회/수정과 내부 사용자 API를 제공하는 Django 앱입니다.

## 주요 기능

- 사용자 프로필 관리
- 레벨, 경험치, 신뢰도 점수 시스템
- 북마크 기능 연동
- 알림 구독 설정 (이메일, 이벤트, 게시글)

## 모델 구조

### User 모델
```python
- user_id: 기본키 (AutoField)
- email: 이메일 (고유값)
- nickname: 닉네임
- provider: OAuth 제공자 (kakao, google, naver 등)
- provider_id: OAuth 제공자의 사용자 ID
- created_at: 가입일시
- is_email_sub: 이메일 구독 여부
- is_events_notification_sub: 이벤트 알림 구독 여부
- is_posts_notification_sub: 게시글 알림 구독 여부
- is_admin: 관리자 권한
- exp: 경험치
- level: 레벨
- reliability_score: 신뢰도 점수 (기본값: 50)
- is_active: 활성 상태
```

## 환경 변수 설정

`.env` 파일에 다음 항목을 추가해야 합니다:

```env
SECRET_KEY=your_django_secret_key
```

## API 엔드포인트

### 사용자 정보

#### 내 정보 조회
```
GET /api/users/me
X-User-Id: {user_id}
```

**응답**
```json
{
  "success": true,
  "message": "정보 조회 성공",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "nickname": "사용자닉네임",
    "provider": "kakao",
    "provider_id": "123456789",
    "created_at": "2026-01-09T12:00:00Z",
    "is_email_sub": false,
    "is_events_notification_sub": false,
    "is_posts_notification_sub": false,
    "is_admin": false,
    "exp": 100,
    "level": 2,
    "reliability_score": 55,
    "bookmarks": [1, 2, 3]
  }
}
```

#### 다른 사용자 정보 조회
```
GET /api/users/{user_id}
X-User-Id: {user_id}
```

**응답**
```json
{
  "success": true,
  "message": "정보 조회 성공",
  "data": {
    "id": 2,
    "nickname": "다른사용자",
    "level": 5,
    "exp": 500
  }
}
```

#### 내 프로필 수정
```
PATCH /api/users/me/profile
X-User-Id: {user_id}
Content-Type: application/json

{
  "nickname": "새로운닉네임",
  "is_email_sub": true,
  "is_events_notification_sub": true,
  "is_posts_notification_sub": false
}
```

**응답**
```json
{
  "success": true,
  "message": "정보 수정 성공",
  "data": {
    "id": 1,
    "nickname": "새로운닉네임",
    "bookmarks": [1, 2, 3]
  }
}
```

## 테스트 가이드 (curl)

### 1. 개발 환경 실행
```bash
docker compose up
```

### 2. 프로필 조회
```bash
curl -X GET http://localhost:8000/api/users/me \
-H "X-User-Id: 1"
```

## 인증 방식

- **API Gateway 전달 헤더 사용**: 애플리케이션은 `X-User-Id` 헤더를 기준으로 인증 사용자 정보를 받습니다.
- **토큰 발행/검증 책임 분리**: JWT 발행과 검증은 `stagelog-auth` Lambda 서비스에서 담당합니다.

## 주요 유틸리티 함수

- `login_check`: 데코레이터 - API Gateway 사용자 헤더 검증
- `common_response(success, message, data, status)`: 통일된 API 응답 형식

## 보안 고려사항

### CSRF 보호
Django는 기본적으로 POST, PUT, PATCH, DELETE 요청에 CSRF 토큰 검증을 수행합니다. 하지만 REST API에서는 다음 이유로 `@csrf_exempt`를 사용합니다:

- **Gateway 기반 인증**: 애플리케이션은 직접 세션/쿠키 인증을 수행하지 않음
- **외부 클라이언트**: 모바일 앱, 프론트엔드 SPA 등 다양한 클라이언트가 접근

**적용 위치**: POST/PATCH 요청을 받는 모든 API 엔드포인트
```python
@csrf_exempt
@require_http_methods(["PATCH"])
def update_user_profile(request):
    ...
```

### 기타 보안
- 인증 사용자 식별은 API Gateway가 주입한 헤더를 사용
- 서비스 내부에서는 토큰을 직접 발행하거나 저장하지 않음

## 에러 응답 예시

```json
{
  "success": false,
  "message": "에러 메시지",
  "status": 400
}
```

## 참고 자료

- [카카오 로그인 REST API 문서](https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api)
- Django Authentication System
- JWT (JSON Web Token)
