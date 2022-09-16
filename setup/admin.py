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
    BtOrder,
    BtGLAccounts
)
from setup.forms import BtUserCreationForm
from delegacje import app_config


class BtUserAdmin(UserAdmin):
    add_form = BtUserCreationForm

    list_display = ('id','first_name', 'last_name','username','vendor_id','group','email')

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
class BtGlAccountsAdmin(admin.ModelAdmin):
    list_display  = ('cost_category', 'tax_category', 'gl_account_number', 'description')
    ordering = ('cost_category',)
admin.site.register(BtGLAccounts, BtGlAccountsAdmin)
    

admin.AdminSite.site_url = '/' + app_config.LINK_PREFIX + 'e-delegacje'


