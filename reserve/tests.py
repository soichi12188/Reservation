from django.test import TestCase
from django.urls import reverse
from .models import Client, Current_reservation,Employee

# アプリ全体の主要な画面フローをまとめてテスト
# TestCaseを継承しているので、各テストメソッドの前後でデータベースがリセットされる
class AppFlowTest(TestCase):
    # test→register→login→reserveの一連の操作をまとめている
    def test_register_login_reserve_flow(self):
        # 1) 会員登録
        resp = self.client.post(reverse('register'), {
            'name': '太郎',
            'gender': True,
            'age': 30,
            'mail': 'taro@example.com',
            'password': 'pass1234'
        })
        # 登録後はマイページにリダイレクトされている
        self.assertRedirects(resp, reverse('mypage'))

        # 2) ログアウト
        resp = self.client.get(reverse('logout'))
        self.assertRedirects(resp, reverse('login'))

        # 3) ログイン
        resp = self.client.post(reverse('login'), {
            'mail': 'taro@example.com',
            'password': 'pass1234'
        })
        self.assertRedirects(resp, reverse('mypage'))

        client = Client.objects.get(mail= 'taro@example.com')

        Employee.objects.create(
            name='テストスタッフ',
            gender=True,
            age=40,
            customer=client
            )


        # 4) 予約作成
        resp = self.client.post(reverse('reserve'), {
            'date_time': '2025-07-15T14:30',
            'purpose': 'テスト予約',
            'employee': Employee.objects.first().id  # 事前に従業員レコードを用意しておく
        })
        # 予約完了ページへリダイレクト
        self.assertEqual(resp.status_code, 302)

        # 5) マイページに現在予約として存在
        resp = self.client.get(reverse('mypage'))
        self.assertContains(resp, 'テスト予約')