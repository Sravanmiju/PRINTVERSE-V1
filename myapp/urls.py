from django.urls import path
from myapp import views

urlpatterns = [
    # --- Public ---
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/shop/', views.register_shop, name='register_shop'),
    path('register/user/', views.register_user, name='register_user'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),

    # --- Admin ---
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_home/registered_shops/', views.registered_shops, name='registered_shops'),
    path('admin_home/approved_shops/', views.approved_shops, name='approved_shops'),
    path('admin_home/registered_users/', views.registered_users, name='registered_users'),
    path('approve_shop/<int:id>/', views.approve_shop, name='approve_shop'),
    path('reject_shop/<int:id>/', views.reject_shop, name='reject_shop'),
    
    # Category Management
    path('admin_home/manage_category/', views.manage_category, name='manage_category'),
    path('admin_home/delete_category/<int:id>/', views.delete_category, name='delete_category'),
    
    # Complaint Management (Admin View)
    path('admin_home/view_complaint/', views.view_complaint, name='view_complaint'),
    path('admin_home/reply_complaint/', views.reply_complaint, name='reply_complaint'),
    path('admin_home/view_feedback/', views.view_feedback, name='view_feedback'),

    # Requests & Orders
    path('admin_home/view_requests/', views.view_requests, name='view_requests'),
    path('admin_home/view_orders/', views.view_orders, name='view_orders'),

    # --- User Dashboard & Actions ---
    path('user_home/', views.user_home, name='user_home'),
    
    # User Complaint
    path('user_sent_complaint/', views.user_sent_complaint, name='user_sent_complaint'),
    path('submit_user_complaint/', views.submit_user_complaint, name='submit_user_complaint'),

    path('user_complaints_toshop/', views.user_complaints_toshop, name='user_complaints_toshop'),
    path('reply_customer_complaint/', views.reply_customer_complaint, name='reply_customer_complaint'),

    # User Feedback
    path('user_sent_feedback/', views.user_sent_feedback, name='user_sent_feedback'),
    path('submit_user_feedback/', views.submit_user_feedback, name='submit_user_feedback'),

    path('submit_product_rating/', views.submit_product_rating, name='submit_product_rating'),

    # --- Shop Dashboard & Actions ---
    path('shop_home/', views.shop_home, name='shop_home'),
    
    # Shop Complaint
    path('shop_sent_complaint/', views.shop_sent_complaint, name='shop_sent_complaint'),
    path('submit_shop_complaint/', views.submit_shop_complaint, name='submit_shop_complaint'),
    
    # Shop Feedback
    path('shop_sent_feedback/', views.shop_sent_feedback, name='shop_sent_feedback'),
    path('submit_shop_feedback/', views.submit_shop_feedback, name='submit_shop_feedback'),

    # --- Print Request System ---
    path('submit_print_request/', views.submit_print_request, name='submit_print_request'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('update_request_status/', views.update_request_status, name='update_request_status'),

    #Order Progress Update
    path('update_order_progress/', views.update_order_progress, name='update_order_progress'),

    #Update profile
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
    path('update_shop_profile/', views.update_shop_profile, name='update_shop_profile'),

    #Core
    path('gen3d/', views.gen3d, name='gen3d'),
    path('check-gradio-status/', views.check_gradio_status, name='check_gradio_status'),
]