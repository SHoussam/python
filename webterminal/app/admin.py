from django.contrib import admin

# Register your models here.


from .models import (
    User,
    Student,
    School,
    Company,
    Group,
    Team,
    Event,
    EventParticipant
)

admin.site.register(User)
admin.site.register(Student)
admin.site.register(School)
admin.site.register(Company)
admin.site.register(Group)
admin.site.register(Team)
admin.site.register(Event)
admin.site.register(EventParticipant)