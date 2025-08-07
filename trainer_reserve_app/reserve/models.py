from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# 会社名を別テーブルで管理することで拡張性を高める

# Userモデルが持つフィールドusername,password（ハッシュ化されたパスワード）,email,first_name,last_name,
# is_staff（管理画面アクセス可否）,is_active（有効/無効）,is_superuser（全権限管理者かどうか）,last_login（最終ログイン日時）,date_joined（登録日時）

# サービス利用企業を管理するモデル
# このモデルは他の企業には見えないような状態を作る必要がある
# このモデルが全モデルの親に位置する
class Company(models.Model):
    name = models.CharField(max_length=100)

# サービス利用企業に予約する個人（エンドユーザー）を管理するモデル
# Userモデルは標準のまま使い、Profileモデルで追加情報を拡張する

class Profile(models.Model):
    # 慣例として変数名userを使う
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 男＝true　女＝false
    GENDER_CHOICES = (
        (True, '男性'),
        (False, '女性'),
    )
    gender = models.BooleanField(choices=GENDER_CHOICES)
    age = models.IntegerField()
    # on_deleteを下記のようにすることでカンパニーが削除されるとprofileやemployee、reservationのcompanyがnullになる
    # 顧客や予約はカンパニーが削除されても残るようにする
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

# companyに所属する従業員を管理するモデル
# companyで絞る必要がある
# 1対多の関係を作る場合、多の方にForeignKeyを設定する
class Employee(models.Model):
    name = models.CharField(max_length=100)
    # 男＝true　女＝false
    gender = models.BooleanField()
    age = models.IntegerField()
    employee_number = models.IntegerField(default=0, unique=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

# 1対多の関係を作る場合、多の方にForeignKeyを設定する
# customerやemployeeを辿ってcompanyを取得することができるのでcompanyは設定しない
class Reservation(models.Model):
    customer = models.ForeignKey(Profile,on_delete=models.CASCADE, related_name='reservations')
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, related_name='reservations')
    date_time = models.DateTimeField()
    purpose = models.CharField(max_length=200)
    # キャンセルしているかしていないか
    is_canceled = models.BooleanField(default=False)
    # キャンセル日時
    canceled_at = models.DateTimeField(null=True, blank=True)
    # 何度もリマインドメールを送らないようにすでに送信済みかを覚えておく
    class Meta:
        verbose_name = '予約'
        verbose_name_plural = '予約'

# notificationlogが必要な理由
# 完全な履歴管理：送信日時、成功/失敗、エラー内容を記録
# デバッグの容易さ：問題発生時の原因特定が可能
# 拡張性：新しい通知タイプを簡単に追加可能
# データの整合性：実際の送信状況を正確に反映
class NotificationLog(models.Model):
    # どの予約に対する通知か指定
    reservation = models.ForeignKey(
        Reservation, 
        on_delete=models.CASCADE, 
        related_name='notification_logs'
    )
    # 通知タイプ：1時間前リマインド、24時間前リマインド、カスタムを指定
    notification_type = models.CharField(
        max_length=20,
        choices=(
            # ここに追加するだけで通知する時間を増やすことができる
            ('reminder_1h', '1時間前リマインド'),
            ('reminder_24h', '24時間前リマインド'),
            ('custom', 'カスタム')
        ),
        verbose_name = '通知タイム'
    )
    # 送信日時：実際に送信された日時を記録
    sent_at = models.DateTimeField(
        default=timezone.now,
        verbose_name = '送信日時'
    )
    # 送信状態：未送信、送信済み、送信失敗を記録
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', '未送信'),
            ('sent', '送信済み'),
            ('failed', '送信失敗')
        ),
        default='pending',
        verbose_name = '送信状態'
    )
    # エラーメッセージ：送信失敗時のエラー内容を記録
    error_message = models.TextField(
        blank=True,
        verbose_name = 'エラーメッセージ'
    )

    class Meta:
        verbose_name = '通知履歴'
        verbose_name_plural = '通知ログ'
        # 同じ予約の同じ通知タイプは重複しないように格納
        unique_together = ['reservation', 'notification_type']
        # 送信日時の新しい順に並び替え
        ordering = ['-sent_at']

# __init__や__str__はデフォルトで定義されているメソッド　__init__はインスタンスが作成されたときに呼ばれる　__str__はインスタンスを文字列に変換するときに呼ばれる
    def __str__(self):
        return f'{self.reservation} - {self.get_notification_type_display()} - {self.get_status_display()}'

# ユーザーごとに異なるリマインド設定が可能
class ReminderSetting(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE, 
        related_name='reminder_settings'
    )
# 通知タイプを管理
    notification_type = models.CharField(
        max_length=20,
        choices=(
            ('reminder_1h', '1時間前リマインド'),
            ('reminder_24h', '24時間前リマインド'),
            ('custom', 'カスタム')
        ),
        verbose_name = '通知タイム'
    )
# 有効、無効の設定：ユーザーが通知を無効化できる
    enabled = models.BooleanField(
        default=True, 
        verbose_name='有効'
    )
    
    custom_hours = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='カスタム時間（時間）',
        help_text='カスタム時間を設定してください。'
    )

    class Meta:
        verbose_name = 'リマインド設定'
        verbose_name_plural = 'リマインド設定'
        unique_together = ['profile', 'notification_type']
        
    # このユーザーの場合、この通知設定は何時間前にリマインドするか？を取得するメソッド
    def get_hours_before(self):
        """通知時間を取得するメソッド"""
        if self.notification_type == 'custom':
            return self.custom_hours or 1
        elif self.notification_type == 'reminder_1h':
            return 1
        elif self.notification_type == 'reminder_24h':
            return 24
        return 1