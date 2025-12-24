from django.contrib import admin
from .models import  Complaint, Event,EventPayment, Maintenance,UserProfile, Flat
from .models import Notification
from django.conf import settings
from twilio.rest import Client
# Register your models here.

admin.site.register(Complaint)
admin.site.register(UserProfile)
admin.site.register(Flat)
admin.site.register(Event)
admin.site.register(EventPayment)
admin.site.register(Maintenance)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        if obj.user:
            profiles = UserProfile.objects.filter(user=obj.user)
        else:
            profiles = UserProfile.objects.exclude(phone__isnull=True).exclude(phone='')

        for p in profiles:
            try:
                print("📤 Sending SMS from Admin:", p.phone)
                client.messages.create(
                    body=f"{obj.title}\n{obj.message}",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=p.phone,
                )
                print("✅ SMS SENT")
            except Exception as e:
                print("❌ SMS ERROR:", e)
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_read')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at', 'is_read')
    list_editable = ('is_read',)  # Admin can mark message as read directly