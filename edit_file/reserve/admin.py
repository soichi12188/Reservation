from django.contrib import admin
# from .models import Employee,Client,Current_reservation

# # Register your models here.
# @admin.register(Client)
# class ClientAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'mail', 'gender', 'age','is_admin')
#     list_filter  = ('is_admin',)
#     search_fields = ('name', 'mail')

# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'gender', 'age', 'customer')
#     list_filter  = ('gender',)
#     search_fields = ('name',)

# # @admin.register(Current_reservation)
# # class Current_reservationAdmin(admin.ModelAdmin):
# #     list_display = ('id', 'client', 'employee', 'reservation_date', 'purpose')
# #     list_filter  = ('reservation_date',)
# #     search_fields = ('client__name', 'employee__name')