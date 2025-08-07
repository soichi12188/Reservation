import logging
# タスクをバックグラウンドで動かせるように登録するためのデコレーター
from celery import shared_task
# メールを送信するための関数
from django.core.mail import send_mail
from django.conf import settings
# 「今から何時間後」「何分後」といった時間のずらし計算に使う
from datetime import timedelta
from django.utils import timezone
from .models import Reservation, NotificationLog

logger = logging.getLogger(__name__)

# @shared_taskをつけることでCeleryがこの関数を実行できるタスクとして認識する
# bind=True：タスクインスタンスをselfで参照可能
# max_retries：リトライ回数の上限
# 現状：1時間前のリマインドのみを行なっているが、この関数を呼び出すときにreminder_hoursを指定することで、任意の時間前のリマインドを行うことができる
@shared_task(bind=True,max_retries=3)
def send_reminders(self, reminder_hours=1):

    """予約リマインドを送信するタスク"""
    try:
        # 通知対象時間の計算
        # timedelta(hours=reminder_hours)：指定時間後の時間を計算
        # reminder_hours：今から何時間後の時間が格納される（現状1時間後）
        reminder_time = timezone.now() + timedelta(hours=reminder_hours)
        # getattr：オブジェクトから属性を取得する関数　getattr(オブジェクト、属性名、デフォルト値)
        # settings：settings.pyの全体設定をさす
        # デフォルト値だと5分がtime_rangeに格納される
        # settings.pyにREMINDER_TIME_RANGE_MINUTESがあれば、その値でリマインドを行う
        time_range = getattr(settings, 'REMINDER_TIME_RANGE_MINUTES', 5)

        # 通知対象の予約を取得
        reservations = Reservation.objects.filter(
            # date_time_range：予約日時がreminder_timeの前後time_range分の範囲内にある予約を取得
            # 現状1時間後の予約で、+-5分の範囲内にある予約をreservation内から取得
            # date_time__range(start, end)：startからendまでの範囲内にある予約を取得
            date_time__range=(
                reminder_time - timedelta(minutes=time_range),
                reminder_time + timedelta(minutes=time_range),
            ),
            is_canceled=False,
        # 
        ).select_related('customer__user','employee')
        
        success_count = 0
        error_count = 0

        # 各予約ごとに通知処理を実行
        for reservation in reservations:
            # f'{}：文字列内に変数の値を埋め込む書き方
            notification_type = f'{reminder_hours}h_before'

            # すでに通知済みかチェック
            if NotificationLog.objects.filter(
                reservation=reservation,
                notification_type=notification_type,
                status='sent',
            ).exists():
                # continue：スキップして次の予約に進む
                continue

            # 通知ログを作成
            # get_or_create：既存のオブジェクトを一つ目の変数に取得、なければ新規作成してcreatedにTrue/Falseを格納
            notification_log, created = NotificationLog.objects.get_or_create(
                reservation=reservation,
                notification_type=notification_type,
                # 新規作成時のデフォルト値
                defaults={'status':'pending'},
            )

            try:
                # メール送信
                send_mail(
                    subject=f"予約リマインド：{reservation.date_time.strftime('%Y年%m%d %H:%M')}",
                    message=create_reminder_message(reservation),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reservation.customer.user.email],
                    # エラー時に例外を発生させるか
                    fail_silently=False,
                )

                # 成功時のログを更新
                notification_log.status = 'sent'
                notification_log.sent_at = timezone.now()
                notification_log.save()
                success_count += 1
                logger.info(f"リマインドメールを送信しました: {reservation.customer.user.username}")

            except Exception as e:
                # 失敗時のエラーハンドリング
                error_count += 1
                notification_log.status = 'failed'
                # 例外分を文字列に変換して保存
                notification_log.error_message = str(e)
                notification_log.save()
                logger.error(f"リマインドメール送信に失敗しました: {reservation.customer.user.username} - {e}")
            
            # リトライ処理
            # self.request.retries：Celeryが自動的に管理するリトライ回数
            if self.request.retries < self.max_retries:
                # self.retry：Celeryのリトライ機能 1回目60*(2*0)=60　２回目60*(2*1)=120　３回目60*(2*2)=240秒後にリトライするということ
                raise self.retry(countdown=60 * (2 ** self.request.retries))

            # 処理結果のログ出力
            # settings.pyのLOGGINGにどこにログを出力するかを設定
        logger.info(f"リマインドメール処理完了：成功{success_count}件、エラー{error_count}件")

    except Exception as e:
        # 全体のエラーハンドリング
        logger.error(f"リマインドタスク全体エラー: {e}")
        # raise：例外を発生させる
        # raiseのみ記載の場合、直前の例外を再度発生させる　except内の場合、exceptで捕まえたエラーを再度発生させる
        raise

def create_reminder_message(reservation):
    """リマインドメッセージを作成"""
    return f"""
{reservation.customer.user.username}様
    
以下の予約の時間が近づいています。

【予約詳細】
日時: {reservation.date_time.strftime("%Y年%m月%d日 %H:%M")}
担当者: {reservation.employee.name}
目的: {reservation.purpose}

お忘れのないようお気をつけください。

※このメールは自動送信されています。
"""