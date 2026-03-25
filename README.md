# Auth Service

`auth`는 사용자, 인증, 북마크 도메인을 담당하는 Django 서비스입니다.

## Responsibility
- 사용자 계정/프로필 관리
- 로그인 사용자 기준 북마크 조회 및 변경
- 다른 서비스가 참조하는 사용자/북마크 내부 API 제공
- 알림용 outbox 이벤트 발행

## Main Routes
- Public
  - `/api/users/*`
  - `/api/bookmarks/*`
- Internal
  - `/internal/users:*`
  - `/internal/bookmarks/events:favorite-count`

## Runtime
- Python 3.12 / Django / Gunicorn
- 컨테이너 포트: `8000`
- Kubernetes에서는 `.env` 파일 마운트 대신 Secret key를 환경변수로 직접 주입합니다

## Deploy
- Kubernetes 매니페스트
  - [`auth/deploy/k8s/auth-env-externalsecret.yaml`](/home/woosupar/stagelog/auth/deploy/k8s/auth-env-externalsecret.yaml)
  - [`auth/deploy/k8s/auth-deployment.yaml`](/home/woosupar/stagelog/auth/deploy/k8s/auth-deployment.yaml)
- CI/CD workflow
  - [`auth/.github/workflows/build-and-push.yml`](/home/woosupar/stagelog/auth/.github/workflows/build-and-push.yml)

배포 흐름은 아래와 같습니다.
- GitHub Actions가 이미지를 빌드해 ECR에 push
- 같은 workflow가 `stagelog-gitops`의 이미지 태그를 갱신
- ArgoCD가 변경된 태그를 감지해 클러스터에 반영

## Configuration
주요 환경변수 예시는 [`auth/.env.example`](/home/woosupar/stagelog/auth/.env.example) 에 있습니다.

운영 환경에서는 값의 소스 오브 트루스를 SSM Parameter Store에 두고, ExternalSecret이 필요한 키만 Kubernetes Secret으로 동기화합니다.

## Notes
- API Gateway authorizer가 붙는 보호 경로에서는 `X-User-Id` 헤더를 통해 사용자 문맥을 받습니다.
- `auth`는 `events` 존재 여부 확인 등 일부 내부 호출을 수행합니다.
- 북마크 수 집계 API는 다른 서비스가 메인 화면 카드 정보를 구성할 때 사용합니다.
