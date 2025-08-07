from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Employee, Reservation, Company
# Companyの登録フォームも作成

# UserRegisterFormは「ログインに必要な情報だけ管理」　Userは認証を行うために使う
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email','password1','password2']
    
    # user_form.is_valid()でバリデーションを行うと、clean_email()とclean_username()が自動で呼び出される
    def clean_email(self):
        # ユーザーがフォームに入力したメールアドレスを取得
        email = self.cleaned_data.get('email')
        # データベースに同じメールアドレスが存在するかを確認
        if User.objects.filter(email=email).exists():
            # 重複している場合はエラーを発生させる
            raise forms.ValidationError('このメールアドレスはすでに使用されています')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('このユーザー名はすでに使用されています')
        return username

# ProfileFormは「ユーザーの追加情報を管理」
class ProfileForm(forms.ModelForm):
    # genderはmodel内で定義したのでここでは定義しない
    class Meta:
        model = Profile
        fields = ['gender', 'age']

# 標準Userモデルではusernameとpasswordでログインするが、Profileモデルではemailとpasswordでログインする
class LoginForm(forms.Form):
    username = forms.CharField(label='ユーザー名',)
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(),
    )

class ReservationForm(forms.ModelForm):
    date_time = forms.DateTimeField(
        label='予約日時',
        widget=forms.DateTimeInput(
            attrs={'type':'datetime-local'}
            )
    )
    purpose = forms.CharField(
        label='目的',
        # 一行だけのテキストボックスを作成
        widget=forms.TextInput()
    )
    employee = forms.ModelChoiceField(
        label='担当者',
        # Employeeモデルに登録されているすべてのデータを選択肢にする
        queryset=Employee.objects.all(),
        # プルダウン形式の選択肢をフォームに表示
        widget=forms.Select()
    )
    class Meta:
        model = Reservation
        fields = ['date_time', 'purpose', 'employee']

class ReservationEditForm(forms.ModelForm):
    date_time = forms.DateTimeField(
        label='予約時間',
        widget=forms.DateTimeInput(attrs={'type':'datetime-local'})
    )
    purpose = forms.CharField(
        label='目的',
        widget=forms.TextInput()
    )
    employee = forms.ModelChoiceField(
        label='担当者',
        queryset=Employee.objects.all(),
        widget=forms.Select()
    )
    class Meta:
        model = Reservation
        fields = ['date_time', 'purpose', 'employee']

# class mypageSettingsForm(forms.ModelForm):


# # 管理者登録用のフォームを作る場合は、is_adminをフォームに追加
# class AdminRegisterForm(forms.Form):
#     password = forms.CharField(
#         widget=forms.PasswordInput(),
#     )
#     class Meta:
#         model = Client
#         fields = ['name', 'gender', 'age', 'mail', 'password']
# # is_adminはviewでTrueにする
