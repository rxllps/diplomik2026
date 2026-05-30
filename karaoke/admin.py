from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from clubuser.models import ClubUser
from rooms.models import Room, ServicePackage, TimeSlot, Booking, Payment
from otziv.models import Review
from guest_otziv.models import GuestBook


class SuperAdmin(admin.ModelAdmin):
    pass


admin.site.register(ClubUser, UserAdmin)
admin.site.register(Room)
admin.site.register(Review)
admin.site.register(GuestBook)
admin.site.register(ServicePackage)
admin.site.register(TimeSlot)
admin.site.register(Booking)
admin.site.register(Payment)
