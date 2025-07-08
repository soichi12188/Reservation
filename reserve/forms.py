from django import forms
from .models import Client, Current_reservation

# フォームを増やすタイミングは、機能を実装しながら「ここにユーザー入力が必要だな」と感じたとき
# ModelForm ①モデルのフィールド定義（CharField や EmailField など）をそのままフォームの入力欄に変換してくれる、②入力チェック（必須／文字数制限など）もモデルに合わせて自動で行ってくれる
class ClientForm(forms.ModelForm):
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