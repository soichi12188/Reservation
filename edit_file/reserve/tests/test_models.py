# Djangoのテスト用の基本クラス
from django.test import TestCase
# テスト対象
from reserve.models import Client, Employee, Current_reservation
from django.utils import timezone

# ユーザー作成とパスワードの動作確認
class ClientModelTest(TestCase):
    def test_create_client_and_password(self):
        # ユーザー作成
        client = Client.objects.create( #type: ignore
            name='test_client',
            mail='test@example.com',
            gender=True,
            age=20,
        )
        # パスワード設定
        client.set_password('test_password')
        client.save()
        # パスワードでログインできるか確認＋パスワードが暗号化されているか確認
        self.assertTrue(client.check_password('test_password'))
    
    # 同じメールアドレスで複数のユーザーを作成できないか確認
    def test_unique_mail(self):
        # 最初のユーザー作成
        client = Client.objects.create( #type: ignore
            name='test_client',
            mail='test@example.com',
            password='test_password',
            gender=True,
            age=20,
        )
        # 同じメールアドレスで2つ目のユーザーを作成しようとするとエラーが発生するか確認
        with self.assertRaises(Exception):
            Client.objects.create( #type: ignore
                name='test_client',
                mail='test@example.com',
                password='test_password',
                gender=True,
                age=20,
            )

# 予約作成の動作確認
class ReservationModelTest(TestCase):
    def test_create_reservation(self):
        client = Client.objects.create( #type: ignore
            name='test_client',
            mail='test@example.com',
            password='test_password',
            gender=True,
            age=20,
        )
        emp = Employee.objects.create( #type: ignore
            name='test_employee',
            gender=True,
            age=20,
            customer=client,
        )
        # 上記を使って予約を作成
        reservation = Current_reservation.objects.create( #type: ignore
            customer=client,
            employee=emp,
            date_time=timezone.now(),
            purpose='test_purpose',
        )
        # 予約の内容が正しく保存されているか確認
        self.assertEqual(reservation.customer, client)