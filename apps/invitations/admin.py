from django.contrib import admin
from apps.invitations.models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "status", "plan_type", "view_count", "created_at", "published_at"]
    list_filter = ["status", "plan_type", "is_public", "created_at"]
    search_fields = ["title", "groom_name", "bride_name", "user__email"]
    readonly_fields = ["url_slug", "view_count", "created_at", "updated_at", "published_at"]
    fieldsets = (
        ("기본 정보", {"fields": ("user", "template", "title", "url_slug", "status")}),
        ("신랑 정보", {"fields": ("groom_name", "groom_father_name", "groom_mother_name", "groom_phone")}),
        ("신부 정보", {"fields": ("bride_name", "bride_father_name", "bride_mother_name", "bride_phone")}),
        (
            "예식 정보",
            {
                "fields": (
                    "wedding_date",
                    "wedding_location_name",
                    "wedding_location_address",
                    "wedding_location_lat",
                    "wedding_location_lng",
                )
            },
        ),
        ("메시지", {"fields": ("invitation_message", "greeting_message", "ending_message")}),
        ("옵션", {"fields": ("background_animation", "background_color", "font_family", "music_url")}),
        ("기능 설정", {"fields": ("enable_rsvp", "enable_guestbook", "enable_account_transfer")}),
        ("기타", {"fields": ("is_public", "view_count", "is_paid", "plan_type", "published_at")}),
    )
