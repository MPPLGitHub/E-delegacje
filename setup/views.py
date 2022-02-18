from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from django.contrib import messages
from setup.forms import LoginForm, BtUserCreationForm, LocationForm
from django.shortcuts import render, redirect
from setup.models import (
    BtUser,
    BtRegion,
    BtDivision,
    BtLocation,
    BtCostCenter,
    BtMileageRates,
    BtDelegationRate,
    BtDepartment,

)


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


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_change_done.html'


class BtUserCreateView(LoginRequiredMixin, CreateView):
    model = BtUser
    template_name = "my_name.html"
    form_class = BtUserCreationForm
    # fields = "__all__"
    success_url = reverse_lazy("setup:user-list-view")


class BtUserListView(LoginRequiredMixin, ListView):
    model = BtUser
    template_name = "user_list_view.html"


class BtUserDetailView(LoginRequiredMixin, DetailView):
    model = BtUser
    template_name = "user_details.html"


class BtRegionListView(LoginRequiredMixin, ListView):
    model = BtRegion
    template_name = "region_list_view.html"


class BtRegionDetailView(LoginRequiredMixin, DetailView):
    model = BtRegion
    template_name = "region_details_view.html"


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
    template_name = "division_list_view.html"


class BtDivisionDetailView(LoginRequiredMixin, DetailView):
    model = BtDivision
    template_name = "division_details_view.html"


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
    template_name = "location_list_view.html"


class BtLocationCreateView(LoginRequiredMixin, CreateView):
    model = BtLocation
    template_name = "my_name.html"
    form_class = LocationForm
#    fields = "__all__"
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
        # profit_center = form.cleaned_data["profit_center"]
        # if BtLocation.objects.get(profit_center=result['profit_center']) is not None:
        #     self.add_error('profit_center', f'Taki Profit Center juz istnieje {result["profit_center"]}')
        # BtLocation.objects.create(profit_center=profit_center)
        # return result

    #         if result['profit_center'] == BtLocation.objects.get['profit_center']:
    #             raise ValidationError("cosssss!")
    #     if BtLocation.objects.get(profit_center=result['profit_center']) is not None:
    #         self.add_error('profit_center', f'Taki Profit Center juz istnieje {result["profit_center"]}')
    #            return result
    #    return result



class BtLocationDetailView(LoginRequiredMixin, DetailView):
    model = BtLocation
    template_name = "location_details_view.html"


class BtCostCenterListView(LoginRequiredMixin, ListView):
    model = BtCostCenter
    template_name = "costcenter_list_view.html"


class BtCostCenterDetailView(LoginRequiredMixin, DetailView):
    model = BtCostCenter
    template_name = "costcenter_details_view.html"


class BtCostCenterCreateView(LoginRequiredMixin, CreateView):
    model = BtCostCenter
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:costcenter-create")


class BtMileageRatesListView(LoginRequiredMixin, ListView):
    model = BtMileageRates
    template_name = "mileagetate_list_view.html"


class BtMileageRatesDetailView(LoginRequiredMixin, DetailView):
    model = BtMileageRates
    template_name = "mileagetate_details_view.html"


class BtMileageRatesCreateView(LoginRequiredMixin, CreateView):
    model = BtMileageRates
    template_name = "my_name.html"
    fields = "__all__"
    success_url = reverse_lazy("setup:mileagetate-create")


class BtDelegationRateListView(LoginRequiredMixin, ListView):
    model = BtDelegationRate
    template_name = "delegationrate_list_view.html"


class BtDelegationRateDetailView(LoginRequiredMixin, DetailView):
    model = BtDelegationRate
    template_name = "delegationrate_details_view.html"


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
    template_name = "department_list_view.html"


class BtDepartmentDetailView(LoginRequiredMixin, DetailView):
    model = BtDepartment
    template_name = "department_details_view.html"


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