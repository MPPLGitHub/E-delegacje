from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from setup.views import (
    BtUserListView,
    BtUserDetailView,
    BtUserCreateView,
    BtUserUpdateView,
    BtCompanyCodeListView,
    BtCompayCodeDetailView,
    BtCompanyCodeCreateView,
    BtCompanyCodeUpdateView,
    BtRegionListView,
    BtRegionDetailView,
    BtRegionUpdateView,
    BtRegionCreateView,
    BtDivisionListView,
    BtDivisionDetailView,
    BtDivisionUpdateView,
    BtDivisionCreateView,
    BtLocationListView,
    BtLocationDetailView,
    BtLocationCreateView,
    BtCostCenterListView,
    BtCostCenterDetailView,
    BtCostCenterCreateView,
    BtMileageRatesListView,
    BtMileageRatesDetailView,
    BtMileageRatesCreateView,
    BtDelegationRateListView,
    BtDelegationRateDetailView,
    BtDelegationRateCreateView,
    BtDelegationRateUpdateView,
    BtDepartmentListView,
    BtDepartmentDetailView,
    BtDepartmentCreateView,
    BtDepartmentUpdateView,
    user_login,
    user_logout,
    PasswordResetView,
    PasswordResetDoneView,
    MyPasswordChangeDoneView,
    MyPasswordChangeView,
    BtLocationFormView,
    upload,
    BtAuthorisationsCreateView,
    BtAuthorisationsListView,
    BtAuthorisationsDetailView,
    BtAuthorisationsUpdateView,
    BtAuthorisationsDeleteView,
    load_costcenters_for_new_authorisation,
    load_filtered_authorisations_context,
    load_filtered_costcenter_context,
    load_users_filtered_view,
    BtOrderCreateView,
    BtOrderDetailView,
    BtOrderListView,
    BtOrderUpdateView,
    indexsetup

#    main_login,
#    signup_view,

)
app_name = 'setup'

urlpatterns = [
    path('index/', indexsetup, name="index"),

    path('user-list-view/', BtUserListView.as_view(), name="user-list-view"),
    path('user-details-view/<pk>', BtUserDetailView.as_view(), name="user-details-view"),
    path('user-update/<pk>', BtUserUpdateView.as_view(), name="user-update"),
    path('user-create-view/', BtUserCreateView.as_view(), name="user-create"),
    path('user-list-filter-context/', load_users_filtered_view, name="user-list-filter-context"),

    path('company-code-list/',BtCompanyCodeListView.as_view(),name="companycode-list"),
    path('company-code-create/',BtCompanyCodeCreateView.as_view(),name="companycode-create"),
    path('company-code-update/<pk>',BtCompanyCodeUpdateView.as_view(),name="companycode-update"),
    path('company-code-detail/<pk>',BtCompayCodeDetailView.as_view(),name="companycode-details"),    

    path('region-list-view/', BtRegionListView.as_view(), name="region-list-view"),
    path('region-details-view/<pk>', BtRegionDetailView.as_view(), name="region-details-view"),
    path('region-update-view/<pk>', BtRegionUpdateView.as_view(), name="region-update-view"),
    path('region-create-view/', BtRegionCreateView.as_view(), name="region-create"),

    path('division-list-view/', BtDivisionListView.as_view(), name="division-list-view"),
    path('division-details-view/<pk>', BtDivisionDetailView.as_view(), name="division-details-view"),
    path('division-update-view/<pk>', BtDivisionUpdateView.as_view(), name="division-update-view"),
    path('division-create-view/', BtDivisionCreateView.as_view(), name="division-create"),

    path('location-list-view/', BtLocationListView.as_view(), name="location-list-view"),
    path('location-details-view/<pk>', BtLocationDetailView.as_view(), name="location-details-view"),
    path('location-create-view/', BtLocationCreateView.as_view(), name="location-create"),
    path('location-create-view2/', BtLocationFormView.as_view(), name="location-create2"),

    path('costcenter-list-view/', BtCostCenterListView.as_view(), name="costcenter-list-view"),
    path('costcenter-details-view/<pk>', BtCostCenterDetailView.as_view(), name="costcenter-details-view"),
    path('costcenter-create-view/', BtCostCenterCreateView.as_view(), name="costcenter-create"),
    path('costcenter-list-filter-context/', load_filtered_costcenter_context, name="costcenter-filtered-context"),

    path('mileagetate-list-view/', BtMileageRatesListView.as_view(), name="mileagetate-list-view"),
    path('mileagetate-details-view/<pk>', BtMileageRatesDetailView.as_view(), name="mileagetate-details-view"),
    path('mileagetate-create-view/', BtMileageRatesCreateView.as_view(), name="mileagetate-create"),

    path('delegationrate-list-view/', BtDelegationRateListView.as_view(), name="delegationrate-list-view"),
    path('delegationrate-details-view/<pk>', BtDelegationRateDetailView.as_view(), name="delegationrate-details-view"),
    path('delegationrate-create-view/', BtDelegationRateCreateView.as_view(), name="delegationrate-create"),
    path('delegationrate-update-view/<pk>', BtDelegationRateUpdateView.as_view(), name="delegationrate-update-view"),

    path('department-list-view/', BtDepartmentListView.as_view(), name="department-list-view"),
    path('department-details-view/<pk>', BtDepartmentDetailView.as_view(), name="department-details-view"),
    path('department-create-view/', BtDepartmentCreateView.as_view(), name="department-create"),
    path('department-update-view/<pk>', BtDepartmentUpdateView.as_view(), name="department-update-view"),

    path('order-list-view/', BtOrderListView.as_view(), name="order-list-view"),
    path('order-details-view/<pk>', BtOrderDetailView.as_view(), name="order-details-view"),
    path('order-create-view/', BtOrderCreateView.as_view(), name="order-create"),
    path('order-update-view/<pk>', BtOrderUpdateView.as_view(), name="order-update-view"),

    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('password-change/', MyPasswordChangeView.as_view(), name='password-change'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(),  name='password-reset-done'),
    path('password-change/done/', MyPasswordChangeDoneView.as_view(),  name='password-change-done'),

    path('upload/', upload, name='upload'),

    path('authorisations-list/',BtAuthorisationsListView.as_view(),name="authorisations-list"),
    path('authorisations-create/',BtAuthorisationsCreateView.as_view(),name="authorisations-create"),
    path('authorisations-update/<pk>', BtAuthorisationsUpdateView.as_view(),name="authorisations-update"),
    path('authorisations-delete/<pk>', BtAuthorisationsDeleteView.as_view(),name="authorisations-delete"),
    path('authorisations-detail/<pk>',BtAuthorisationsDetailView.as_view(),name="authorisations-details"),
    path('authorisations-load-costcenter/',load_costcenters_for_new_authorisation,name="authorisations-load-costcenters"),
    path('authorisations-list-filter-context/',load_filtered_authorisations_context,name="authorisationslist-filter-context"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
