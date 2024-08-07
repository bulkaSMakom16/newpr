# urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('post/<str:name>', views.post, name='post'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('category/<str:c>', views.category, name='category'),
    path('search/', views.search, name='search'),
    path('create/', views.create, name='create'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='blog/registration/login.html'), name='blog_login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='blog_logout'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add_product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/history/', views.order_history, name='order_history'),
    path('orders/pay/<int:order_id>/', views.pay_order, name='pay_order'),
    path('pay/<int:order_id>/', views.pay_order, name='pay_order'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)