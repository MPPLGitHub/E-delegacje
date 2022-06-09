from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from setup.models import (
    BtUser,
    BtDivision,
    BtCostCenter,
    BtLocation,
    BtRegion,
    BtDepartment,
    BtMileageRates,
    BtDelegationRate,
    BtCurrency,
    BtCountry,
    BtCompanyCode,
    BtUserAuthorisation,
    BtOrder
)
from setup.forms import BtUserCreationForm


class BtUserAdmin(UserAdmin):
    add_form = BtUserCreationForm
    list_display = ('first_name', 'last_name','manager', 'id','vendor_id','group')
    fieldsets = ((None, {'fields': ('username',
                                    'password',
                                    'first_name',
                                    'last_name',
                                    'email',
                                    'company_code',
                                    'department',
                                    'manager',
                                    'employee_level',
                                    'vendor_id',
                                    'group',
                                    'is_superuser',
                                    'is_staff',
                                    'is_active',
                                    )}), )

    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('username',
                   'password',
                   'first_name',
                   'last_name',
                   'email',
                   'company_code',
                   'department',
                   'manager',
                   'employee_level',
                   'group',
                   'vendor_id',
                   'is_superuser',
                   'is_staff',
                   'is_active',
                   )
    },
                     ),)

    ordering = ('id',)

admin.site.register(BtUser, BtUserAdmin)
admin.site.register(BtCompanyCode)
admin.site.register(BtRegion)
admin.site.register(BtLocation)
admin.site.register(BtCostCenter)
admin.site.register(BtDepartment)
admin.site.register(BtMileageRates)
admin.site.register(BtDivision)
admin.site.register(BtDelegationRate)
admin.site.register(BtCurrency)
admin.site.register(BtCountry)
admin.site.register(BtUserAuthorisation)
admin.site.register(BtOrder)

admin.AdminSite.site_url = '/prod/e-delegacje'


