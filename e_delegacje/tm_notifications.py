from email import message
from msilib import text
from socket import timeout

# from prompt_toolkit import application
# from e_delegacje.enums import BtApplicationStatus
from e_delegacje.models import BtApplicationSettlementCost
from setup.models import BtUser
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives, send_mail
import smtplib


def new_application_notification(user_mail, sent_app):
    application = sent_app
    application_number = sent_app.id
    application_status = sent_app.application_status

    html_content = render_to_string(
        'Mail_templates/bt_mail_notification.html',
        {
            'application': application,
            'application_status': application_status,
        }
    )
    text_content = strip_tags(html_content)
    if application_status == 'in_progress':
        email = EmailMultiAlternatives(
            # subject
            f'Proszę o weryfikację wniosku nr {application_number}.',
            # content
            text_content,
            # from email
            'travel-management@metro-properties.pl',
            # receipients list
            [user_mail]
        )
    elif application_status == 'settlement_in_progress':
            email = EmailMultiAlternatives(
            # subject
            f'Proszę o weryfikację rozliczenia do wniosku nr {application_number}.',
            # content
            text_content,
            # from email
            'travel-management@metro-properties.pl',
            # receipients list
            [user_mail]
        )
    email.attach_alternative(html_content, 'text/html')
    email.send()
   

def approved_or_rejected_notification(sent_app, appr_rejct_user, approval_status,rejection_reason):

    application_number = sent_app.id
    application = sent_app
    application_author = sent_app.application_author
    approval_status = approval_status
    
    if application.application_status == 'settled':
        receipient_list = [application_author.email, application.target_user.email]
        mail_subject = \
            f'Wniosek nr {application_number} został rozliczony i finalnie zaakceptowany'
        application_to_be_booked_notification(sent_app)
        
    else:
        receipient_list = [application_author.email, application.target_user.email]
        mail_subject = f'Wniosek nr {application_number} został {approval_status}.'


    html_content = render_to_string(
        'Mail_templates/bt_mail_approved_rejected_notification.html',
        {
            'application': application,
            'approval_status': approval_status,
            'approver': appr_rejct_user,
            'rejection_reason' : rejection_reason
        }
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        # subject
        mail_subject,
        # content
        text_content,
        # from email
        'travel-management@metro-properties.pl',
        # receipients list
        receipient_list
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
   


def application_to_be_booked_notification(sent_app):
    
    application = sent_app
    attachments = []
    receipient_list = []
    for accountant in BtUser.objects.filter(group=1):
        receipient_list.append(accountant.email)
        print(accountant.email)
    
    mail_subject = \
        f'Wniosek nr {application.id} został zaakceptowany. w załączeniu dane do zaksięgowania'

    for cost in BtApplicationSettlementCost.objects.\
        filter(bt_application_settlement = application.bt_applications_settlements.id):
        attachments.append(cost.attachment)
        print('utworzono listę załączników {attachments}')

    html_content = render_to_string(
        'Mail_templates/bt_mail_acoounting_notification.html',
        {
            'application': application,
        }
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        # subject
        mail_subject,
        # content
        text_content,
        # from email
        'travel-management@metro-properties.pl',
        # receipients list
        receipient_list
    )
    email.attach_alternative(html_content, 'text/html')
    if attachments:
        for attachment in attachments:
            email.attach_file(attachment.path)
    email.send()
