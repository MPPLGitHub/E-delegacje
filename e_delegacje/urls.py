""" List of urlpatterns for app_name = e_delegacje. """
from django.urls import path
from e_delegacje.views import (
    index,
    BtApplicationCreateView,
    BtApplicationListView,
    BtApplicationDetailView,
    BtApplicationDeleteView,
    BtApplicationSettlementCreateView,
    BtApplicationSettlementsListView,
    BtApplicationSettlementDetailView,
    BtApplicationSettlementMileageCreateView,
    BtApplicationSettlementCostCreateView,
    BtApplicationSettlementFeedingCreateView,
    BtApplicationSettlementInfoCreateFormView,
    BtApplicationSettlementCostDeleteView,
    BtApplicationSettlementInfoUpdateView,
    BtApplicationSettlementMileageDeleteView,
    BtApplicationApprovalDetailView,
    BtApprovalListView,
    BtApplicationSettlementFeedingUpdateView,
    bt_application_approved,
    bt_application_rejected,
    BtApplicationUpdateView,
    send_settlement_to_approver,
    bt_settlement_approved,
    bt_settlement_rejected,
    BtApplicationApprovalMailDetailView,
    CreatePDF,
    render_pdf_view,
    PrintInLinePDFView,
    DownloadPDFView,
    load_costcenters,
    load_company_codes,
    load_settled_cancelled_filter,
    load_current_filter,
    load_all_applications_filter,
    BtAllApplicationListView
)

app_name = 'e_delegacje'
urlpatterns = [

    path('', index, name='index'),

    # BtApplicatons - wnioski o delegacje
    path('applications-create/', BtApplicationCreateView.as_view(), name='applications-create'),
    path('applications-list', BtApplicationListView.as_view(), name='applications-list'),
    path('applications-all-list', BtAllApplicationListView.as_view(), name='applications-all-list'),
    path('application-details/<pk>', BtApplicationDetailView.as_view(), name='application-details'),
    path('application-delete/<pk>', BtApplicationDeleteView.as_view(), name='application-delete'),
    path('application-update/<pk>', BtApplicationUpdateView.as_view(), name='application-update'),
    path('application-create-pdf/<pk>', CreatePDF.as_view(), name='application-create-pdf'),
    path('application-render-pdf/<pk>', render_pdf_view, name='application-render-pdf'),
    path('application-pdf/<pk>', PrintInLinePDFView.as_view(), name='application-pdf'),
    path('application-inline-pdf/<pk>', PrintInLinePDFView.as_view(), name='pdf-in-line'),
    path('application-download-pdf/<pk>', DownloadPDFView.as_view(), name='pdf-download'),
    path('load-cost-centers/', load_costcenters, name='load-costcenters'),
    path('load-company-codes/', load_company_codes, name='load-company-codes'),
    path('settled_cancelled-applications-filter/', load_settled_cancelled_filter, 
                                name='settled_cancelled-applications-filter'),
    path('current-applications-filter/', load_current_filter, name='current-applications-filter'),
    path('all-applications-filter/', load_all_applications_filter, name='all-applications-filter'),


    # BtApplicatons - wnioski o rozliczenie delegacji
    path('settlement-create/<pk>', BtApplicationSettlementCreateView.as_view(), name='settlement-create'),
    path('settlements-list', BtApplicationSettlementsListView.as_view(), name='settlements-list'),
    path('settlement-details/<pk>', BtApplicationSettlementDetailView.as_view(), name='settlement-details'),
    path('settlement-send/<pk>', send_settlement_to_approver, name='settlement-send'),

    # Approvals
    path('approve/<pk>', BtApplicationApprovalDetailView.as_view(), name='approval'),
    path('approval-list', BtApprovalListView.as_view(), name='approval-list'),
    path('application-approved/<pk>', bt_application_approved, name='application-approved'),
    path('application-rejected/<pk>', bt_application_rejected, name='application-rejected'),
    path('settlement-approved/<pk>', bt_settlement_approved, name='settlement-approved'),
    path('settlement-rejected/<pk>', bt_settlement_rejected, name='settlement-rejected'),

    # do sprawdzenia czy poniższe nadal są używane?

    path('approve/mail/<pk>', BtApplicationApprovalMailDetailView.as_view(), name='approval-mail'),

    # podformularze do rozliczenia wniosku

    # create Views
    path(
        'settlement-info-create/<pk>',
        BtApplicationSettlementInfoCreateFormView.as_view(),
        name='settlement-info-create'
    ),
    path(
        'settlement-cost-create/<pk>',
        BtApplicationSettlementCostCreateView.as_view(),
        name='settlement-cost-create'
    ),
    path(
        'settlement-mileage-create/<pk>',
        BtApplicationSettlementMileageCreateView.as_view(),
        name='settlement-mileage-create'
    ),
    path(
        'settlement-feeding-create/<pk>',
        BtApplicationSettlementFeedingCreateView.as_view(),
        name='settlement-feeding-create'
    ),

    # Delete Views
    path(
        'settlement-cost-delete/<pk>',
        BtApplicationSettlementCostDeleteView.as_view(),
        name='settlement-cost-delete'
    ),
    path(
        'settlement-mileage-delete/<pk>',
        BtApplicationSettlementMileageDeleteView.as_view(),
        name='settlement-mileage-delete'
    ),

    # UpdateViews
    path(
        'settlement-info-update/<pk>',
        BtApplicationSettlementInfoUpdateView.as_view(),
        name='settlement-info-update'
    ),
    path(
        'settlement-feeding-update/<pk>',
        BtApplicationSettlementFeedingUpdateView.as_view(),
        name='settlement-feeding-update'
    ),
]
