"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path, include

from django.conf import settings 
from django.conf.urls.static import static 
from django.conf.urls import include

from product import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('', views.index),
    path('index/', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),

    path('category/index/', views.category_index, name='category_index'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:id>/', views.category_delete, name='category_delete'),
    path('category/read/<int:id>/', views.category_read, name='category_read'),

    path('catalog/index/', views.catalog_index, name='catalog_index'),
    path('catalog/list/', views.catalog_list, name='catalog_list'),
    path('catalog/create/', views.catalog_create, name='catalog_create'),
    path('catalog/edit/<int:id>/', views.catalog_edit, name='catalog_edit'),
    path('catalog/delete/<int:id>/', views.catalog_delete, name='catalog_delete'),
    path('catalog/read/<int:id>/', views.catalog_read, name='catalog_read'),
    path('catalog/details/<int:id>/', views.catalog_details, name='catalog_details'),    

    path('customer/index/', views.customer_index, name='customer_index'),
    #path('customer/create/', views.customer_create, name='customer_create'),
    #path('customer/edit/<int:id>/', views.customer_edit, name='customer_edit'),
    #path('customer/delete/<int:id>/', views.customer_delete, name='customer_delete'),
    path('customer/read/<int:id>/', views.customer_read, name='customer_read'),

    path('application/index/', views.application_index, name='application_index'),
    #path('application/create/', views.application_create, name='application_create'),
    #path('application/edit/<int:id>/', views.application_edit, name='application_edit'),
    path('application/delete/<int:id>/', views.application_delete, name='application_delete'),
    path('application/read/<int:id>/', views.application_read, name='application_read'),

    path('movement/index/<int:application_id>/', views.movement_index, name='movement_index'),
    #path('movement/create/<int:application_id>/', views.movement_create, name='movement_create'),
    path('movement/edit/<int:id>/<int:application_id>/', views.movement_edit, name='movement_edit'),
    #path('movement/delete/<int:id>/<int:application_id>/', views.movement_delete, name='movement_delete'),
    path('movement/read/<int:id>/<int:application_id>/', views.movement_read, name='movement_read'),

    path('report/report_1/', views.report_1, name='report_1'),
    path('report/report_2/', views.report_2, name='report_2'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logout/', views.logoutUser, name="logout"),
    path('settings/account/', views.UserUpdateView.as_view(), name='my_account'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

