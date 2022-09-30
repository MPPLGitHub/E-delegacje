""" Business logic for Views in e-delegacje """
import functools
import ssl
from black import T
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.views import View
import datetime
from django.contrib import messages
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django_weasyprint.utils import django_url_fetcher
from e_delegacje.tm_notifications import (
    new_application_notification, 
    approved_or_rejected_notification
    )
from e_delegacje.enums import BtApplicationStatus, BtBookingStatus, BtTaxCategory, BtCostCategory
from e_delegacje.forms import (
    BtApplicationForm,
    BtApplicationSettlementInfoForm,
    BtApplicationSettlementCostForm,
    BtApplicationSettlementMileageForm,
    BtApplicationSettlementFeedingForm,
    BtApplicationSettlementInfoFormset,
    BtApplicationSettlementFeedingFormset,
    BtRejectionForm,
    BtApprovedForm,
    BtChangeCostCategoryForm
)
from e_delegacje.models import (
    BtApplication,
    BtCompanyCode,
    BtApplicationSettlement,
    BtApplicationSettlementInfo,
    BtApplicationSettlementCost,
    BtApplicationSettlementMileage,
    BtApplicationSettlementFeeding,
)
from e_delegacje.tm_approvals import (
    bt_application_approved, 
    bt_application_rejected,  
    send_settlement_to_approver, 
    bt_settlement_rejected,
    bt_settlement_approved
)
from e_delegacje.tm_calculations import (
    settlement_cost_sum, 
    mileage_cost_sum,
    get_diet_amount_poland,
    get_diet_amount_abroad,
    diet_reconciliation_poland,
    diet_reconciliation_abroad,
    update_diet_amount
    )
from e_delegacje.tm_upload_creator import Upload
from setup.models import BtCostCenter, BtDelegationRate, BtMileageRates, BtUser, BtUserAuthorisation, BtCurrency
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import  WeasyTemplateResponse
from django.core.files.storage import FileSystemStorage
from django.db.models import Q


@login_required
def index(request):
    """main view for main site"""
    applications = BtApplication.objects.all()
    cancelled_settled = [BtApplicationStatus.canceled, BtApplicationStatus.settled]
    items_number = BtApplication.objects.filter(application_author=request.user).exclude(application_status__in=cancelled_settled).count() + \
                   BtApplication.objects.filter(target_user=request.user).exclude(
                       application_author=request.user).count()
    approval_items = BtApplication.objects.filter(
        application_status=BtApplicationStatus.in_progress.value).filter(
        target_user__manager=request.user).count() + BtApplicationSettlement.objects.filter(
        settlement_status=BtApplicationStatus.in_progress.value).count()
    return render(request, template_name='index_del.html', context={'applications': applications,
                                                                    'items_number': items_number,
                                                                    'approval_items': approval_items})


class BtApplicationCreateView(LoginRequiredMixin,View):
    """Creates new application"""
    def get(self, request):
        form = BtApplicationForm()
        form.fields['target_user'].queryset = \
            BtUser.objects.filter(department=request.user.department)
        current_datetime = ""
        return render(request,
                      template_name="form_template.html",
                      context={"form": form, 'current_datetime': current_datetime}
                      )

    def post(self, request):
        form = BtApplicationForm(request.POST)
        if form.is_valid():
            bt_company_code = form.cleaned_data['bt_company_code']
            bt_country = form.cleaned_data['bt_country']
            target_user = form.cleaned_data['target_user']
            application_author = self.request.user
            application_status = BtApplicationStatus.in_progress.value
            trip_purpose_text = form.cleaned_data['trip_purpose_text']
            CostCenter = form.cleaned_data['CostCenter']
            transport_type = form.cleaned_data['transport_type']
            travel_route = form.cleaned_data['travel_route']
            planned_start_date = form.cleaned_data['planned_start_date']
            planned_end_date = form.cleaned_data['planned_end_date']
            advance_payment = form.cleaned_data['advance_payment']
            advance_payment_currency = form.cleaned_data['advance_payment_currency']
            employee_level = BtUser.objects.get(id=target_user.id)
            current_datetime = form.cleaned_data['current_datetime']
            application_log = f'''Wniosek o delegację utworzony przez: {application_author} - {current_datetime}
                    \n-----\nSkierowany do akceptacji do: {target_user.manager.first_name} {target_user.manager.last_name}
                    '''

            BtApplication.objects.create(
                bt_company_code=bt_company_code,
                bt_country=bt_country,
                target_user=target_user,
                application_author=application_author,
                application_status=application_status,
                trip_purpose_text=trip_purpose_text,
                CostCenter=CostCenter,
                transport_type=transport_type,
                travel_route=travel_route,
                planned_start_date=planned_start_date,
                planned_end_date=planned_end_date,
                advance_payment=advance_payment,
                advance_payment_currency=advance_payment_currency,
                employee_level=employee_level,
                application_log=application_log
            )

            new_application_notification(target_user.manager.email, BtApplication.objects.last())

            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
        else:
            print(form.errors)
            form.fields['target_user'].queryset = \
                BtUser.objects.filter(department=request.user.department)
            current_datetime = ""
            return render(request,
                      template_name="form_template.html",
                      context={"form": form, 'current_datetime': current_datetime}
                      )


class BtApplicationListView(LoginRequiredMixin, ListView):
    """ List View for applications"""
    model = BtApplication
    template_name = "Application/bt_applications_list.html"
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        """Adds context data to the view"""
        context = super().get_context_data(**kwargs)

        filters = (Q(target_user=self.request.user) | Q(application_author=self.request.user))
        status_filter = (Q(application_status=BtApplicationStatus.canceled) | 
            Q(application_status=BtApplicationStatus.settled))

        current_target_users_set = \
        {item.target_user for item in BtApplication.objects.filter(filters).exclude(status_filter)}
        
        settled_cancelled_target_users_set = \
        {item.target_user for item in BtApplication.objects.filter(filters).filter(status_filter)}
        
        current_company_codes = \
            {item.bt_company_code for item in BtApplication.objects.filter(filters).exclude(status_filter)}
        
        settled_cancelled_company_codes2 = \
            {item.bt_company_code for item in BtApplication.objects.filter(filters).filter(status_filter)}

        context['company_codes1'] = current_company_codes
        context['company_codes2'] = settled_cancelled_company_codes2
        context['taget_users1'] = current_target_users_set
        context['taget_users2'] = settled_cancelled_target_users_set
        context['application_statuses'] = [BtApplicationStatus.canceled, BtApplicationStatus.settled]

        return context


class BtAllApplicationListView(BtApplicationListView):
    """ List View for applications"""
    model = BtApplication
    template_name = "Application/bt_all_applications_list.html"
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        """Add context data to the view"""
        context = super().get_context_data(**kwargs)
        target_users_set = {item.target_user for item in BtApplication.objects.all()}
        application_statuses = {item.application_status for item in BtApplication.objects.all()}

        context['all_statuses'] = application_statuses
        context['target_users'] = target_users_set
        return context


class BtApplicationDetailView(LoginRequiredMixin, DetailView):
    """ Detail View for e_delegacje application"""
    model = BtApplication
    template_name = "Application/bt_application_details.html"


class BtApplicationApprovalDetailView(LoginRequiredMixin, View):
    """ Detail view for e_delegacje application which is shown in approoval view"""
    def get(self, request, pk):

        application = BtApplication.objects.get(id=pk)
        advance = application.advance_payment
        cost_sum = 0
        mileage_cost = 0
        diet = 0
        total_costs = 0
        settlement_amount = 0
        rejected_form = BtRejectionForm()
        approved_form = BtApprovedForm()
        try:
            settlement_pk = application.bt_applications_settlements.id    
            settlement = BtApplicationSettlement.objects.get(id=settlement_pk)
            advance = float(settlement.bt_application_id.advance_payment)
            cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
                diet = diet_reconciliation_poland(settlement)
            else:
                diet = diet_reconciliation_abroad(settlement)
            total_costs = cost_sum + mileage_cost + diet
            settlement_amount = round(advance - total_costs, 2)
            if settlement_amount < 0:
                settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text} - ' \
                                    f'{abs(float(settlement_amount * settlement.bt_application_id.bt_application_settlement_info.settlement_exchange_rate))}.'
                                    
            else:
                settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text} - ' +\
                                    f'{abs(float(settlement_amount * settlement.bt_application_id.bt_application_settlement_info.settlement_exchange_rate))}.'
            return render(
                request,
                template_name="bt_application_approval.html",
                context={
                    'application': application,
                    'cost_sum': round(cost_sum, 2),
                    'total_costs': round(total_costs, 2),
                    'advance': advance,
                    'settlement_amount': settlement_amount,
                    'mileage_cost': mileage_cost,
                    'diet': diet,
                    'rejected_form': rejected_form,
                })
        except:
            return render(
                request,
                template_name="Approval/bt_application_approval.html",
                context={
                    'application': application, 
                    'cost_sum': round(cost_sum, 2),
                    'total_costs': round(total_costs, 2),
                    'advance': advance,
                    'settlement_amount': settlement_amount,
                    'mileage_cost': mileage_cost,
                    'diet': diet,
                'rejected_form': rejected_form, 
                'approved_form': approved_form})

    def post(self, request, pk):
        rejected_form = BtRejectionForm(request.POST)
        if rejected_form.is_valid():
            bt_application = BtApplication.objects.get(id=pk)
            rejection_reason = rejected_form.cleaned_data['application_log']
            try:
                settlement = BtApplicationSettlement.objects.get(id=bt_application.bt_applications_settlements.id)
                settlement.settlement_status = BtApplicationStatus.rejected.value
                settlement.save()
                bt_application.application_log = \
                    bt_application.application_log + \
                    f"\n-----\nRozliczenie odrzucone przez {request.user.first_name} " \
                    f"{request.user.last_name}.\n Powód: " \
                    f"{rejection_reason}."
                bt_application.save()
                approved_or_rejected_notification(bt_application, request.user, 
                BtApplicationStatus.rejected.label, rejection_reason)
                return HttpResponseRedirect(reverse("e_delegacje:approval-list"))
            except ObjectDoesNotExist:
                bt_application.application_status = BtApplicationStatus.rejected.value
                bt_application.application_log = bt_application.application_log + \
                                                 f"\n-----\nWniosek odrzucony przez {request.user.first_name} " \
                                                 f"{request.user.last_name}.\n Powód: " \
                                                 f"{rejection_reason}."
                bt_application.save()
                approved_or_rejected_notification(bt_application, request.user, 
                BtApplicationStatus.rejected.label, rejection_reason)
                return HttpResponseRedirect(reverse("e_delegacje:approval-list"))
                
        else:
            return HttpResponseRedirect(reverse("e_delegacje:approval", args=[pk]))
            

class BtApplicationApprovalMailDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        application = BtApplication.objects.get(id=pk)
        try:
            set_pk = application.bt_applications_settlements.id
            settlement = BtApplicationSettlement.objects.get(id=set_pk)
            advance = float(settlement.bt_application_id.advance_payment)
            cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
            if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
                diet = diet_reconciliation_poland(settlement)
            else:
                diet = diet_reconciliation_abroad(settlement)
            total_costs = cost_sum + mileage_cost + diet
            settlement_amount = round(advance - total_costs, 2)
            if settlement_amount < 0:
                settlement_amount = f'Do zwrotu dla pracownika: {abs(settlement_amount)} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.code}.'
            else:
                settlement_amount = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.code}'
            return render(
                request,
                template_name="Approval/bt_approval_mail_detail.html",
                context={
                    'application': application,
                    'cost_sum': round(cost_sum, 2),
                    'total_costs': round(total_costs, 2),
                    'advance': advance,
                    'settlement_amount': settlement_amount,
                    'mileage_cost': mileage_cost,
                    'diet': diet
                })
        except:
            return render(
                request,
                template_name="Approval/bt_approval_mail_detail.html",
                context={'application': application})


class BtApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = BtApplication
    template_name = "form_template.html"
    form_class = BtApplicationForm
    success_url = reverse_lazy("e_delegacje:applications-list")

    def post(self, request, *args, **kwargs):
        application = self.get_object()

        form = BtApplicationForm(request.POST)
        if form.is_valid():
            application.bt_country = form.cleaned_data['bt_country']
            application.target_user = form.cleaned_data['target_user']
            application.application_status = BtApplicationStatus.in_progress.value
            application.trip_purpose_text = form.cleaned_data['trip_purpose_text']
            application.CostCenter = form.cleaned_data['CostCenter']
            application.transport_type = form.cleaned_data['transport_type']
            application.travel_route = form.cleaned_data['travel_route']
            application.planned_start_date = form.cleaned_data['planned_start_date']
            application.planned_end_date = form.cleaned_data['planned_end_date']
            application.advance_payment = form.cleaned_data['advance_payment']
            application.advance_payment_currency = form.cleaned_data['advance_payment_currency']
            application.current_datetime = form.cleaned_data['current_datetime']
            application.application_log = application.application_log + \
                              f'Wniosek o delegację poprawiony przez: {request.user.first_name} ' \
                              f'{request.user.last_name} - {application.current_datetime}\n'
            application.save()
            new_application_notification(application.target_user.manager.email, application)
            

            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
        else:
            print(form.errors)
            return HttpResponseRedirect(reverse("e_delegacje:index"))


class BtApprovalListView(LoginRequiredMixin, ListView):
    model = BtApplication
    template_name = "Approval/bt_approval_list.html"
    ordering = ['-id']

    def get_queryset(self):
        return BtApplication.objects.filter(
            application_status=BtApplicationStatus.in_progress.value).filter(
            target_user__manager=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settlements'] = BtApplicationSettlement.objects.filter(
            settlement_status=BtApplicationStatus.in_progress.value).filter(
            bt_application_id__target_user__manager=self.request.user)
        return context


class BtApprovaHistorylListView(LoginRequiredMixin, ListView):
    model = BtApplication
    template_name = "Approval/bt_approval_list_history.html"
 
    def get_queryset(self):
        user_cost_center = BtUser.objects.get(id = self.request.user.id).department.cost_center
        return BtApplication.objects.filter(
            application_status=BtApplicationStatus.settled.value).filter(
            CostCenter=user_cost_center).order_by('-id')

            
# Settlement Views

class BtApplicationSettlementCreateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        bt_application = BtApplication.objects.get(id=pk)
        now = datetime.datetime.now()
        bt_start_date = bt_application.planned_start_date
        bt_end_date = bt_application.planned_end_date

        settlement = BtApplicationSettlement.objects.create(
            bt_application_id=bt_application,
            settlement_status=BtApplicationStatus.saved.value
        )
        settlement_log = f'Nowe rozliczenie wniosku nr: {settlement.bt_application_id.id} - ' \
                    f'{now}\n'
        BtApplicationSettlementFeeding.objects.create(
            bt_application_settlement=settlement,
            breakfast_quantity=0,
            dinner_quantity=0,
            supper_quantity=0
        )

        BtApplicationSettlementInfo.objects.create(
            bt_application_settlement=settlement,
            # bt_start_date=bt_start_date,
            # bt_start_time = now,
            # bt_end_date=bt_end_date,
            # bt_end_time = now,
            advance_payment = bt_application,
            settlement_exchange_rate = 1,
            diet_amount = 0,
            settlement_log = settlement_log,
        )
        bt_application.application_status = BtApplicationStatus.settlement_in_progress.value
        bt_application.save()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[settlement.id]))

    def post(self, request, pk):
        bt_application = BtApplication.objects.get(id=pk)
        now = datetime.datetime.now()
        bt_start_date = bt_application.planned_start_date
        bt_end_date = bt_application.planned_end_date

        settlement = BtApplicationSettlement.objects.create(
            bt_application_id=bt_application,
            settlement_status=BtApplicationStatus.saved.value
        )
        settlement_log = f'Nowe rozliczenie wniosku nr: {settlement.bt_application_id.id} - ' \
                    f'{now}\n'
        BtApplicationSettlementFeeding.objects.create(
            bt_application_settlement=settlement,
            breakfast_quantity=0,
            dinner_quantity=0,
            supper_quantity=0
        )
        BtApplicationSettlementInfo.objects.create(
            bt_application_settlement=1,
            bt_start_date=bt_start_date,
            bt_start_time = now,
            bt_end_date=bt_end_date,
            bt_end_time = now,
            advance_payment = bt_application,
            settlement_exchange_rate = 1,
            diet_amount = 0,
            settlement_log = settlement_log,
        )
        bt_application.application_status = BtApplicationStatus.settlement_in_progress.value
        bt_application.save()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[settlement.id]))


class BtApplicationSettlementsListView(LoginRequiredMixin, ListView):
    model = BtApplicationSettlement
    template_name = "Application/bt_applications_list.html"


class BtApplicationSettlementDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        advance = float(settlement.bt_application_id.advance_payment)
        cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        diet=float(settlement.bt_application_info.diet_amount)
        diet2=float(diet_reconciliation_poland(settlement))
        total_costs = cost_sum + mileage_cost + diet
        settlement_amount = advance - total_costs

        if settlement.bt_application_id.advance_payment_currency.code != "PLN":
            settlement_amount_curency = settlement_amount
            rate = settlement.bt_application_id.bt_application_settlement_info.settlement_exchange_rate
            settlement_amount_PLN = round(settlement_amount * float(rate),2)
            
            if settlement_amount < 0:
                settlement_amount_text = f'Do zwrotu dla pracownika: {abs(round(settlement_amount,2))} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text} ('\
                                    f'{abs(settlement_amount_PLN)}zł.).'
            else:
                settlement_amount_text = f'Do zapłaty przez pracownika: {settlement_amount} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text} ('\
                                    f'{abs(settlement_amount_PLN)}zł.).'
        else:
            if settlement_amount < 0:
                    settlement_amount_text = f'Do zwrotu dla pracownika: {abs(round(settlement_amount,2))} ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text}'\
                                    
            else:
                settlement_amount_text = f'Do zapłaty przez pracownika: {settlement_amount} - ' \
                                    f'{settlement.bt_application_id.advance_payment_currency.text}'\
                                   
 

        return render(
            request,
            template_name="Settlement/bt_settlement_details.html",
            context={'object': settlement,
                     'cost_sum': cost_sum,
                     'total_costs': total_costs,
                     'advance': advance,
                     'settlement_amount': settlement_amount_text,
                     'mileage_cost': mileage_cost,
                     'diet': diet,
                     'diet2': diet2
                     })


# Subform create Views
# Create Views
class BtApplicationSettlementInfoCreateFormView(LoginRequiredMixin, View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        application = BtApplication.objects.get(id=settlement.bt_application_id.id)
        form = BtApplicationSettlementInfoForm()
        form.initial['bt_start_date'] = application.planned_start_date
        form.initial['bt_end_date'] = application.planned_end_date
        return render(
            request,
            template_name="Settlement/settlement_subform_info.html",
            context={"form": form, 'settlement': settlement})

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementInfoForm(request.POST)

        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            if form.cleaned_data["bt_completed"] == 'nie':

                bt_application_settlement.bt_application_id.application_status = BtApplicationStatus.canceled
                bt_application_settlement.bt_application_id.save()
                bt_application_settlement.delete()
                return HttpResponseRedirect(reverse("e_delegacje:applications-list"))
            else:
                bt_completed = form.cleaned_data["bt_completed"]
                bt_start_date = form.cleaned_data["bt_start_date"]
                bt_start_time = form.cleaned_data["bt_start_time"]
                bt_end_date = form.cleaned_data["bt_end_date"]
                bt_end_time = form.cleaned_data["bt_end_time"]
                settlement_exchange_rate = form.cleaned_data['settlement_exchange_rate']
                current_datetime = form.cleaned_data["current_datetime"]
                settlement_log = f'Nowe rozliczenie wniosku nr: {bt_application_settlement.bt_application_id.id} - ' \
                                 f'{current_datetime}\n'
                advance_payment = BtApplication.objects.get(
                    id=BtApplicationSettlement.objects.get(id=pk).bt_application_id.id
                )
                if bt_application_settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
                    diet = round(diet_reconciliation_poland(bt_application_settlement), 2)
                else:
                    diet = round(diet_reconciliation_abroad(bt_application_settlement), 2)
                
                diet_amount = diet

                BtApplicationSettlementInfo.objects.create(
                    bt_application_settlement=bt_application_settlement,
                    bt_completed=bt_completed,
                    bt_start_date=bt_start_date,
                    bt_start_time=bt_start_time,
                    bt_end_date=bt_end_date,
                    bt_end_time=bt_end_time,
                    settlement_exchange_rate=settlement_exchange_rate,
                    advance_payment=advance_payment,
                    settlement_log=settlement_log,
                    diet_amount=diet_amount
                )
                return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
        else:
            return HttpResponseRedirect(reverse("e_delegacje:settlement-info-create", args=[pk]))


class BtApplicationSettlementCostCreateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementCostForm()
        currency = settlement.bt_application_id.advance_payment_currency.code
        cost_list = BtApplicationSettlementCost.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        
        return render(
            request,
            template_name="Settlement/settlement_subform_cost.html",
            context={"form": form, 'cost_list': cost_list, 'settlement': settlement, 'currency': currency})

    def post(self, request, pk, *args, **kwargs):
        category_tax_dict = {
            BtCostCategory.accommodation: BtTaxCategory.KUP, 
            BtCostCategory.consumption_invoice: BtTaxCategory.KUP,
            BtCostCategory.consumption: BtTaxCategory.KUP,
            BtCostCategory.consumption_nkup: BtTaxCategory.NKUP,
            BtCostCategory.tickets: BtTaxCategory.KUP,
            BtCostCategory.taxi: BtTaxCategory.KUP,
            BtCostCategory.taxi_nkup: BtTaxCategory.NKUP,
            BtCostCategory.parking: BtTaxCategory.KUP,
            BtCostCategory.parking_nkup: BtTaxCategory.NKUP,
            BtCostCategory.transport: BtTaxCategory.KUP,
            BtCostCategory.transport_nkup: BtTaxCategory.NKUP,
            }
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementCostForm(request.POST, request.FILES)
        cost_list = BtApplicationSettlementCost.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        uploaded_file = request.FILES.get('attachment')
        currency = settlement.bt_application_id.advance_payment_currency.code
        NKUP_cost_list = [
            BtCostCategory.transport_nkup,
            BtCostCategory.taxi_nkup,
            BtCostCategory.parking_nkup,
            BtCostCategory.consumption_nkup,
            ]

        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            bt_cost_category = form.cleaned_data["bt_cost_category"]
            bt_cost_description = form.cleaned_data["bt_cost_description"]
            bt_cost_amount = form.cleaned_data["bt_cost_amount"]
            bt_cost_currency = settlement.bt_application_id.advance_payment_currency
            bt_cost_document_date = form.cleaned_data["bt_cost_document_date"]
            bt_cost_VAT_rate = form.cleaned_data["bt_cost_VAT_rate"]
            tax_deductible = category_tax_dict[bt_cost_category]

            BtApplicationSettlementCost.objects.create(
                bt_application_settlement=bt_application_settlement,
                bt_cost_category=bt_cost_category,
                bt_cost_description=bt_cost_description,
                bt_cost_amount=bt_cost_amount,
                bt_cost_currency=bt_cost_currency,
                bt_cost_document_date=bt_cost_document_date,
                bt_cost_VAT_rate=bt_cost_VAT_rate,
                attachment=uploaded_file,
                tax_deductible=tax_deductible
            )

            return HttpResponseRedirect(reverse("e_delegacje:settlement-cost-create", args=[pk]))
        return render(request, "Settlement/settlement_subform_cost.html", {
            "form": form,
            'cost_list': cost_list,
            'settlement': settlement,
            'currency': currency
            })


class BtApplicationSettlementMileageCreateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementMileageForm()
        trip_list = BtApplicationSettlementMileage.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        return render(
            request,
            template_name="Settlement/settlement_subform_mileage.html",
            context={"form": form, 'settlement': settlement, 'trip_list': trip_list})

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementMileageForm(request.POST)
        trip_list = BtApplicationSettlementMileage.objects.filter(
            bt_application_settlement=BtApplicationSettlement.objects.get(id=pk))
        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            bt_car_reg_number = form.cleaned_data["bt_car_reg_number"]
            bt_mileage_rate = form.cleaned_data["bt_mileage_rate"]
            trip_start_place = form.cleaned_data["trip_start_place"]
            trip_date = form.cleaned_data["trip_date"]
            trip_description = form.cleaned_data["trip_description"]
            trip_purpose = form.cleaned_data["trip_purpose"]
            mileage = form.cleaned_data["mileage"]
            amount = bt_mileage_rate.rate * mileage
            BtApplicationSettlementMileage.objects.create(
                bt_application_settlement=bt_application_settlement,
                bt_car_reg_number=bt_car_reg_number,
                bt_mileage_rate=bt_mileage_rate,
                trip_start_place=trip_start_place,
                trip_date=trip_date,
                trip_description=trip_description,
                trip_purpose=trip_purpose,
                mileage=mileage,
                amount=amount
            )
            return HttpResponseRedirect(reverse("e_delegacje:settlement-mileage-create", args=[pk]))
        return render(request, "Settlement/settlement_subform_mileage.html", {"form": form, 'trip_list': trip_list})


class BtApplicationSettlementFeedingCreateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        settlement = BtApplicationSettlement.objects.get(id=pk)
        form = BtApplicationSettlementFeedingForm()
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet_rate = BtDelegationRate.objects.get(country=settlement.bt_application_id.bt_country).delagation_rate
            diet_amount = get_diet_amount_poland(settlement)  # dieta bez odliczeń
            diet = diet_reconciliation_poland(settlement)  # dieta bez odliczeń po korekcie o wyżywienie
        else:
            diet_rate = BtDelegationRate.objects.get(country=settlement.bt_application_id.bt_country).delagation_rate
            diet_amount = get_diet_amount_abroad(settlement)  # dieta bez odliczeń
            diet = diet_reconciliation_poland(settlement)  # dieta bez odliczeń po korekcie o wyżywienie
        
        return render(
            request,
            template_name="Settlement/settlement_subform_feeding.html",
            context={"form": form,
                     'settlement': settlement,
                     'diet': diet,
                     'diet_amount': diet_amount,
                     'diet_rate': diet_rate
                     }
        )

    def post(self, request, pk, *args, **kwargs):
        form = BtApplicationSettlementFeedingForm(request.POST)

        if form.is_valid():
            bt_application_settlement = BtApplicationSettlement.objects.get(id=pk)
            breakfast_quantity = form.cleaned_data["breakfast_quantity"]
            dinner_quantity = form.cleaned_data["dinner_quantity"]
            supper_quantity = form.cleaned_data["supper_quantity"]
            BtApplicationSettlementFeeding.objects.create(
                bt_application_settlement=bt_application_settlement,
                breakfast_quantity=breakfast_quantity,
                dinner_quantity=dinner_quantity,
                supper_quantity=supper_quantity
            )
            
            return HttpResponseRedirect(reverse("e_delegacje:settlement-details", args=[pk]))
        return render(request, "Settlement/settlement_subform_feeding.html", {"form": form})




# Delete Views
class BtApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = BtApplication
    template_name = "Application/bt_application_delete.html"
    success_url = reverse_lazy("e_delegacje:applications-list")


class BtApplicationSettlementCostDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        item_to_be_deleted = BtApplicationSettlementCost.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.get(id=item_to_be_deleted.bt_application_settlement.id)
        item_to_be_deleted.delete()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-cost-create", args=[settlement.id]))


class BtApplicationSettlementMileageDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        item_to_be_deleted = BtApplicationSettlementMileage.objects.get(id=pk)
        settlement = BtApplicationSettlement.objects.get(id=item_to_be_deleted.bt_application_settlement.id)
        item_to_be_deleted.delete()
        return HttpResponseRedirect(reverse("e_delegacje:settlement-mileage-create", args=[settlement.id]))


# UpdateViews
class BtApplicationSettlementInfoUpdateView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = BtApplicationSettlementInfo
    template_name = "Settlement/settlement_subform_info.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())

        result = self.get_form().cleaned_data
        bt_completed = result[0]['bt_completed']
        if bt_completed == 'nie':
            self.object.bt_application_id.application_status = BtApplicationStatus.canceled
            self.object.bt_application_id.save()
            self.object.delete()
            return HttpResponseRedirect(reverse("e_delegacje:applications-list"))

        else:
            return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return BtApplicationSettlementInfoFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Zmiany zostąły zapisane"
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        settlement_id = self.object.bt_application_info.id
        return reverse("e_delegacje:settlement-diet-update", kwargs={'pk': settlement_id})


class BtDietAmountUpdate(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        settlement_info = BtApplicationSettlementInfo.objects.get(id=pk)
        diet_amount = update_diet_amount(settlement_info.bt_application_settlement)
        settlement_info.diet_amount = diet_amount
        settlement_info.save()
        
        return HttpResponseRedirect(reverse(
            "e_delegacje:settlement-details", 
            args=[settlement_info.bt_application_settlement.id]))

    def post(self, request, pk):
        settlement_info = BtApplicationSettlementInfo.objects.get(id=pk)
        diet_amount = update_diet_amount(settlement_info.bt_application_settlement)
        print(diet_amount)
        settlement_info.diet_amount = diet_amount
        settlement_info.save()
        
        return HttpResponseRedirect(reverse(
            "e_delegacje:settlement-details", 
            args=[settlement_info.bt_application_settlement.id]))

        
class BtApplicationSettlementFeedingUpdateView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = BtApplicationSettlementFeeding
    template_name = "Settlement/settlement_subform_feeding.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=BtApplicationSettlement.objects.all())

        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return BtApplicationSettlementFeedingFormset(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        settlement_id = self.object.bt_application_info.id
        return reverse("e_delegacje:settlement-diet-update", kwargs={'pk': settlement_id})
        # return reverse("e_delegacje:settlement-details", kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settlement = BtApplicationSettlement.objects.get(id=self.object.id)
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet = round(diet_reconciliation_poland(settlement), 2)
        else:
            diet = round(diet_reconciliation_abroad(settlement), 2)

        context['settlement'] = settlement
        context['diet_amount'] = diet
        
        return context


class CreatePDF(LoginRequiredMixin, DetailView):
    model = BtApplication
    template_name = 'PDF.html'
    target = '_blank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_object()
        settlement = BtApplicationSettlement.objects.get(id=application.bt_applications_settlements.id)
        advance = float(application.advance_payment)
        cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            diet = round(diet_reconciliation_poland(settlement), 2)
        else:
            diet = round(diet_reconciliation_abroad(settlement), 2)
        total_costs = cost_sum + mileage_cost + diet
        settlement_amount = advance - total_costs
        if settlement_amount < 0:
            settlement_amount = f'Do zwrotu dla pracownika: {abs(round(settlement_amount, 4))} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'
        else:
            settlement_amount = f'Do zapłaty przez pracownika: {round(settlement_amount, 4)} ' \
                                f'{settlement.bt_application_id.advance_payment_currency.code}'

        context['settlement_amount'] = settlement_amount
        context['cost_sum'] = cost_sum
        context['total_costs'] = total_costs
        context['diet'] = diet
        context['mileage_cost'] = mileage_cost

        return context


def render_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    get_object_or_404(BtApplication, pk=pk)
    application = get_object_or_404(BtApplication, pk=pk)
    settlement = BtApplicationSettlement.objects.get(id=application.bt_applications_settlements.id)
    advance = float(application.advance_payment)
    cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
    mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
    if settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
        diet = round(diet_reconciliation_poland(settlement), 2)
    else:
        diet = round(diet_reconciliation_abroad(settlement), 2)
    total_costs = cost_sum + mileage_cost + diet
    settlement_amount = advance - total_costs
    if settlement_amount < 0:
        settlement_amount = f'Do zwrotu dla pracownika: {abs(round(settlement_amount, 4))} ' \
                            f'{settlement.bt_application_id.advance_payment_currency.code}'
    else:
        settlement_amount = f'Do zapłaty przez pracownika: {round(settlement_amount, 4)} ' \
                            f'{settlement.bt_application_id.advance_payment_currency.code}'
    context = {'object': application,
               'settlement_amount': settlement_amount,
               'cost_sum': cost_sum,
               'total_costs': total_costs,
               'diet': diet,
               'mileage_cost': mileage_cost
               }

    template_path = 'PDF.html'

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download get this code
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display get this code
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class CustomWeasyTemplateResponse(LoginRequiredMixin, WeasyTemplateResponse):
    # customized response class to change the default URL fetcher
    def get_url_fetcher(self):
        # disable host and certificate check
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return functools.partial(django_url_fetcher, ssl_context=context)


class PrintInLinePDFView(WeasyTemplateResponseMixin, CreatePDF):
    # output of MyModelView rendered as PDF with hardcoded CSS
    pdf_stylesheets = [
        # settings.STATIC_ROOT + '/css/bootstrap.css',
        settings.STATICFILES_DIRS[0] + '/css/bootstrap.css',
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = False

    response_class = CustomWeasyTemplateResponse

    def get_pdf_filename(self):
        obj = CreatePDF.get_object(self)
        return f'Rozliczenie delegacji nr: {obj.id}.pdf'


class DownloadPDFView(WeasyTemplateResponseMixin, CreatePDF):
    # suggested filename (is required for attachment/download!)
    pdf_stylesheets = [
        # settings.STATIC_ROOT + '/css/bootstrap.css',
        settings.STATICFILES_DIRS[0] + '/css/bootstrap.css',
    ]
    # show pdf in-line (default: True, show download dialog)
    pdf_attachment = True
    # custom response class to configure url-fetcher
    response_class = CustomWeasyTemplateResponse

    def get_pdf_filename(self):
        obj = CreatePDF.get_object(self)
        return f'Rozliczenie delegacji nr: {obj.id}.pdf'


def load_company_codes(request):
    """Takes target_user id from request.
        Filters Company codes queryset to.  
        returns objects that the user has authorisation to and passes context data to a view.
    """
    target_user = request.GET.get('id_target_user')
    company_codes = \
        [company_code for company_code in BtUser.objects.get(id=target_user).company_code.all()]
    return render(request, 'Company_code/company_codes_list_options.html', {'company_codes': company_codes})


def load_costcenters(request):
    """Takes target_user_id and Company_code_id from request.
        Filters Cost center queryset.
        returns filtered objects to context data.
    """
    target_user = request.GET.get('id_target_user')
    company_code = request.GET.get('company_code')
    cost_centers = \
        [authorisation.cost_center for authorisation in \
        BtUserAuthorisation.objects.filter(user_id=target_user).filter(company_code=company_code)]
    return render(request, 'Cost_center/cost_centers_list_options.html', {'cost_centers': cost_centers})


def load_settled_cancelled_filter(request):
    """Takes company_code, target_user id, application_ststus from request.
        Filters settled_cancelled table queryset.
        returns filtered objects to context data.
    """
    applications = BtApplication.objects.all()

    target_user = request.GET.get('target_user')
    c_code = request.GET.get('c_code')
    application_status = request.GET.get('application_status')
    if target_user:   
        applications = applications.filter(target_user=target_user)
        
    if c_code:
        applications = applications.filter(bt_company_code=c_code)
    
    if application_status:
        
        applications = applications.filter(application_status=application_status)
        

    return render(request, 'Application/bt_applications_filtered.html', 
    {'applications': applications.order_by('-id')})


def load_current_filter(request):
    """Takes company_code, target_user id from request.
        Filters current applications table queryset.
        returns filtered objects to context data.
    """
    applications = BtApplication.objects.all()

    target_user = request.GET.get('target_user')
    c_code = request.GET.get('c_code')

    if target_user:   
        applications = applications.filter(target_user=target_user)
        
    if c_code:
        applications = applications.filter(bt_company_code=c_code)      

    return render(request, 'Application/bt_current_applications_filtered.html', 
    {'current_applications': applications.order_by('-id')})


def load_all_applications_filter(request):
    """Takes company_code, target_user id, start_date and end_date from request.
        Filters all_applications table queryset.
        returns filtered objects to context data.
    """
    applications = BtApplication.objects.all()

    target_user = request.GET.get('target_user')
    c_code = request.GET.get('c_code')
    start_date = request.GET.get('start_date')
    filter_start_date = \
        ((Q(bt_applications_settlements__bt_application_info__bt_start_date__lte=start_date) &
                Q(bt_applications_settlements__bt_application_info__bt_end_date__gte=start_date)) |
        (Q(planned_start_date__lte=start_date) &
                Q(planned_end_date__gte=start_date)))
    
    if target_user:   
        applications = applications.filter(target_user=target_user)
        
    if c_code:
        applications = applications.filter(bt_company_code=c_code)
    
    if start_date:
        applications = applications.filter(filter_start_date)
    
    return render(request, 'Application/bt_all_applications_filtered.html', 
    {'applications': applications.order_by('-id')})


class ApplicationsToBeBooked(BtApplicationListView):
    """ List View for approved applications"""
    model = BtApplication
    template_name = "CreateCSV/bt_applications_to_be_booked_list.html"
    

    def get_context_data(self, **kwargs):
        """Add context data to the view filters only settled applications"""
        context = super().get_context_data(**kwargs)
        settled_applications = BtApplication.objects.filter(
            application_status='settled').filter(
                booked=None).order_by('-id')
        booked_application = BtApplication.objects.filter(
                booked__isnull=False).order_by('-id')
        target_users_set = {item.target_user for item in BtApplication.objects.all()}
        application_statuses = {item.application_status for item in BtApplication.objects.all()}

        context['all_statuses'] = application_statuses
        context['target_users'] = target_users_set
        context['settled_applications'] = settled_applications
        context['booked_application'] = booked_application
        return context


def load_applications_to_be_booked_filter(request):
    """Takes company_code, target_user id, start_date and end_date from request.
        Filters applications_to_be_booked table queryset.
        returns filtered objects to context data.
    """
    applications = BtApplication.objects.all()

    target_user = request.GET.get('target_user')
    c_code = request.GET.get('c_code')
    if target_user:   
        applications = applications.filter(target_user=target_user)
        
    if c_code:
        applications = applications.filter(bt_company_code=c_code)
    
    return render(request, 'Application/bt_applications_to_be_booked_filtered.html', 
    {'applications': applications.order_by('-id')})


class ApplicationToBeBookedDetails(DetailView):
    model = BtApplicationSettlement
    template_name = "CreateCSV/bt_application_to_be_booked_details.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settlement = BtApplicationSettlement.objects.get(id=self.object.id)
        cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=settlement.id)))
        diet=float(settlement.bt_application_info.diet_amount)
        total_costs = cost_sum + mileage_cost + diet
        upload =  Upload(settlement)
        file_name = upload.file_name
        csv_file = upload.read_upload_file()
        invoice_required_cost_categories = [
            BtCostCategory.accommodation, 
            BtCostCategory.consumption_invoice,
            BtCostCategory.taxi,
            BtCostCategory.parking,
            BtCostCategory.transport,
            ]

        context['total_costs'] = total_costs
        context['mileage_cost'] = mileage_cost
        context['cost_sum'] = cost_sum
        context['csv_file'] = csv_file
        context['file_name'] = file_name
        context['invoice_required_cost_categories'] = invoice_required_cost_categories
       
        return context

class CostCategoryUpdateView(UpdateView):
    model= BtApplicationSettlementCost
    template_name = 'CreateCSV/bt_application_to_be_booked_update_cost.html'
    fields = ['bt_cost_category']


    def get_form(self, form_class=None):
        return BtChangeCostCategoryForm()
        

    def post(self, request, *args, **kwargs):
        category_tax_dict = {
            BtCostCategory.accommodation: BtTaxCategory.KUP, 
            BtCostCategory.consumption_invoice: BtTaxCategory.KUP,
            BtCostCategory.consumption: BtTaxCategory.KUP,
            BtCostCategory.consumption_nkup: BtTaxCategory.NKUP,
            BtCostCategory.tickets: BtTaxCategory.KUP,
            BtCostCategory.taxi: BtTaxCategory.KUP,
            BtCostCategory.taxi_nkup: BtTaxCategory.NKUP,
            BtCostCategory.parking: BtTaxCategory.KUP,
            BtCostCategory.parking_nkup: BtTaxCategory.NKUP,
            BtCostCategory.transport: BtTaxCategory.KUP,
            BtCostCategory.transport_nkup: BtTaxCategory.NKUP,
            }
        cost = self.get_object()
        settlement_id = cost.bt_application_settlement.id
        form = BtChangeCostCategoryForm(request.POST)
        if form.is_valid():
            cost.bt_cost_category = form.cleaned_data['bt_cost_category']
            cost.tax_deductible = category_tax_dict[cost.bt_cost_category]
            cost.save()

        return HttpResponseRedirect(reverse("e_delegacje:create-csv-ht",
                args=[settlement_id]))
  
class CreateCSVview(LoginRequiredMixin,View):
    """View for accounting department for updateing all necessary data to prepare 
    CSV upload to SAP system"""
    def get(self, request):

        return render(request,
                      template_name="form_template.html",
                      context={}
                      )
