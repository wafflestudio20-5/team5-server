"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="크림맛와플", # 타이틀
        default_version='v1', # 버전
        description="프로젝트 API 문서", # 설명
        terms_of_service="https://www.google.com/policies/terms/",
        url='http://127.0.0.1:8000/'
        # contact=openapi.Contact(email="이메일"),
        # license=openapi.License(name=""),
    ),
    validators=['flex'],
    public=True,
)

swagger_ulrpatterns = [
    re_path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('styles/', include('styles.urls')),
    path('shop/', include('shop.urls')),
] + swagger_ulrpatterns


