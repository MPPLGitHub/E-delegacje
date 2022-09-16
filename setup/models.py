
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from e_delegacje.enums import (
    BtEmployeeLevel,
    BtMileageVehicleTypes,
    BtCostCategory,
    BtTaxCategory
)

class BtCompanyCode(models.Model):
    company_code = models.CharField(max_length=4)
    company_name = models.CharField(max_length=80)

    def __str__(self):
        return f'{self.company_code} - {self.company_name}'


class BtUser(AbstractUser):
    department = models.ForeignKey("BtDepartment", on_delete=models.PROTECT, related_name="bt_Users", null=True)
    employee_level = models.CharField(max_length=15, choices=BtEmployeeLevel.choices, default=BtEmployeeLevel.lvl7)
    manager = models.ForeignKey("BtUser", on_delete=models.PROTECT, related_name="bt_Users", null=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, null=True, blank=True)
    vendor_id = models.CharField(max_length=10, default='11')
    company_code = models.ManyToManyField(BtCompanyCode, default=1)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# class BtUserVendor(models.Model):
#     user_id = models.ForeignKey(BtUser, on_delete=models.PROTECT,related_name="bt_users_vendor" )
#     vendor_id = models.CharField(max_length=10)


class BtRegion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'


class BtDivision(models.Model):
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(BtUser, on_delete=models.PROTECT, related_name="Bt_Divisions")

    def __str__(self):
        return f'{self.name}'


class BtLocation(models.Model):
    name = models.CharField(max_length=100)
    profit_center = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.name} - {self.profit_center}'


class BtOrder(models.Model):
    """Model class for SAP Orders""" 
    order = models.CharField(max_length=12,null=True, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.order} - {self.name}'


class BtCostCenter(models.Model):
    text = models.CharField(max_length=50)
    cost_center_number = models.CharField(max_length=10)
    profit_center_id = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_CostCenters")
    company_code = models.ForeignKey(BtCompanyCode, on_delete=models.PROTECT, related_name="Bt_CostCenters")
    order = models.ForeignKey(
        BtOrder, 
        on_delete=models.PROTECT, 
        null=True,
        blank=True,
        related_name="Bt_CostCenters")

    def __str__(self):
        return f'{self.cost_center_number} - {self.text}'


class BtCountry(models.Model):
    country_name = models.CharField(max_length=20)
    alpha_code = models.CharField(max_length=3)

    def __str__(self):
        return f'{self.country_name}'


class BtCurrency(models.Model):
    code = models.CharField(max_length=3)
    text = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.code}'


class BtDelegationRate(models.Model):
    delagation_rate = models.IntegerField()
    country = models.ForeignKey(BtCountry, on_delete=models.PROTECT, related_name="Bt_Delegationrates", default=1)
    currency = models.ForeignKey(BtCurrency, on_delete=models.PROTECT, related_name="Bt_Delegationrates", default=1)    

    def __str__(self):
        return f'{self.country.country_name} - {self.delagation_rate} {self.currency}'


class BtMileageRates(models.Model):
    vehicle_type = models.CharField(max_length=20, choices=BtMileageVehicleTypes.choices)
    rate = models.DecimalField(decimal_places=4, max_digits=6)

    def __str__(self):
        return f'{self.vehicle_type} - rate: {self.rate}'


class BtDepartment(models.Model):
    name = models.CharField(max_length=100)
    manager_id = models.ForeignKey("BtUser", on_delete=models.PROTECT, related_name="Bt_Departments")
    profit_center = models.ForeignKey(BtLocation, on_delete=models.PROTECT, related_name="Bt_Departments")
    cost_center = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name="Bt_Departments")

    def __str__(self):
        return f'{self.name}'


class BtUserAuthorisation(models.Model):
    user_id = models.ForeignKey(BtUser, on_delete=models.PROTECT,related_name="bt_user_authorisations" )
    cost_center = models.ForeignKey(BtCostCenter, on_delete=models.PROTECT, related_name="bt_user_authorisations")
    company_code = models.ForeignKey(BtCompanyCode, on_delete=models.PROTECT, related_name="bt_user_authorisations")

    def __str__(self):
        return f'{self.user_id.first_name} {self.user_id.last_name} - {self.cost_center.cost_center_number}'


class BtGLAccounts(models.Model):
    gl_account_number = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    cost_category = models.CharField(max_length=40, choices=BtCostCategory.choices)
    tax_category = models.CharField(max_length=40, choices=BtTaxCategory.choices)
    
    def __str__(self):
        return f'{self.gl_account_number} - ({self.tax_category})- {self.cost_category}: {self.description}'