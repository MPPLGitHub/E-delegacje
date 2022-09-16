from dataclasses import fields
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from setup.models import BtUser, BtLocation, BtUserAuthorisation
from e_delegacje.models import BtCompanyCode, BtCostCenter

class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        result = super().clean()
        entered_user = BtUser.objects.get(username=result['username'])
        if not entered_user:
            self.add_error('username', f'Nie ma takiego użytkownika {entered_user.first_name}')
        elif not entered_user.is_active:
            raise ValidationError('Użytkownik nieaktywny')


class BtUserCreationForm(forms.ModelForm):
    class Meta:
        model = BtUser
        fields = ('username',
                  'email',
                  'password',
                  'first_name',
                  'last_name',
                  'is_superuser',
                  'is_staff',
                  'is_active',
                  'group',
                  'company_code',
                  'vendor_id',
                  'department',
                  'manager',
                  'employee_level')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].queryset = BtUser.objects.all().exclude(employee_level='lvl1')

    def save(self, commit=True):
        user = super(BtUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class BtUserUpdateForm(forms.ModelForm):
    class Meta:
        model = BtUser
        fields = ('username',
            'email',
            'first_name',
            'last_name',
            'is_superuser',
            'is_staff',
            'is_active',
            'group',
            'company_code',
            'vendor_id',
            'department',
            'manager',
            'employee_level')


class LocationForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    profit_center = forms.CharField(label="Profit Center", max_length=10,)

    class Meta:
        model = BtLocation
        fields = "__all__"


    def clean_profit_center(self):
        profit_center = self.cleaned_data['profit_center']
        obj = BtLocation.objects.filter(profit_center=profit_center)
        if obj:
            raise forms.ValidationError('Ten Profit center juz istnieje Proszę popraw pole Profit Center')


class AuthorisationForm(forms.ModelForm):
    class Meta:
       model = BtUserAuthorisation
       fields = ('user_id', 'company_code', 'cost_center',)

    def __init__(self, *args, **kwargs):
        # setting initial value of bt_company_code and CostCenter to empty queryset
        super().__init__(*args, **kwargs)
        self.fields['user_id'].queryset = BtUser.objects.all().order_by('-id')
        self.fields['company_code'].queryset = BtCompanyCode.objects.none()
        self.fields['cost_center'].queryset = BtCostCenter.objects.none()

        if 'user_id' in self.data:
            
            try:
                user_id = int(self.data.get('user_id'))
                company_code = int(self.data.get('company_code'))
                # collecting costcenters to which target_user has authorisation
                authorisation_list = [authorisation.cost_center.id for authorisation in BtUserAuthorisation.objects.filter(user_id=user_id)]
                # if target_user is chosen, adding filtered querysets
                self.fields['company_code'].queryset = BtUser.objects.get(id=user_id).company_code.all()
                self.fields['cost_center'].queryset = BtCostCenter.objects.filter(company_code=company_code)

            except (ValueError, TypeError):
                print('exception occured')
                pass  # invalid input from the client; ignore and fallback to empty target_user queryset
        elif self.instance.pk:
            """when editing application"""
            self.fields['company_code'].queryset = self.instance.user_id.company_code.all()
            self.fields['cost_center'].queryset = BtCostCenter.objects.all()
        else:
            print('nie ma id_target_user?')
            print(f'self.data: {self.data}')
