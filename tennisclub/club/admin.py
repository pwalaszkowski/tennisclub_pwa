from django.contrib import admin
from .models import TennisClubMember, Court

# Register the model
admin.site.register(TennisClubMember)
admin.site.register(Court)
