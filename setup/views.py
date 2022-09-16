from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView, PasswordResetView
from django.contrib import messages
from setup.forms import LoginForm, BtUserCreationForm, LocationForm, BtUserUpdateForm, AuthorisationForm
from django.shortcuts import render, redirect
from django.db.models import Q
from setup.models import (
    BtUser,
    BtCompanyCode,
    BtRegion,
    BtDivision,
    BtLocation,
    BtCostCenter,
    BtMileageRates,
    BtDelegationRate,
    BtDepartment,
    BtUserAuthorisation,
    BtOrder,
    BtGLAccounts
)
import json
from django.contrib.auth.decorators import login_required


@login_required
def indexsetup(request):
    """main view for main site in setup"""
    return render(request, template_name='index_setup.html')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():

            user = form.get_user()
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('e_delegacje:index'))
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                print(f'user {form.cleaned_data["username"]} is none')
        else:
            for item in form.errors:
                print(f'form errors: {item}')
    else:

        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
#    messages.info(request, "logged successfylly!")
    return redirect('setup:login')


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'password_change-form.html'
    success_url = reverse_lazy('setup:password-change-done')


class PasswordResetView(PasswordResetView):
    template_name = 'reset_password.html'
    success_url = reverse_lazy('setup:password-reset-done')


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class MyPasswordChangeDoneView(PasswordResetDoneView):
    template_name = 'password_change_done.html'


class BtUserCreateView(LoginRequiredMixin, CreateView):
    model = BtUser
    template_name = "my_name.html"
    form_class = BtUserCreationForm
    success_url = reverse_lazy("setup:user-list-view")


class BtUserUpdateView(LoginRequiredMixin, UpdateView):
    model = BtUser
    template_name = "my_name.html"
    form_class = BtUserUpdateForm
    success_url = reverse_lazy("setup:user-list-view")


class BtUserListView(LoginRequiredMixin, ListView):
    model = BtUser
    template_name = "user_list_view.html"

    def get_queryset(self):
        return BtUser.objects.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        managers = {user.manager for user in BtUser.objects.all()}
        context['managers'] = managers
        context['c_codes'] = BtCompanyCode.objects.all()
        return context


class BtUserDetailView(LoginRequiredMixin, DetailView):
    model = BtUser
    template_name = "user_details.html"


class BtCompanyCodeListView(LoginRequiredMixin, ListView):
    model = BtCompanyCode
    template_name = "Company_code/company_code_list_view.html"


class BtCompayCodeDetailView(LoginRequiredMixin, DetailView):
    model = BtCompanyCode
    template_name = "Company_code/companycode_details_view.html"


class BtCompanyCodeUpdateView(LoginRequiredMixin, UpdateView):
    model = BtCompanyCode
    fields = "__all__"
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:companycode-list")


class BtCompanyCodeCreateView(LoginRequiredMixin, CreateView):
    model = BtCompanyCode
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:companycode-list")


class BtRegionListView(LoginRequiredMixin, ListView):
    model = BtRegion
    template_name = "Region/region_list_view.html"


class BtRegionDetailView(LoginRequiredMixin, DetailView):
    model = BtRegion
    template_name = "Region/region_details_view.html"


class BtRegionUpdateView(LoginRequiredMixin, UpdateView):
    model = BtRegion
    fields = ("name", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:region-list-view")


class BtRegionCreateView(LoginRequiredMixin, CreateView):
    model = BtRegion
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:region-create")


class BtDivisionListView(LoginRequiredMixin, ListView):
    model = BtDivision
    template_name = "Division/division_list_view.html"


class BtDivisionDetailView(LoginRequiredMixin, DetailView):
    model = BtDivision
    template_name = "Division/division_details_view.html"


class BtDivisionUpdateView(LoginRequiredMixin, UpdateView):
    model = BtDivision
    fields = ("name", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:division-list-view")


class BtDivisionCreateView(LoginRequiredMixin, CreateView):
    model = BtDivision
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:division-create")
class BtLocationListView(LoginRequiredMixin, ListView):
    model = BtLocation
    template_name = "Location/location_list_view.html"


class BtLocationCreateView(LoginRequiredMixin, CreateView):
    model = BtLocation
    template_name = "my_name.html"
    form_class = LocationForm
    success_url = reverse_lazy("setup:location-create")

class BtLocationFormView(LoginRequiredMixin, FormView):
    model = BtLocation
    template_name = "my_name.html"
    form_class = LocationForm
    success_url = reverse_lazy("setup:location-create2")

    def form_valid(self, form):
        result = super().form_valid(form)
        profit_center = form.cleaned_data["profit_center"]
        BtLocation.objects.create(profit_center=profit_center)
        return result

    def form_invalid(self, form):
        return super().form_invalid(form)


class BtLocationDetailView(LoginRequiredMixin, DetailView):
    model = BtLocation
    template_name = "Location/location_details_view.html"


class BtCostCenterListView(LoginRequiredMixin, ListView):
    model = BtCostCenter
    template_name = "Cost_center/costcenter_list_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profit_center_set = {cost_center.profit_center_id for cost_center in BtCostCenter.objects.all()}
        context['profit_centers'] = profit_center_set
        context['c_codes'] = BtCompanyCode.objects.all()
        return context


class BtCostCenterDetailView(LoginRequiredMixin, DetailView):
    model = BtCostCenter
    template_name = "Cost_center/costcenter_details_view.html"


class BtCostCenterCreateView(LoginRequiredMixin, CreateView):
    model = BtCostCenter
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:costcenter-create")


class BtMileageRatesListView(LoginRequiredMixin, ListView):
    model = BtMileageRates
    template_name = "Mileage_rate/mileagetate_list_view.html"


class BtMileageRatesDetailView(LoginRequiredMixin, DetailView):
    model = BtMileageRates
    template_name = "Mileage_rate/mileagetate_details_view.html"


class BtMileageRatesCreateView(LoginRequiredMixin, CreateView):
    model = BtMileageRates
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:mileagetate-create")


class BtDelegationRateListView(LoginRequiredMixin, ListView):
    model = BtDelegationRate
    template_name = "Delegation_rate/delegationrate_list_view.html"


class BtDelegationRateDetailView(LoginRequiredMixin, DetailView):
    model = BtDelegationRate
    template_name = "Delegation_rate/delegationrate_details_view.html"


class BtDelegationRateCreateView(LoginRequiredMixin, CreateView):
    model = BtDelegationRate
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:delegationrate-create")


class BtDelegationRateUpdateView(LoginRequiredMixin, UpdateView):
    model = BtDelegationRate
    fields = ("delegation_rate","alpha_code", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:delegationrate-list-view")


class BtDepartmentListView(LoginRequiredMixin, ListView):
    model = BtDepartment
    template_name = "Department/department_list_view.html"


class BtDepartmentDetailView(LoginRequiredMixin, DetailView):
    model = BtDepartment
    template_name = "Department/department_details_view.html"


class BtDepartmentCreateView(LoginRequiredMixin, CreateView):
    model = BtDepartment
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:department-create")


class BtDepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = BtDepartment
    fields = ("name", )
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:department-list-view")


def upload(request):
    if request.method == "POST":
        uploaded_files = request.FILES['document']
        print(uploaded_files.name)
        print(uploaded_files.size)
    return render(request, 'upload.html')


class BtAuthorisationsListView(LoginRequiredMixin, ListView):
    model = BtUserAuthorisation
    template_name = "Authorisation/authorisations_list_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users_set = {user.user_id for user in BtUserAuthorisation.objects.all()}
        context['users'] = users_set
        context['c_codes'] = BtCompanyCode.objects.all()
        return context


class BtAuthorisationsDetailView(LoginRequiredMixin, DetailView):
    model = BtUserAuthorisation
    template_name = "Authorisation/authorisations_details_view.html"


class BtAuthorisationsDeleteView(LoginRequiredMixin, DeleteView):
    model = BtUserAuthorisation
    template_name = "Authorisation/Authorisation_delete.html"
    success_url = reverse_lazy("setup:authorisations-list")


class BtAuthorisationsUpdateView(LoginRequiredMixin, UpdateView):
    model = BtUserAuthorisation
    form_class = AuthorisationForm
    template_name = "Authorisation/Authorisations_form.html"
    success_url = reverse_lazy("setup:authorisations-list")


class BtAuthorisationsCreateView(LoginRequiredMixin, CreateView):
    model = BtUserAuthorisation
    form_class = AuthorisationForm
    template_name = "Authorisation/Authorisations_form.html"
    success_url = reverse_lazy("setup:authorisations-create")


def load_costcenters_for_new_authorisation(request):
    """Takes Company_code_id from request.
        Filters Costcenter queryset.
        returns filtered objects to context data.
    """
    company_code = request.GET.get('company_code')
    cost_centers = \
        [costcenter for costcenter in \
        BtCostCenter.objects.filter(company_code=company_code)]
    return render(request, 'Cost_center/cost_centers_list_options.html', {'cost_centers': cost_centers})


def load_filtered_authorisations_context(request):
    """Takes argues from request.
        Filters BtUserAuthorisations queryset.
        returns filtered objects to context data.
    """
    authorisations = BtUserAuthorisation.objects.all()
    original_query = authorisations
    user = request.GET.get('user')
    if user:
        authorisations = authorisations.filter(user_id=user)
        original_query = authorisations
 
    c_code = request.GET.get('c_code')
    if c_code:
        authorisations = authorisations.filter(company_code=c_code)
        original_query = authorisations

    c_center = request.GET.get('c_center')
    if c_center:
        lookups = Q(cost_center__text__icontains=c_center) | Q(cost_center__cost_center_number__icontains=c_center)
        authorisations = authorisations.filter(lookups)
    else:
        authorisations = original_query

    return render(request, 'Authorisation/filtered_authorisation_list.html', {'authorisations': authorisations})


def load_filtered_costcenter_context(request):
    """Takes argues from request.
        Filters BtCostCenter queryset.
        returns filtered objects to context data.
    """
    Cost_centers = BtCostCenter.objects.all()
    original_query = Cost_centers

    p_center = request.GET.get('p_center')
    if p_center:
        Cost_centers = Cost_centers.filter(profit_center_id=p_center)
        original_query = Cost_centers
 
    c_code = request.GET.get('c_code')
    if c_code:
        Cost_centers = Cost_centers.filter(company_code=c_code)
        original_query = Cost_centers

    c_center = request.GET.get('c_center')
    if c_center:
        Cost_centers = Cost_centers.filter(cost_center_number__icontains=c_center)
        original_query = Cost_centers
    else:
        Cost_centers = original_query
    text = request.GET.get('text')
    if text:
        Cost_centers = Cost_centers.filter(text__icontains=text)
        original_query = Cost_centers
    else:
        Cost_centers = original_query
   
    return render(request, 'Cost_center/costcenter_filtered_list.html', {'filtered_cost_centers': Cost_centers})


def load_users_filtered_view(request):
    """Takes argues from request.
        Filters BtUser queryset.
        returns filtered objects to context data.
    """
    users = BtUser.objects.all()
    original_query = users
    
    name = request.GET.get('name')
    
    if name:
        lookups = Q(first_name__icontains=name) | Q(last_name__icontains=name)
        users = users.filter(lookups)
        original_query = users
        print(users, end="/n")
        print(" -----------------")
    else:
        users = original_query
    
    c_code = request.GET.get('c_code')
    if c_code:
        users = users.filter(company_code=c_code)
        original_query = users
    
    manager = request.GET.get('manager')
    if manager:
        users = users.filter(manager=manager)
        original_query = users
    
    department = request.GET.get('department')
    if department:
        users = users.filter(department__name__icontains=department)
        original_query = users
    else:
        users = original_query

    vendor = request.GET.get('vendor')
    if vendor:
        users = users.filter(vendor_id__icontains=vendor)
        original_query = users
    else:
        users = original_query

    return render(request, 'user_filtered_list_view.html', {'filtered_users': users})


class BtOrderListView(LoginRequiredMixin, ListView):
    model = BtOrder
    template_name = "Order/order_list_view.html"


class BtOrderDetailView(LoginRequiredMixin, DetailView):
    model = BtOrder
    template_name = "Order/order_details_view.html"


class BtOrderCreateView(LoginRequiredMixin, CreateView):
    model = BtOrder
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:order-list-view")


class BtOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = BtOrder
    fields = ("name", "order", "cost_center")
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:order-list-view")


class BtGlAccountListView(LoginRequiredMixin, ListView):
    model = BtGLAccounts
    template_name = "GL_Account/GL_account_list_view.html"
    
    def get_queryset(self):
        return BtGLAccounts.objects.order_by('id')


class BtGlAccountDetailView(LoginRequiredMixin, DetailView):
    model = BtGLAccounts
    template_name = "GL_Account/GL_account_details_view.html"


class BtGlAccountCreateView(LoginRequiredMixin, CreateView):
    model = BtGLAccounts
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:gl_account-list-view")


class BtGlAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BtGLAccounts
    fields = "__all__"
    template_name = "my_name.html"
    success_url = reverse_lazy("setup:gl_account-list-view")