from django.urls import path
from. import views

# アプリケーションのurls.pyの次に見られる
# アプリケーションのurls.pyのpath('reserve/', include('reserve.urls')),からこのページに飛ぶ
urlpatterns= [
    # path('', views.index, name='index'),
    # reserveアプリケーションのviewsのhomwメソッドにアクセス
    path('', views.home, name='home'),
    path('reserve', views.reserve, name='reserve'),
    path('reservedetails', views.reservedetails, name='reservedetails'),
    path('mypage', views.mypage, name='mypage'),
    path('mypagesettings', views.mypagesettings, name='mypagesettings'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
]