from django.contrib import admin

from .models import User
from .models import ConfirmString

admin.site.register(User)
admin.site.register(ConfirmString)