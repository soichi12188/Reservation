from pyexpat import model
from django import forms
from django.forms import widgets
from .models import Client, Current_reservation

# フォームを増やすタイミングは、機能を実装しながら「ここにユーザー入力が必要だな」と感じたとき
# ModelForm ①モデルのフィールド定義（CharField や EmailField など）をそのままフォームの入力欄に変換してくれる、②入力チェック（必須／文字数制限など）もモデルに合わせて自動で行ってくれる
class ClientForm(forms.ModelForm):
    # フォーム上でユーザーに選ばせたい選択肢の組み合わせ
    GENDER_CHOICES = (
        (True, '男性'),
        (False, '女性')
    )
    # モデルのBooleanFieldを明示的にChiceFieldに置き換え（男性or女性の二択にするため）
    gender = forms.ChoiceField(
        label='性別',
        # <select><option value="True">男</option><option value="False">女</option></select>というhtmlが自動生成される
        choices= GENDER_CHOICES,
        # プルダウン形式にすると言う明示的な定義
        widget=forms.Select,
    )
    password = forms.CharField(
        label='パスワード',
        # passwordを伏せ字入力にしてくれる（●●●）
        widget= forms.PasswordInput(),
    )
    class Meta:
        # どのモデルを対象にしているか
        model = Client
        # どのフィールドをフォームに含めるか
        fields = ['name', 'gender', 'age', 'mail', 'password']

class LoginForm(forms.Form):
    mail = forms.EmailField(label='メールアドレス')
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(),
    )

class CurrentReservationForm(forms.ModelForm):
    date_time=forms.DateTimeField(
        label='予約日時',
        widget=forms.DateTimeInput(
            attrs={'type':'datetime-local'}
            )
    )
    
    class Meta:
        model = Current_reservation
        fields = ['date_time', 'purpose', 'employee']

class ProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        (True, '男性'),
        (False, '女性')
    )
    # モデルのBooleanFieldを明示的にChiceFieldに置き換え（男性or女性の二択にするため）
    gender = forms.ChoiceField(
        label='性別',
        # <select><option value="True">男</option><option value="False">女</option></select>というhtmlが自動生成される
        choices= GENDER_CHOICES,
        # プルダウン形式にすると言う明示的な定義
        widget=forms.Select,
    )
    # どのモデルをベースにどのフィールドを使って、どのウィジェットで表示するかを指定するもの
    class Meta:
        # どのモデルを使うか指定　会員情報のためClient
        model = Client
        # 編集を許可するモデルの属性リスト
        fields = ['name', 'gender', 'age', 'mail']
        # 表示方法の指定ができる
        widgets = {
            # 性別フィールドだけラジオボタンで表示
            'gender' : forms.RadioSelect(choices=[(True, '男性'), False, '女性']),
        }

class ReservationEditForm(forms.ModelForm):
    date_time = forms.DateTimeField(
        label='予約時間',
        widget=forms.DateTimeInput(attrs={'type':'datetime-local'})
    )
    # どのモデルをベースにどのフィールドを使って、どのウィジェットで表示するかを指定するもの
    class Meta:
        model = Current_reservation
        fields = ['date_time', 'purpose']

# 管理者登録用のフォームを作る場合は、is_adminをフォームに追加
class AdminRegisterForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(),
    )
    class Meta:
        model = Client
        fields = ['name', 'gender', 'age', 'mail', 'password']
# is_adminはviewでTrueにする
