from django.shortcuts import render, redirect
from .forms import ClientForm,LoginForm,CurrentReservationForm,ProfileForm
from .models import Client, Current_reservation, Past_reservation
from django.utils import timezone

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
            # requestのsessionにユーザーIDをセットして自動ログイン状態
            request.session['client_id'] = client.id
            return redirect('mypage')
        
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
            # 保存したreservationのpkを渡す
            return redirect('reservedetails', pk=reservation.pk)
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
    # タイムゾーン設定に沿った今を返す関数
    now = timezone.now()
    # モデルの外部キーcustomerで絞り込みを行っている
    current = Current_reservation.objects.filter(
        customer=client,
        # gte=「以上」　未来の予約
        date_time__gte=now
        )
    # employee__(_が2つ)で記載するとemployee→その先のcustomerで絞り込みを行うことができる
    past = Current_reservation.objects.filter(
        customer=client,
        # lt=「未満」　過去の予約　それぞれを切り分ける
        date_time__lt=now
    )
    return render(request, 'reserve/mypage.html',{
        'current_list':current,
        'past_list':past,
        'client':client,
    })

def mypagesettings(request):
    # ログイン中のユーザーIDをsessionから取り出す
    client_id = request.session.get('client_id')
    # そのIDでClientレコードを取得
    client = Client.objects.get(pk=client_id)
    
    if request.method == 'POST':
        # Profileは「この画面のこのモデルのこのフィールドだけ編集させたい」といった会員情報編集用のフォーム
        # 雛形のある部分を編集することに特化したフォーム
        # instance=clientは既存の会員情報をフォームに読み込む＋保存もそのレコードに対して行うという指定
        form = ProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('mypage')
    
    else:
        form = ProfileForm(instance=client)

    return render(request, 'reserve/mypagesettings.html',{
        'form':form
    })

def logout_view(request):
    request.session.flush()
    return redirect('login')