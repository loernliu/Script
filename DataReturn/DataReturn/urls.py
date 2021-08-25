"""DataReturn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path
from vi.views import return_data, save_vi_result, data_return1, data_return2, data_return3, data_return4, data_return5

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('vi_detect', return_data),
    path('vi_detect1', data_return1),
    path('vi_detect2', data_return2),
    path('vi_detect3', data_return3),
    path('vi_detect4', data_return4),
    path('vi_detect5', data_return5),
    path('save_vi_result', save_vi_result)
]
