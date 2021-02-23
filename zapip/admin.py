from django.contrib import admin

from zapip.models import Application, ZoomMeeting


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "external_id", "name", "created", "updated")
    search_fields = ("external_id", "name")
    readonly_fields = ("id", "created", "updated")


class ZoomMeetingAdmin(admin.ModelAdmin):
    list_display = ("id", "meeting_id", "user_id", "application", "created", "updated")
    search_fields = ("meeting_id", "user_id", "application")
    readonly_fields = ("id", "created", "updated")


admin.site.register(Application, ApplicationAdmin)
admin.site.register(ZoomMeeting, ZoomMeetingAdmin)
