from django.test import TestCase
from reserve.forms import ClientForm

# 正しい入力データでフォームが有効か確認
class ClientFormTest(TestCase):
    def test_valid_form(self):
        # フォームがこのデータで作成できるか確認
        form = ClientForm(data={'name':'a','gender':True,'age':20,'mail':'a@a.com','password':'pass1234'})
        # フォームが有効か確認
        self.assertTrue(form.is_valid())

    # メールアドレスが正しくない場合にフォームが無効か確認
    def test_invalid_mail(self):
        # フォームがこのデータで作成できないか確認
        form = ClientForm(data={'name':'a','gender':True,'age':20,'mail':'notanemail','password':'pass1234'})
        # フォームが無効か確認
        self.assertFalse(form.is_valid())