from django.urls import path
from .views import CustomPasswordResetView
from django.contrib.auth import views as auth_views
# from profile_app.tasks import send_daily_highlighted_book_notification
from . import views
from .views import subscribe_to_notifications

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('books/', views.book_list, name='book_list'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('view-cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-history/', views.order_history, name='order_history'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('send-otp/', views.send_otp_email, name='send_otp'),
    path('otp-verification/', views.verify_otp, name='verify_otp'),
    path('add_to_wishlist/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_review/<int:book_id>/', views.add_review, name='add_review'),
    path('book_detail/<int:book_id>/', views.book_detail, name='book_detail'),
    # path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('subscribe-to-notifications/', subscribe_to_notifications, name='subscribe_to_notifications'),

]
