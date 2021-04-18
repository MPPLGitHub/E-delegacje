from django.urls import path
from e_delegacje.views import (
    index,
    BtApplicationCreateView,
    BtApplicationListView,
    BtApplicationDetailView,
    BtApplicationDeleteView,
    BtApplicationSettlementView,
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
    BtApprovalListView
)

app_name = 'e_delegacje'
urlpatterns = [

    path('', index, name='index'),

    # BtApplicatons - wnioski o delegacje
    path('applications-create/', BtApplicationCreateView.as_view(), name='applications-create'),
    path('applications-list', BtApplicationListView.as_view(), name='applications-list'),
    path('application-details/<pk>', BtApplicationDetailView.as_view(), name='application-details'),
    path('application-delete/<pk>', BtApplicationDeleteView.as_view(), name='application-delete'),
    # BtApplicatons - wnioski o rozliczenie delegacji
    path('settlement-create/<pk>', BtApplicationSettlementCreateView.as_view(), name='settlement-create'),
    path('settlement-add-forms/<pk>', BtApplicationSettlementView.as_view(), name='settlement-add-forms'),
    path('settlements-list', BtApplicationSettlementsListView.as_view(), name='settlements-list'),
    path('settlement-details/<pk>', BtApplicationSettlementDetailView.as_view(), name='settlement-details'),
    # Approvals

    path('approve/<pk>', BtApplicationApprovalDetailView.as_view(), name='approval'),
    path('approval-list', BtApprovalListView.as_view(), name='approval-list'),
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

]
