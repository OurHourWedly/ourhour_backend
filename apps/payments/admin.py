from django.contrib import admin
from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'invitation', 'amount', 'plan_type', 'status', 'paid_at', 'created_at']
    list_filter = ['status', 'plan_type', 'created_at']
    search_fields = ['order_id', 'payment_key', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

