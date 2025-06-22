from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField
    # 男＝true　女＝false　それ以外＝null
    gender = models.NullBooleanField
    age = models.IntegerField
    past = models.ForeignKey('Past_reservation', on_delete=models.CASCADE)
    current = models.ForeignKey('Current_reservation',on_delete=models.CASCADE)
    exsistence_current_reservation = models.BooleanField

class Employee(models.Model):
    name = models.CharField
    # 男＝true　女＝false　それ以外＝null
    gender = models.NullBooleanField
    age = models.IntegerField
    customer = models.ForeignKey('Client',on_delete=models.CASCADE)
    # Clientオブジェクトから予約を使う

class Current_reservation(models.Model):
    customer = models.ForeignKey('Client',on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE)
    date_time = models.DateTimeField
    purpose = models.CharField

class Past_reservation(models.Model):
    purpose = models.CharField
    employee = models.ForeignKey('Employee',on_delete=models.CASCADE)
    date_time = models.DateTimeField