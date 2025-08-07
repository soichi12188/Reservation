# デコレータは元の関数をそのまま動かすのではなく、前処理と後処理を追加した新しい関数で包むこと

# 元の関数の名前や文字列を後で作る_wrapped関数にコピーしてくれる
from functools import wraps
from django.shortcuts import redirect
from .models import Client

# ログインしているかを確認できる
def require_login(view_func):
    # sessionのclient_idをチェックし、未ログインなら/reserve/loginへリダイレクトする
    # @wraps(view_func)をつけると _wrappedが元のview_funcと同じ属性や名前を持つようになる
    @wraps(view_func)
    # シグネチャ＝関数が受け取る引数の形　*args, **kwargs（必要に応じて付いてくる追加の引数）の両方をそのまま元のビューに渡せる
    def _wrapped(request, *args, **kwargs):
        # requestのsessionが未ログインの場合(None)の場合、loginにリダイレクト
        if not request.session.get('client_id'):
            redirect('login')
        # セッションにclient_idがあれば、view_func(元のビュー reserve_editに@require_loginの記載がある場合、reserve_editが元)を返す
        # ビュー関数は必ずHttpResponse(画面表示)を返す　view_funcを返すと元のビューを返す
        return view_func(request, *args, **kwargs)
    # wrappedを返すことで@require_loginをつけた関数がwrapsされた状態の動作をする
    return _wrapped


# このページにアクセスできるのは管理者だけという入り口のチェック
# 管理者だけが管理者ページにアクセスできる用のチェック　セキュリティ対策
# デコレータ自体にデコレータをつけてはいけない
# デコレータ自体にデコレータをつけると、関数として実行されてしまうためエラーが発生する
def require_admin(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        client_id = request.session.get('client_id')
        # client_idに合うユーザーを取得
        client = Client.objects.get(pk=client_id) #type: ignore
        # clientのis_adminがFalseの場合はマイページにリダイレクト
        if not client.is_admin:
            return redirect('mypage') #type: ignore
        # 管理者の場合は元のビューを返す
        return view_func(request, *args, **kwargs)
    return _wrapped