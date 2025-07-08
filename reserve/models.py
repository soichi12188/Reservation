from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100)
    # 男＝true　女＝false
    gender = models.BooleanField(null=True)
    age = models.IntegerField()
    mail = models.EmailField()
    past = models.ForeignKey('Past_reservation', 
                            on_delete=models.CASCADE,
                            null= True,
                            blank=True,
                            # 別のモデルから「逆向き」にデータを取るときに活用
                            related_name='client_past')
    current = models.ForeignKey('Current_reservation',
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True,
                                # 別のモデルから「逆向き」にデータを取るときに活用
                                related_name='clients_current')
    exsistence_current_reservation = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    # save()のオーバーライド
    # データベースに書き込むときに必ずハッシュ化されるように設定
    # *args, **kwargsは可変長変数なので、どれだけ多くの引数を渡されても受け取れるようにする仕組み
    def save(self, *args, **kwargs):
        # ハッシュ化されているかを確認
        # ハッシュ化されていると冒頭に「pbkdf2_」が頭文字とされている
        if self.password and not self.password.startswith('pbkdf2_'):

            # ハッシュ化されてからデータベースへ書き込み
            self.password = make_password(self.password)

        super().save(*args, **kwargs)


class Employee(models.Model):
    name = models.CharField(max_length=100)
    # 男＝true　女＝false
    gender = models.BooleanField()
    age = models.IntegerField()
    customer = models.ForeignKey('Client',on_delete=models.CASCADE)
    # Clientオブジェクトから予約を使う

class Current_reservation(models.Model):
    customer = models.ForeignKey('Client',on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    purpose = models.CharField(max_length=100)

class Past_reservation(models.Model):
    purpose = models.CharField(max_length=100)
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE)
    date_time = models.DateTimeField()