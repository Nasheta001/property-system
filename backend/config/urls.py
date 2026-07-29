from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/", include("apps.organizations.urls")),
    path("api/v1/", include("apps.properties.urls")),
    path("api/v1/", include("apps.tenants.urls")),
    path("api/v1/", include("apps.leases.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.maintenance.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/v1/", include("apps.activity.urls")),
    path("api/v1/", include("apps.search.urls")),
    path("api/v1/", include("apps.reports.urls")),
    path("api/v1/", include("apps.support.urls")),
    path("api/v1/", include("apps.calendar_app.urls")),
    path("api/v1/", include("apps.subscriptions.urls")),
    path("api/v1/", include("apps.platform_admin.urls")),
    path("api/v1/", include("apps.ai_assistant.urls")),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
