# celery（python向けの分散タスクキューライブラリ）を活用するためには
# ①pip install celeryを実行、celery：Django外でメール送信などを非同期・定期的に実行するためのもの　Djangoでceleryを実行するための方法
# ②brew install redis を実行、redis（メッセージブローカー）：celeryワーカーに何をするか順番待ちで渡す　
# ワーカー：ブローカーからタスクの指示を受け取り、その通りに処理を実行する

# celeryで実行できるタスクとして認識
# →for文でdeltaに1時間or24時間、flagに1or24のnotifiedを格納
# →window_startに何時間前に通知するか、window_endに1分間のバッファをもたす
# →qsにログインしているユーザーのwindow_start以上window_end未満の予約and flagがFalseの予約を格納
# →for文でrにqsの予約を格納
# →subject：件名 message：本文 from_email：送信元のメールアドレス recipient_list：r内のcustomerのmail内格納のアドレスにメールを送信するsend_mailを定義
# →setattrによって、r内のflagフィールドをTrueに変更
# →rの変更をデータベースに格納

# タスクをバックグラウンドで動かせるように登録するためのデコレーター
from celery import shared_task
from django.utils import timezone
# メールを送信するための関数
from django.core.mail import send_mail
# 「今から何時間後」「何分後」といった時間のずらし計算に使う
from datetime import timedelta
from .models import Current_reservation

# @shared_taskをつけることでCeleryがこの関数を実行できるタスクとして認識する
@shared_task
def send_reminders():
    now = timezone.now()
    # delta：何時間後の通知か　flag：モデルにある通知済みフラグのフィールド名
    # 同じ処理を2回行い、前日と1時間前の両方の通知をまとめて実装
    for delta, flag in[(1, 'notified_1h'), (24, 'notified_24h')]:
        # window_start：今からdela時間後の瞬間　window_end：その瞬間の1分後
        # Beatはちょうどそのタイミングで起動する保証はない→ちょうどの時間に設定すると1秒でも遅れる可能性があり確実に予約を拾い上げる保証ができないため
        window_start = now + timedelta(hours=delta)
        window_end = window_start + timedelta(minutes=1)

        qs = Current_reservation.objects.filter(
            # date_timeがwindow_start以上、date_timeがwindow_end未満の予約を取得
            # 予約時間から1分未満の予約されたものを持ってくる
            date_time__gte=window_start,
            date_time__lt=window_end,
            # 通知フラグがFalseのものを持ってくる
            **{flag:False},
        )
        # loginユーザーにメールを送信
        for r in qs:
            send_mail(
                # 件名
                subject=f"予約リマインダー：{r.purpose}",
                # 本文
                message=f"{r.date_time}の予約をお忘れなく！",
                # 送信もとメールアドレス
                from_email="lvngk527ts@gmail.com",
                # ユーザーメールアドレス
                recipient_list=[r.customer.mail],
            )
            # モデルのnotified_1h or notified_24hをTrueに変換
            setattr(r, flag, True)
            # フラグ変更を保存
            r.save()