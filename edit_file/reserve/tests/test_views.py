from django.test import TestCase
from django.urls import reverse
from reserve.models import Client, Employee, Current_reservation


class RegisterLoginFlowTest(TestCase):
    def test_register_login_logout(self):
        # 会員登録
        # reverse('register')で会員登録画面のURLを取得
        resp = self.client.post(reverse('register'), 
        {
            'name': '太郎', 'gender': True, 'age': 30, 'mail': 'taro@example.com', 'password': 'pass1234'
        })
        # 会員登録後はマイページにリダイレクトされるか確認
        self.assertRedirects(resp, reverse('mypage'))

        # ログアウト
        # reverse('logout')でログアウト画面のURLを取得
        resp = self.client.get(reverse('logout'))
        # ログアウト後はログインページにリダイレクトされるか確認
        self.assertRedirects(resp, reverse('login'))

        # ログイン
        resp = self.client.post(reverse('login'), 
        {
            'mail': 'taro@example.com', 'password': 'pass1234'
        })
        # ログイン後はマイページにリダイレクトされるか確認
        self.assertRedirects(resp, reverse('mypage'))

    def test_reserve_create(self):
        # テスト用のユーザーを作成
        client = Client.objects.create(#type: ignore
            name='a', gender=True, age=20, mail='a@a.com', password='x'
            )
        # テスト用のユーザーをセッションに保存
        self.client.session['client_id'] = client.id
        self.client.session.save()
        # テストクライアントではPOST時にセッションが正しく保存されない可能性があるため、cookieに保存
        self.client.cookies = self.client.session.cookies
        # テスト用の従業員を作成
        emp = Employee.objects.create(#type: ignore
            name='e', gender=True, age=30, customer=client
            )
        # 予約を作成＋フォームを送信
        resp = self.client.post(reverse('reserve'), {
            'date_time': '2025-07-15T14:30', 'purpose': 'テスト予約', 'employee': emp.id
        })
        # 302：リダイレクトが発生するか確認
        self.assertEqual(resp.status_code, 302) #type: ignore