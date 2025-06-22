from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# viewの関数を作成するごとにページを増やすことができる
# def index(request):
#     return HttpResponse('Hello World')

# indexがない場合、下記でマッピングしたテンプレートが読み込まれる
def home(request):
    return render(request, 'reserve/home.html',{})

def reserve(request):
    return render(request, 'reserve/reserve.html',{})

def reservedetails(request):
    return render(request, 'reserve/reservedetails.html',{})

def mypage(request):
    return render(request, 'reserve/mypage.html',{})

def mypagesettings(request):
    return render(request, 'reserve/mypagesettings.html',{})

def login(request):
    return render(request, 'reserve/login.html',{})

def register(request):
    return render(request, 'reserve/register.html',{})