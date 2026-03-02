from django.contrib import admin

from users.models import Payment, User

admin.site.register(User)
admin.site.register(Payment)
