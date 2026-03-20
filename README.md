# auth-service

## Responsibility
- Authentication and user/account domain ownership.
- Owns auth-related internal APIs for other services.

## Owned Domain
- Users profile/account domain
- Bookmarks domain (current migration decision)
- Auth/session token validation and account policy update endpoints

## API Scope
- Public: `/api/auth/*`
- Internal: `/internal/users:batch-get`, `/internal/users/{user_id}/exp`, bookmark internal endpoints as needed

## Data Ownership
- Primary schema: `stagelog_auth`
- Tables owned by auth domain must not be directly written by other services.

## Dependencies
- Inbound auth context from API Gateway Authorizer (`X-User-Id`)
- May call events internal API for event existence checks (temporary during migration)

## Runtime
- API Deployment in EKS
- Uses shared contracts package for internal DTO/event contract compatibility
