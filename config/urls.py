from django.contrib import admin
from django.urls import include, path

from users import views as users_views
from bookmarks import views as bookmarks_views
from common.utils import health_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # public
    path('api/users/', include('users.urls')),
    path('api/bookmarks/', include('bookmarks.urls')),

    # internal
    path('internal/users:batch-get', users_views.internal_users_batch_get, name='internal_users_batch_get'),
    path('internal/users/<int:user_id>/exp', users_views.internal_apply_user_exp, name='internal_apply_user_exp'),
    path(
        'internal/bookmarks/events:favorite-count',
        bookmarks_views.internal_bookmark_favorite_count,
        name='internal_bookmark_favorite_count',
    ),

    path('', health_check),
]
