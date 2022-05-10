""" Forms classes for e_delegacje"""

import datetime
from urllib import request
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory
from django.forms import MultiWidget
from django.http import QueryDict
from e_delegacje.models import (
    BtApplicationSettlement,
    BtApplicationSettlementFeeding,
    BtApplicationSettlementInfo,
    BtApplication
)
from setup.models import BtCompanyCode, BtMileageRates, BtUser, BtCostCenter, BtCurrency, BtCountry, BtUserAuthorisation

from django.core.mail import EmailMultiAlternatives
from django import forms

from e_delegacje.enums import (
    BtApplicationStatus,
    BtTransportType,
    BtCostCategory,
    BtVatRates,
)


class DateInputWidget(forms.DateInput):
    """Changes input type in DateInput"""
    input_type = 'date'


class TimeInputWidget(forms.TimeInput):
    """Changes input type in Timeinput"""
    input_type = 'time'


class BtCompletedAttributesWidget(forms.TypedChoiceField.widget):
    """Adds attributes to TypedChoiceField """
    forms.TypedChoiceField.widget(attrs={'onchange': "ChangeAtributesRequied()", 'id': 'id_bt_completed'})


class BtApplicationForm(forms.ModelForm):
    """form for creating applications"""
    target_user = forms.ModelChoiceField(
        queryset=BtUser.objects.all(),
        error_messages={'required': 'To pole musi być wypełnione'},
        label="Delegowany"
    )
    bt_company_code = forms.ModelChoiceField(
        queryset=BtCompanyCode.objects.all(),
        error_messages={'required': 'To pole musi być wypełnione'},
        
        label="Wybierz spółkę",
    )
    bt_country = forms.ModelChoiceField(
        queryset=BtCountry.objects.all(),
        label="Wybierz kraj",
        error_messages={'required': 'To pole musi być wypełnione'},
        
        initial=BtCountry.objects.get(id=1)
    )
    trip_purpose_text = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={'rows': 3}),
        error_messages={'required': 'To pole musi być wypełnione'},
        help_text='',
        label="Cel podróży")
    CostCenter = forms.ModelChoiceField(
        queryset=BtCostCenter.objects.all(), 
        error_messages={'required': 'To pole musi być wypełnione'},
        help_text='',
        label="Cost Center")
    transport_type = forms.TypedChoiceField(
        choices=BtTransportType.choices,
        empty_value='Wybierz rodzaj transportu',
        error_messages={
            'required': 'To pole musi być wypełnione', 
            'invalid_choice':'To pole musi być wypełnione'
        },
        label="Rodzaj transportu",)
    travel_route = forms.CharField(
        max_length=120, 
        widget=forms.Textarea(attrs={'rows': 1}), 
        error_messages={'required': 'To pole musi być wypełnione'},
        help_text='',
        label="Trasa podróży")
    planned_start_date = forms.DateField(
        label="Data wyjazdu",
        initial=datetime.date.today(),
        help_text='Domyślnie wpisana jest dzisiejsza data. Pamietaj by ją zmienić!',
        widget=DateInputWidget
    )
    planned_end_date = forms.DateField(
        label="Data powrotu",
        error_messages={'required': 'To pole musi być wypełnione'},
        initial=datetime.date.today(),
        help_text='Domyślnie wpisana jest data dzisiejsza. Pamietaj by ją zmienić!',
        widget=DateInputWidget
    )
    advance_payment_currency = forms.ModelChoiceField(
        queryset=BtCurrency.objects.all(),
        label="Waluta",
        blank=True,
        initial=BtCurrency.objects.get(code='PLN')
    )
    advance_payment = forms.DecimalField(
        decimal_places=2, 
        max_digits=6, 
        label="Zaliczka", 
        help_text='',
        initial=0, 
        min_value=0)
    current_datetime = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = BtApplication
        fields = ('target_user', 
        'bt_company_code',
        'CostCenter',
        'trip_purpose_text',
        'bt_country',
        'transport_type',
        'travel_route',
        'planned_start_date',
        'planned_end_date',
        'advance_payment',
        'advance_payment_currency',
        'current_datetime'
        )
    
    def __init__(self, *args, **kwargs):
        """setting initial value of bt_company_code and CostCenter to empty queryset
            if target_user exist in self.data, Filters list of company codes and CostCenters to 
            which target_user has authorisations"""
        super().__init__(*args, **kwargs)
        self.fields['bt_company_code'].queryset = BtCompanyCode.objects.none()
        self.fields['CostCenter'].queryset = BtCostCenter.objects.none()

        if 'target_user' in self.data:
            try:
                target_user = int(self.data.get('target_user'))
                # collecting list of company codes to which target_user has authorisations set
                c_codes_list = [cc.id for cc in BtUser.objects.get(id=target_user).company_code.all()]
                # collecting costcenters to which target_user has authorisation
                authorisation_list = [authorisation.cost_center.id for authorisation in BtUserAuthorisation.objects.filter(user_id=target_user)]
                # if target_user is chosen, adding filtered querysets
                self.fields['bt_company_code'].queryset = BtUser.objects.get(id=target_user).company_code.all()
                self.fields['CostCenter'].queryset = BtCostCenter.objects.filter(id__in=authorisation_list)

            except (ValueError, TypeError):
                print('exception occured')
                pass  # invalid input from the client; ignore and fallback to empty target_user queryset
        elif self.instance.pk:
            """when editing application"""
            self.fields['target_user'].queryset = BtUser.objects.filter(department=self.instance.application_author.department)
            self.fields['bt_company_code'].queryset = self.instance.target_user.company_code
            authorisation_list = [authorisation.id for authorisation in BtUserAuthorisation.objects.filter(user_id=self.instance.target_user.id)]
            self.fields['CostCenter'].queryset = BtCostCenter.objects.filter(id__in=authorisation_list)

    def clean(self):
        """planned_end_date can't be before planned_start_date"""
        result = super().clean()
        if result['planned_start_date'] > result['planned_end_date']:
            raise ValidationError("Data wyjazdu musi być przed datą powrotu!")
        
        

class BtApplicationSettlementForm(forms.Form):
    """Settlement form"""
    bt_application_id = forms.ModelChoiceField(
        queryset=BtApplication.objects.all(),
        label="",
        empty_label="wybierz wniosek do rozliczenia"
    )


class BtApplicationSettlementInfoForm(forms.ModelForm):
    """Form for detailed information of settlement"""
    bt_completed = forms.TypedChoiceField(
        label="Czy delegacja się odbyła?",
        choices=[('', ''), ('tak', 'tak'), ('nie', 'nie')],
        widget=forms.TypedChoiceField.widget(attrs={'onchange': "ChangeAtributesRequied()", 'id': 'id_bt_completed'})
        )
    bt_start_date = forms.DateField(
        label="Data wyjazdu",
        widget=DateInputWidget(attrs={'id': 'id_bt_start_date'}),
        required=False)
    bt_start_time = forms.TimeField(
        label="Godzina wyjazdu",
        widget=TimeInputWidget(attrs={'id': 'id_bt_start_time'}),
        required=False)
    bt_end_date = forms.DateField(
        label="Data powrotu",
        widget=DateInputWidget(attrs={'id': 'id_bt_end_date'}),
        required=False)
    bt_end_time = forms.TimeField(
        label="Godzina powrotu",
        widget=TimeInputWidget(attrs={'id': 'id_bt_end_time'}),
        required=False)
    settlement_exchange_rate = forms.DecimalField(decimal_places=5,
                                                  max_digits=8,
                                                  label="Kurs rozliczenia",
                                                  min_value=0,
                                                  initial=1,
                                                  help_text='W przypadku zaliczki w PLN wpisz "1".',
                                                  required=False,
                                                  widget=forms.DecimalField.widget(
                                                      attrs={'id': 'id_settlement_exchange_rate'})
                                                  )
    current_datetime = forms.CharField(
        max_length=40,
        widget=forms.CharField.widget(attrs={'id': 'id_current_datetime', 'type': 'hidden'}))

    class Meta:
        model = BtApplicationSettlementInfo
        exclude = ('bt_application_settlement', 'advance_payment', 'settlement_log')
    
    def clean(self):
        result = super().clean()

        if result['bt_completed'] == 'tak':
            comb_start_time = datetime.datetime(
                result['bt_start_date'].year,
                result['bt_start_date'].month,
                result['bt_start_date'].day,
                result['bt_start_time'].hour,
                result['bt_start_time'].minute)

            comb_end_time = datetime.datetime(
                result['bt_end_date'].year,
                result['bt_end_date'].month,
                result['bt_end_date'].day,
                result['bt_end_time'].hour,
                result['bt_end_time'].minute)

            if comb_start_time > comb_end_time:
                raise ValidationError("Data i godzina wyjazdu musi być przed datą i godziną powrotu!")

        return result


class BtApplicationSettlementCostForm(forms.Form):
    """Settlement cost form"""
    bt_cost_category = forms.TypedChoiceField(choices=BtCostCategory.choices, label="Kategoria kosztu", initial="")
    bt_cost_description = forms.CharField(max_length=120, label="Opis")
    bt_cost_amount = forms.DecimalField(decimal_places=2, max_digits=8, label="Kwota", min_value=0)
    bt_cost_currency = forms.ModelChoiceField(queryset=BtCurrency.objects.all(), label="Waluta", initial='')
    bt_cost_document_date = forms.DateField(label="Data dokumentu", widget=DateInputWidget)
    bt_cost_VAT_rate = forms.TypedChoiceField(choices=BtVatRates.choices, label="Stawka vat")
    attachment = forms.FileField()


class BtApplicationSettlementMileageForm(forms.Form):
    """Mileage lump sum form"""
    bt_car_reg_number = forms.CharField(max_length=8, label='Numer rejestracyjny')
    bt_mileage_rate = forms.ModelChoiceField(queryset=BtMileageRates.objects.all(), label='Stawka')
    trip_start_place = forms.CharField(max_length=50, label='Miejsce wyjazdu')
    trip_date = forms.DateField(widget=DateInputWidget, label='Data przejazdu')
    trip_description = forms.CharField(max_length=120, label='Trasa przejazdu')
    trip_purpose = forms.CharField(max_length=240, label='Cel przejazdu')
    mileage = forms.IntegerField(label='Liczba kilometrów', min_value=0)
    is_agreement_signed = forms.BooleanField(label='Czy masz podpisaną umowe?')


class BtApplicationSettlementFeedingForm(forms.ModelForm):
    """Feedeing form"""
    breakfast_quantity = forms.IntegerField(label='Liczba zapewnionych śniadań', min_value=0, initial=0)
    dinner_quantity = forms.IntegerField(label='Liczba zapewnionych obiadów', min_value=0, initial=0)
    supper_quantity = forms.IntegerField(label='Liczba zapewnionych kolacji', min_value=0, initial=0)

    class Meta:
        model = BtApplicationSettlementInfo
        fields = ('breakfast_quantity', 'dinner_quantity', 'supper_quantity')
        widgets = forms.IntegerField.widget(attrs={'onchange': "get_onchange_meals_correction()"})


BtApplicationSettlementInfoFormset = inlineformset_factory(
    BtApplicationSettlement,
    BtApplicationSettlementInfo,
    fields=('bt_completed',
            'bt_start_date',
            'bt_start_time',
            'bt_end_date',
            'bt_end_time',
            'settlement_exchange_rate',
            'current_datetime'),
    form=BtApplicationSettlementInfoForm,
    labels={'bt_start_date': "Data wyjazdu",
            'bt_start_time': "Godzina wyjazdu",
            "bt_end_date": "Data powrotu",
            "bt_end_time": "Godzina powrotu",
            'bt_completed': "Czy delegacja się odbyła?",
            'settlement_exchange_rate': "Kurs rozliczenia",
            },
    widgets={'bt_start_date': DateInputWidget(attrs={'id': 'id_bt_start_date'}),
             'bt_end_date': DateInputWidget(attrs={'id': 'id_bt_end_date'}),
             'bt_start_time': DateInputWidget(attrs={'id': 'id_bt_start_time'}),
             'bt_end_time': TimeInputWidget(attrs={'id': 'id_bt_end_time'}),
             'bt_completed': forms.TypedChoiceField.widget(
                 attrs={'onchange': "ChangeAtributesRequied()", 'id': 'id_bt_completed'}),
             # 'current_datetime': CurrentDatetimeHiddenWidget(attrs={'id': 'id_current_datetime'}),
             'settlement_exchange_rate': forms.DecimalField.widget(attrs={'id': 'id_settlement_exchange_rate'})

             },

    can_delete=False
)


BtApplicationSettlementFeedingFormset = inlineformset_factory(
    BtApplicationSettlement, BtApplicationSettlementFeeding,
    fields=(
        'breakfast_quantity',
        'dinner_quantity',
        'supper_quantity'),
    labels={'breakfast_quantity': 'Liczba zapewnionych śniadań',
            'dinner_quantity': 'Liczba zapewnionych obiadów',
            'supper_quantity': 'Liczba zapewnionych kolacji'},
    can_delete=False,
    # widgets=forms.IntegerField.widget(attrs={'onchange': "get_onchange_meals_correction()"})
)


class BtRejectionForm(forms.Form):
    """Rejection form"""
    application_log = forms.CharField(max_length=240,
                                      label="Przyczyna odrzucenia",
                                      widget=forms.Textarea(attrs={'rows': 5})
                                      )


class BtApprovedForm(forms.Form):
    """Approval form"""
    application_log = forms.CharField(max_length=240,
                                      label="Przyczyna odrzucenia",
                                      widget=forms.HiddenInput(),
                                      initial='approved',

                                      )
    current_datetime = forms.CharField(widget=forms.HiddenInput())
