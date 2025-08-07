# ファイル位置：-A reservationと指定するとreservationパッケージ内の初期化処理を探す
# reservation/__init__.pyを通じてDjango側から参照できるようにする
import os
from celery import Celery

# Djangoの設定ファイル(settings.py)へのパスを環境変数に登録
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservation.settings')
# Celeryインスタンスを作成
app = Celery('reservation')
# settings.pyに書いたCELERY_BROKER_URLやCELERY_BEAT_SCHEDULEを読み込む
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.enable_utc = True
# reserve/tasks.pyの@shared_taskを自動で見つけて登録
app.autodiscover_tasks()


# celery -A reservation worker --loglevel=infoでエラーが出ていた原因
# →which celeryで確認したところ、実行場所がグローバルになっていた　本来であればvenv内で実行されなければならない
# →pip installを仮想環境適応前に実行したことが原因　→ pip installは仮想環境適応時に行う