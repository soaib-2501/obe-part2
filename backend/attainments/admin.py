from django.contrib import admin
from .models import Attainment, HistoricalCoAttainment, ProgramAttainment

admin.site.register(Attainment)
admin.site.register(ProgramAttainment)
admin.site.register(HistoricalCoAttainment)
