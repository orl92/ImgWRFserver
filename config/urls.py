"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
                                   SpectacularAPIView,
                                   SpectacularSwaggerView,
)

handler400 = 'core.views.my400_view'
handler403 = 'core.views.my400_view'
handler404 = 'core.views.my400_view'
handler500 = 'core.views.my400_view'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    path('api/simulations/', include('wrf_img.urls')),
    path('api/station_data/', include('station_data.urls')),
            ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
