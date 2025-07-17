from django.shortcuts import render, redirect,get_object_or_404
from .forms import ClientForm,LoginForm,CurrentReservationForm,ProfileForm,ReservationEditForm,AdminRegisterForm
from .models import Client, Current_reservation, Past_reservation
from django.utils import timezone
from .decorators import require_admin, require_login


# viewの関数を作成するごとにページを増やすことができる
# def index(request):
#     return HttpResponse('Hello World')

# indexがない場合、下記でマッピングしたテンプレートが読み込まれる
def home(request):
    client = None
    is_admin = False
    if request.session.get('client_id'):
        from .models import Client
        client = Client.objects.get(pk=request.session['client_id'])#type:ignore
        is_admin = client.is_admin
    return render(request, 'reserve/home.html',{
        'client':client,
        'is_admin':is_admin,
    })

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

# Djangoの標準認証システムはDjangoのUserモデルを使う場合にだけ有効
# 今回はClientモデルを使うため、ログインページ、ログアウトページ、パスワードリセットページを自作する
def login(request):
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            mail = form.cleaned_data['mail']
            pw   = form.cleaned_data['password']
            try:
                client = Client.objects.get(mail=mail) #type: ignore
                if client.check_password(pw):
                    request.session['client_id'] = client.id
                    return redirect('mypage')
                else:
                    error='パスワードが違います'
            except Client.DoesNotExist: #type: ignore
                error = 'メールアドレスが見つかりません'
    else:
        form= LoginForm()
    return render(request, 'reserve/login.html',{'form':form, 'error':error})

def logout_view(request):
    request.session.flush()
    return redirect('login')

# 管理者だけが管理者ページにアクセスできる用のチェック　セキュリティ対策
@require_login #順番を入れ替えるとエラーになる
@require_admin
def admin_dashboard(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id) #type: ignore
    return render(request, 'reserve/admin_dashboard.html',{
        'client':client,
    })

@require_admin
def admin_user_list(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id) #type: ignore
    clients = Client.objects.all() #type: ignore
    return render(request, 'reserve/admin_user_list.html', {
        'clients': clients,
        'client': client,
    })

@require_admin
def admin_reservation_list(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id) #type: ignore
    reservations = Current_reservation.objects.all() #type: ignore
    return render(request, 'reserve/admin_reservation_list.html', {
        'reservations': reservations,
        'client': client,
    })

# 管理者ユーザーを新しく登録するページ
def admin_register(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id) #type: ignore
    if request.method == 'POST':
        # ユーザーが入力したデータをAdminRegisterFormに渡す
        form = AdminRegisterForm(request.POST)
        # 必須項目が空がじゃないか、メールアドレスの形式が正しいかなど入力内容が正しいかなどをチェック
        if form.is_valid():
            # form.save(commit=False)はデータベースに保存せずにオブジェクトを作成する
            # commit=Falseを使うと、データベースに保存せずにオブジェクトを作成することができる
            admin = form.save(commit=False) #type: ignore
            admin.is_admin = True
            admin.save()
            # 新しく登録した管理者ユーザーのIDを今ログインしているユーザーとしてセッションに保存
            # これでそのユーザーが管理者ダッシュボードにアクセスできるようになる
            request.session['client_id'] = admin.id
            return redirect('admin_dashboard')
    else:
        form = AdminRegisterForm()
    return render(request, 'reserve/admin_register.html', {'form': form, 'client': client})

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
    reservation = Current_reservation.objects.get(pk=pk) #type: ignore
    return render(request, 'reserve/reservedetails.html',{
        'reservation':reservation
    })

@require_login
def reserve_edit(request,pk):
    # 指定した条件に合うレコードがあれば取得し、なければ404エラーを返す関数
    # sesssionの中でキャンセルされていない予約を取得している
    res = get_object_or_404(
        Current_reservation,
        pk=pk,
        customer_id = request.session['client_id'],
        is_canceled = False,
    )
    if request.method =='POST':
        # instance=resと書くと、フォームの各フィールドにおけるすでにデータベースに保存されている既存オブジェクトを編集対象にする
        form = ReservationEditForm(request.POST, instance=res)
        if form.is_valid():
            form.save()
            return redirect('reservedetails', pk=pk)
    else:
        form = ReservationEditForm(instance=res)
    return render(request, 'reserve/reserve_edit.html', {'form':form})

@require_login
def reserve_cancel(request, pk):
    # sessionの自分の予約を受け取っている
    res = get_object_or_404(
        Current_reservation,
        pk=pk,
        customer_id = request.session['client_id']
    )
    res.is_canceled = True
    res.canceled_at = timezone.now()
    # 変更をデータベースに保存
    res.save()
    return redirect('mypage')

def mypage(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id) #type: ignore
    # タイムゾーン設定に沿った今を返す関数
    now = timezone.now()
    # Current_reservationのオブジェクトを作成する際の絞り込みをfilterで行っている
    current = Current_reservation.objects.filter( #type: ignore
        customer=client,
        # gte=「以上」　未来の予約
        date_time__gte=now,
        is_canceled = False
        )
    # employee__(_が2つ)で記載するとemployee→その先のcustomerで絞り込みを行うことができる
    past = Current_reservation.objects.filter( #type: ignore
        customer=client,
        # lt=「未満」　過去の予約　それぞれを切り分ける
        date_time__lt=now,
        is_canceled = False,
    )
    cancel = Current_reservation.objects.filter( #type: ignore
        customer = client,
        is_canceled = True,
    )
    return render(request, 'reserve/mypage.html',{
        'current_list':current,
        'past_list':past,
        'canceled_list':cancel,
        'client':client,
    })

def mypagesettings(request):
    # ログイン中のユーザーIDをsessionから取り出す
    client_id = request.session.get('client_id')
    # そのIDでClientレコードを取得
    client = Client.objects.get(pk=client_id) #type: ignore
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