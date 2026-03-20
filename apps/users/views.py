import json
import traceback

from .models import User
from django.views.decorators.http import require_POST, require_safe, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction
from apps.common.utils import (
    common_response,
    login_check,
)
from bookmarks.models import Bookmark
from django.http import JsonResponse


@csrf_exempt
@require_POST
def internal_users_batch_get(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"message": "invalid json"}, status=400)

    raw_user_ids = payload.get("user_ids")
    if not isinstance(raw_user_ids, list):
        return JsonResponse({"message": "user_ids must be list"}, status=400)

    normalized_user_ids = []
    for raw in raw_user_ids:
        try:
            normalized_user_ids.append(int(raw))
        except (TypeError, ValueError):
            continue

    if not normalized_user_ids:
        return JsonResponse({"users": []}, status=200)

    rows = User.objects.filter(user_id__in=normalized_user_ids).values("user_id", "nickname")
    rows_by_user_id = {int(row["user_id"]): row for row in rows}

    users = []
    seen = set()
    for user_id in normalized_user_ids:
        if user_id in seen:
            continue
        seen.add(user_id)
        row = rows_by_user_id.get(user_id)
        if not row:
            continue
        users.append(
            {
                "user_id": int(row["user_id"]),
                "nickname": row.get("nickname"),
            }
        )

    return JsonResponse({"users": users}, status=200)


@csrf_exempt
@require_POST
def internal_apply_user_exp(request, user_id):
    from users.services import ExpPolicy, apply_user_exp

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"message": "invalid json"}, status=400)

    policy = str(payload.get("policy") or "").strip().upper()
    policy_map = {
        "POST": ExpPolicy.POST,
        "COMMENT": ExpPolicy.COMMENT,
    }
    exp_policy = policy_map.get(policy)
    if exp_policy is None:
        return JsonResponse({"message": "invalid policy"}, status=400)

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"message": "user not found"}, status=404)

    result = apply_user_exp(user, exp_policy)
    result["user_id"] = int(user_id)
    result["policy"] = policy
    return JsonResponse(result, status=200)

@require_safe
@login_check
def get_user_info(request):
    try:
        user_id = request.user_id
        user = User.objects.get(user_id=user_id)
        bookmarked_id = list(Bookmark.objects.filter(user_id=user.user_id).values_list('event_id', flat=True))

        return common_response(
            success=True,
            message="정보 조회 성공",
            data={
                "id": user.user_id,
                "email": user.email,
                "nickname": user.nickname,
                "provider": user.provider,
                "provider_id": user.provider_id,
                "created_at": user.created_at,
                "is_email_sub": user.is_email_sub,
                "is_events_notification_sub": user.is_events_notification_sub,
                "is_posts_notification_sub": user.is_posts_notification_sub,
                "is_admin": user.is_admin,
                "exp": user.exp,
                "level": user.level,
                "reliability_score": user.reliability_score,
                "bookmarks": bookmarked_id
            },
            status=200
        )
    except User.DoesNotExist:
        return common_response(success=False, message="존재하지 않는 회원입니다.", status=404)
    except Exception as e:
        print(f"에러 발생 : {e}")
        traceback.print_exc()
        return common_response(success=False, message="정보 조회 중 서버 오류 발생", status=500)

@require_safe
@login_check
def get_other_user_info(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)
        public_data = {
            "id": user.user_id,
            "nickname": user.nickname,
            "level": user.level,
            "exp": user.exp,
        }
        return common_response(
            success=True,
            message="정보 조회 성공",
            data=public_data,
            status=200
        )
    except User.DoesNotExist:
        return common_response(success=False, message="존재하지 않는 유저입니다.", status=404)
    except Exception as e:
        return common_response(success=False, message="서버 에러", status=500)

@csrf_exempt
@require_http_methods(["PATCH"])
@login_check
@transaction.atomic
def update_user_profile(request):
    try:
        user_id = request.user_id
        user = User.objects.get(user_id=user_id)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return common_response(success=False, message="잘못된 JSON 형식입니다.", status=400)

        if 'nickname' in body:
            new_nickname = body['nickname']
            if user.nickname != new_nickname:
                if User.objects.filter(nickname=new_nickname).exists():
                    return common_response(success=False, message="이미 존재하는 닉네임입니다.", status=409)
                user.nickname = new_nickname

        if 'is_email_sub' in body:
            user.is_email_sub = body['is_email_sub']
        if 'is_events_notification_sub' in body:
            user.is_events_notification_sub = body['is_events_notification_sub']
        if 'is_posts_notification_sub' in body:
            user.is_posts_notification_sub = body['is_posts_notification_sub']

        try:
            user.save()
        except IntegrityError:
            return common_response(False, message="이미 존재하는 닉네임입니다.", status=409)
        bookmarked_id = list(Bookmark.objects.filter(user_id=user.user_id).values_list('event_id', flat=True))

        return common_response(
            success=True,
            message="정보 수정 성공",
            data={
                "id": user.user_id,
                "email": user.email,
                "nickname": user.nickname,
                "provider": user.provider,
                "provider_id": user.provider_id,
                "created_at": user.created_at,
                "is_email_sub": user.is_email_sub,
                "is_events_notification_sub": user.is_events_notification_sub,
                "is_posts_notification_sub": user.is_posts_notification_sub,
                "is_admin": user.is_admin,
                "exp": user.exp,
                "level": user.level,
                "reliability_score": user.reliability_score,
                "bookmarks": bookmarked_id
            },
            status=200
        )
    except User.DoesNotExist:
        return common_response(success=False, message="존재하지 않는 회원입니다.", status=404)
    except Exception as e:
        return common_response(success=False, message="서버 에러", status=500)
