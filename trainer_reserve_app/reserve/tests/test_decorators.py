from django.test import TestCase, RequestFactory
from reserve.decorators import require_login, require_admin
from reserve.models import Client
from django.http import HttpResponse

# ダミー関数：テスト用の関数
def dummy_view(request):
    return HttpResponse(b"ok")

class DecoratorTest(TestCase):
    # 各テストの前に実行される準備処理
    def setUp(self):
        # RequestFactory：テスト用のリクエストを作成するため道具
        self.factory = RequestFactory()
        # テスト用のユーザーを作成
        self.client = Client.objects.create(#type: ignore
            name='a', gender=True, age=20, mail='a@a.com', password='x'
            )

    def test_require_login_redirect(self):
        # ログインしていない状態リクエストを作成
        request = self.factory.get('/')
        request.session = {} #type: ignore
        # require_loginデコレーターによるアクセス制限を確認
        response = require_login(dummy_view)(request)
        # ログインしていない場合はリダイレクト
        # 200：正常な画面　notequalであるため正常な画面ではないことを確認
        self.assertNotEqual(response.status_code, 200)

    def test_require_admin_redirect(self):
        # ログインしている＆管理者でない状態のリクエストを作成
        request = self.factory.get('/')
        request.session = {'client_id': self.client.id} #type: ignore
        self.client.is_admin = False
        self.client.save()
        # require_adminデコレーターによるアクセス制限を確認
        response = require_admin(dummy_view)(request)
        # 管理者でない場合はリダイレクト
        self.assertNotEqual(response.status_code, 200)