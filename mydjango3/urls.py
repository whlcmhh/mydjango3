"""mydjango2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path,re_path
from schedule import views
# from django.conf.urls import include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/',views.products_list),#返回所有的产品线及对应值班模式，添加产品线
    path('api/products/<int:pk>/',views.products_detail),
    path('api/dutygroups/',views.dutygroups_list),
    path('api/dutygroups/<int:pk>/',views.dutygroups_detail),
    path('api/dutypersons/',views.dutypersons_list),
    path('api/dutypersons/<int:pk>/',views.dutypersons_detail),
    path('api/dutylist/<int:pk>/',views.dutylist),
    path('api/dutyex/',views.dutyexchange),
    path('api/dutytmp/',views.dutytmp_post),
    path('api/dutytmp/<int:pk>/',views.dutytmp_delete),
    path('api/persondetail/',views.persondetail_post),
    path('api/persondetail/<int:pk>/',views.persondetail_delete),

]
