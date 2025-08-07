# celery.pyで定義したappをcelery_appの名前で外部に公開する
# celery -A reservation worker が「reservation.celery_app を探してタスクを実行してね」という契約に基づくため、このエントリポイントが無いと Celery がどのインスタンスを使えばいいかわからない

from .celery import app as celery_app
__all__ = ['celery_app']