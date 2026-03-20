from django.urls import path
from .views import (
    get_other_user_info,
    get_user_info,
    update_user_profile,
)


urlpatterns = [
    # 마이페이지
    path('me', get_user_info, name='get_user_info'),
    #다른 유저 정보 조회
    path('<int:user_id>', get_other_user_info, name='get_other_user_info'),
    #내 정보 수정
    path('me/profile', update_user_profile, name='update_user_profile'),
]
