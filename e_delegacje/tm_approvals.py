from e_delegacje.enums import BtApplicationStatus
from e_delegacje.models import (
    BtApplication,
    BtApplicationSettlement
)
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
import datetime
from e_delegacje.tm_notifications import approved_or_rejected_notification, new_application_notification

def bt_application_approved(request, pk):
    bt_application = BtApplication.objects.get(id=pk)
    rejection_reason = ""
    if bt_application.application_status == BtApplicationStatus.in_progress.value:
        bt_application.application_status = BtApplicationStatus.approved.value
        bt_application.application_log = \
            bt_application.application_log + \
            f"\nWniosek zaakceptowany przez {request.user.first_name} {request.user.last_name} "

        bt_application.save()
        approved_or_rejected_notification(bt_application, request.user, BtApplicationStatus.approved.label, rejection_reason)
    else:
        return render(request, template_name='already_processed.html', context={'application': bt_application})

    # return render(request, template_name='approve_reject_success.html', context={'application': bt_application})
    return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


def bt_application_rejected(request, pk):
    bt_application = BtApplication.objects.get(id=pk)
    if bt_application.application_status == BtApplicationStatus.in_progress.value:
        bt_application.application_status = BtApplicationStatus.rejected.value
        bt_application.application_log = \
            bt_application.application_log + \
            f"\nWniosek odrzucony przez {request.user.first_name} {request.user.last_name} \n\n" \
            f"Powód: "
        bt_application.save()
        approved_or_rejected_notification(bt_application, request.user, BtApplicationStatus.rejected.label)
    else:
        return render(request, template_name='already_processed.html', context={'application': bt_application})

    return render(request, template_name='approve_reject_success.html', context={'application': bt_application})
    # return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


def send_settlement_to_approver(request, pk):
    settlement = BtApplicationSettlement.objects.get(id=pk)
    settlement.settlement_status = BtApplicationStatus.in_progress.value
    settlement.save()
    bt_application = BtApplication.objects.get(bt_applications_settlements__id=pk)
    
    new_application_notification(bt_application.target_user.manager.email,bt_application)
    return HttpResponseRedirect(reverse("e_delegacje:applications-list"))


def bt_settlement_approved(request, pk):
    bt_application = BtApplication.objects.get(bt_applications_settlements__id=pk)
    bt_application.application_status = BtApplicationStatus.settled.value
    bt_application.approver = request.user
    bt_application.approval_date = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    bt_application.save()

    settlement = BtApplicationSettlement.objects.get(id=pk)
    settlement.settlement_status = BtApplicationStatus.approved.value
    settlement.save()
    approved_or_rejected_notification(bt_application, request.user, BtApplicationStatus.approved.label,"")

    return HttpResponseRedirect(reverse("e_delegacje:approval-list"))


def bt_settlement_rejected(request, pk):
    settlement = BtApplicationSettlement.objects.get(id=pk)
    settlement.settlement_status = BtApplicationStatus.rejected.value
    settlement.save()

    return HttpResponseRedirect(reverse("e_delegacje:approval-list"))
