from django.urls import path, include
from. import views

# アプリケーションのurls.pyの次に見られる
# アプリケーションのurls.pyのpath('reserve/', include('reserve.urls')),からこのページに飛ぶ
urlpatterns= [
    # path('', views.index, name='index'),
    # reserveアプリケーションのviewsのhomwメソッドにアクセス
    path('', views.home, name='home'),
    # path('accounts/', include('django.contrib.auth.urls')),　# Djangoの標準認証システムはDjangoのUserモデルを使う場合にだけ有効
    path('reserve/', views.reserve, name='reserve'),
    path('reservedetails/<int:pk>/', views.reservedetails, name='reservedetails'),
    path('<int:pk>/edit', views.reserve_edit, name='reserve_edit'),
    path('<int:pk>/cancel', views.reserve_cancel, name='reserve_cancel'),
    path('mypage/', views.mypage, name='mypage'),
    # path('mypagesettings/', views.mypagesettings, name='mypagesettings'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view,name='logout'),
    # 管理者用画面のパス
    # path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('admin_register/', views.admin_register, name='admin_register'),
    # path('admin_user_list/', views.admin_user_list, name='admin_user_list'),
    # path('admin_reservation_list/', views.admin_reservation_list, name='admin_reservation_list'),
]