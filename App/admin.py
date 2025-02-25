from django.contrib import admin
from .models import SportProvider, SportPartner, SportWorker, SportActivity, Contract, AllowedActivity, Attendance,SportCode
# Register your models here.
class SportProviderAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_phone', 'company_address','user')
    search_fields = ('company_name', 'company_email')
    list_filter = ('company_name',)

admin.site.register(SportProvider, SportProviderAdmin)

class SportPartnerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_phone', 'company_address','user')
    search_fields = ('company_name', 'company_email')
    list_filter = ('company_name',)

admin.site.register(SportPartner, SportPartnerAdmin)

class SportWorkAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'sport_partner')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_filter = ('sport_partner',)

admin.site.register(SportWorker, SportWorkAdmin)

class SportActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'sport_provider')
    search_fields = ('activity_name', 'sport_provider__company_name')
    list_filter = ('sport_provider',)

admin.site.register(SportActivity, SportActivityAdmin)

class ContractAdmin(admin.ModelAdmin):
    list_display = ('sport_provider', 'sport_partner', 'start_date', 'end_date')
    search_fields = ('sport_provider__company_name', 'sport_partner__company_name')
    list_filter = ('sport_provider', 'sport_partner')

admin.site.register(Contract, ContractAdmin)

class AllowedActivityAdmin(admin.ModelAdmin):
    list_display = ('sport_activity', 'contract', 'allowed')
    search_fields = ('sport_activity__activity_name', 'contract__sport_provider__company_name', 'contract__sport_partner__company_name')
    list_filter = ('allowed',)

admin.site.register(AllowedActivity, AllowedActivityAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('sport_provider', 'sport_partner', 'sport_work', 'sport_activity', 'activity_date', 'activity_time')
    list_filter = ('sport_provider', 'sport_partner')
admin.site.register(Attendance, AttendanceAdmin)


@admin.register(SportCode)
class SportCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'sport_worker')
