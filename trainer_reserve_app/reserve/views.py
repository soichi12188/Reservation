from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Employee, Reservation, Company
from .forms import UserRegisterForm, ProfileForm, LoginForm, ReservationForm, ReservationEditForm

# User認証と追加情報を分けて扱うことで保守性・拡張性を高める

def home(request):
    profile = None
    is_admin = False
    # authenticatedはログインしているかどうかを確認するメソッド
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)# type: ignore[attr-defined]
            is_admin = request.user.is_staff
        # これはこのままでいいのか確認
        # except以下は後ほど実装
        except Profile.DoesNotExist:# type: ignore[attr-defined]
            # passは何もしない
            pass
    return render(request, 'reserve/home.html',{
        'profile':profile,
        'is_admin':is_admin,
    })

def register(request):
    if request.user.is_authenticated:
        return redirect('mypage')

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # 複数のデータ保存をまとめて行うためにトランザクションを使う　
            # ユーザー情報とプロファイル情報をまとめて保存することで、どちらかが失敗した場合に両方ともロールバックされる
            try:
                with transaction.atomic():# type: ignore
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password1'])
                    user.save()
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
            # ログインしたユーザーをセッションに保存　移行request.userでログインしたユーザーの情報を取得できる
                login(request, user)
                messages.success(request, '登録が完了しました')
                return redirect('mypage')

            # Exceptionキャッチではなく、エラーの種類に応じて処理を分割する
            except Exception as e:
                messages.error(request, '登録に失敗しました')
    else:
        user_form=UserRegisterForm()
        profile_form=ProfileForm()
    return render(request, 'reserve/register.html',{'user_form':user_form, 'profile_form':profile_form})

# Djangoの標準認証システムはDjangoのUserモデルを使う場合にだけ有効
def login_view(request):
    # すでにログイン済みかを確認
    if request.user.is_authenticated:
        return redirect('mypage')
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password  = form.cleaned_data['password']
            # ユーザー名とパスワードが正しいかをチェック
            # 正しければUserを返す　間違いならNoneを返す　パスワードのハッシュ化やセキュリティ対策も自動でやってくれる
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # ユーザーがアクティブか(無効化orアカウント停止がされいないか)どうかを確認
                if user.is_active:
                    login(request, user)
                    return redirect('mypage')
                else:
                    error = 'アカウントが無効です'
            else:
                error = 'ユーザー名またはパスワードが違います'
    else:
        form= LoginForm()
    return render(request, 'reserve/login.html',{'form':form, 'error':error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def reserve(request):
    # ログインしていないユーザーアクセスすることはできないため、ログインしているユーザーのProfile情報を取得
    # このコードでログインしているがProfileがないユーザーを無くす
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        raise

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['date_time'] <= timezone.now():
                form.add_error('date_time', '過去の日時は選択できません')
            else:
                # 重複予約の確認のための変数を定義
                existing_reservation = Reservation.objects.filter(
                    # すでに取得済みのprofileを使う→データベースの負荷を軽減する
                    customer=profile,
                    date_time=form.cleaned_data['date_time'],
                    is_canceled=False,
                ).exists() #存在するか確認

                # 実際の重複予約確認ロジック
                if existing_reservation:
                    form.add_error('date_time', 'その日時はすでに予約されています')
                else:
                    # データベースに保存せずにオブジェクトを作成する→formで入力されていない情報を追加でセットできる
                    reservation = form.save(commit=False)
                    # ログインしているユーザーのProfile情報を取得して、reservationのcustomerフィールドにセットする
                    reservation.customer = profile
                    reservation.save()
                    messages.success(request, '予約が完了しました')

                    #　Djangoのモデルにはデフォルトでidというキーがあり、そのidをpkとして使うことができる　その予約に該当するidを渡す
                    # 指定したテンプレートをそのまま表示→入力フォームや一覧画面など：その場でデータを表示したいとき
                    return redirect('reservedetails', pk=reservation.pk)
    else:
        form = ReservationForm()
    # 新しいURLに移動させる→登録完了後の詳細画面など：何かの処理を行った後にユーザーを別のページに誘導したいとき
    # 理由：リロードで同じデータが二重登録されるなどのバグを防ぐため
    return render(request, 'reserve/reserve.html',{'form': form})

# 例外処理を使う　
@login_required
def reservedetails(request, pk):
    # 指定した条件に合うレコードがあれば取得し、なければ404エラーを返す関数
    reservation = get_object_or_404(
        # 予約と一緒に担当者や顧客の情報も取得する→他のモデルから情報を取得してくる
        Reservation.objects.select_related('employee', 'customer'),
        pk=pk,
    )
    # 予約の顧客が今ログインしているユーザーではない場合は403エラーを返す
    if reservation.customer.user != request.user:
        # 権限がない場合は403エラーを返すに変更
        return HttpResponseForbidden('権限がありません')
    return render(request, 'reserve/reservedetails.html',{
        'reservation':reservation
    })

@login_required
def reserve_edit(request,pk):
    # ログインしているユーザおのprofileが存在しない場合でもprofileを取得できるようにする
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        raise

    # 指定した条件に合うレコードがあれば取得し、なければ404エラーを返す関数
    res = get_object_or_404(
        Reservation,
        pk=pk,
        customer = profile,
        is_canceled = False,
    )

    if request.method =='POST':
        # instance=resと書くと、resに保存されている既存の予約内容をフォームに反映させることができる
        form = ReservationEditForm(request.POST, instance=res)
        if form.is_valid():
            if form.cleaned_data['date_time'] <= timezone.now():
                form.add_error('date_time', '過去の日時は選択できません')
            else:
                reservation_time = form.cleaned_data['date_time']
                existing_reservation = Reservation.objects.filter(
                    customer=profile,
                    date_time=reservation_time,
                    is_canceled=False,
                # 自分以外の予約を削除
                ).exclude(pk=res.pk).exists()

                if existing_reservation:
                    form.add_error('date_time', 'その日時はすでに予約されています')
                else:
                    try:
                        form.save()
                        messages.success(request, '予約が更新されました')
                        return redirect('reservedetails', pk=pk)
                    except Exception as e:
                        messages.error(request, '予約の更新に失敗しました')

    else:
        form = ReservationEditForm(instance=res)

    return render(request, 'reserve/reserve_edit.html', {'form':form})

@login_required
def reserve_cancel(request, pk):
    # sessionの自分の予約を受け取っている
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        raise

    reservation = get_object_or_404(
        Reservation,
        pk=pk,
        customer = profile,
        is_canceled = False,
    )

    if reservation.date_time <= timezone.now():
        messages.error(request, '過去の日時はキャンセルできません')
        return redirect('mypage')
    
    try:
        reservation.is_canceled = True
        reservation.canceled_at = timezone.now()
        # 変更をデータベースに保存
        reservation.save()
        messages.success(request, '予約がキャンセルされました')
    except Exception as e:
        messages.error(request, '予約のキャンセルに失敗しました')
    
    return redirect('mypage')

@login_required
def mypage(request):
    # 今ログインしているユーザーの追加情報を取得
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        raise

    now = timezone.now()
    # Reservationモデルの全データにアクセスし、customerが今ログインしているユーザーのものからemployeeフィールドも一緒に持ってくる
    base_queryset = Reservation.objects.select_related('employee').filter(customer=profile)
    # 持ってきたデータをcurrent,past,canceledのデータに切り分ける
    context = {
        # order_by('date_time')でdate_timeについてデータベースから指定したフィールドの値に基づいて昇順（小さい順）にソートしている
        # [:10]は取得する件数→10件だけ取得する
        'current_list':base_queryset.filter(date_time__gte=now, is_canceled=False).order_by('date_time')[:10],
        'past_list':base_queryset.filter(date_time__lt=now, is_canceled=False).order_by('-date_time')[:10],
        'canceled_list':base_queryset.filter(is_canceled=True).order_by('-canceled_at')[:10],
        'profile':profile,
    }
    return render(request, 'reserve/mypage.html', context)

# def mypagesettings(request):
#     # ログイン中のユーザーIDをsessionから取り出す
#     profile = get_object_or_404(Profile, user=request.user)
#     # そのIDでClientレコードを取得
#     if request.method == 'POST':
#         # Profileは「この画面のこのモデルのこのフィールドだけ編集させたい」といった会員情報編集用のフォーム
#         # 雛形のある部分を編集することに特化したフォーム
#         # instance=clientは既存の会員情報をフォームに読み込む＋保存もそのレコードに対して行うという指定
#         form = ProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('mypage')
#     else:
#         form = ProfileForm(instance=profile)
#     return render(request, 'reserve/mypagesettings.html',{'form':form})
