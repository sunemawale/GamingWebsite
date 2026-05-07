from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage showing products
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('myproduct/', views.myproduct, name='myproduct'),
    path('about/', views.about, name='about'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove'),
    path('increase/<int:id>/', views.increase_quantity, name='increase'),
    path('decrease/<int:id>/', views.decrease_quantity, name='decrease'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('khalti-verify/', views.khalti_verify, name='khalti_verify'),
   
   
]
