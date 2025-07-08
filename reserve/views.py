from django.shortcuts import render, redirect
from .forms import ClientForm,LoginForm,CurrentReservationForm
from .models import Client, Current_reservation, Past_reservation

# viewの関数を作成するごとにページを増やすことができる
# def index(request):
#     return HttpResponse('Hello World')

# indexがない場合、下記でマッピングしたテンプレートが読み込まれる
def home(request):
    return render(request, 'reserve/home.html',{})

def register(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.set_password(form.cleaned_data['password'])
            client.save()
            return redirect('login')
        
    else:
        form = ClientForm()
    
    return render(request, 'reserve/register.html',{'form':form})

def login(request):
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            mail = form.cleaned_data['mail']
            pw   = form.cleaned_data['password']
            try:
                client = Client.objects.get(mail=mail)
                if client.check_password(pw):
                    request.session['client_id'] = client.id
                    return redirect('mypage')
                else:
                    error='パスワードが違います'
            except Client.DoesNotExist:
                error = 'メールアドレスが見つかりません'
    else:
        form= LoginForm()
    return render(request, 'reserve/login.html',{'form':form, 'error':error})

def reserve(request):
    if request.method == 'POST':
        form = CurrentReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer_id = request.session.get('client_id')
            reservation.save()
            return redirect('reservedetails')
    else:
        form = CurrentReservationForm()
    return render(request, 'reserve/reserve.html',{'form': form})


def reservedetails(request, pk):
    reservation = Current_reservation.objects.get(pk=pk)
    return render(request, 'reserve/reservedetails.html',{
        'reservation':reservation
    })

def mypage(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    current = Current_reservation.objects.filter(customor=client)
    past = Past_reservation.objects.filter(employee_customer=client)
    return render(request, 'reserve/mypage.html',{
        'current_list':current,
        'past_list':past,
        'client':client,
    })

def mypagesettings(request):
    return render(request, 'reserve/mypagesettings.html',{})