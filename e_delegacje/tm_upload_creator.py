from django.shortcuts import render
from django.http import HttpResponse
import unicodedata
# from unidecode import unidecode
from wsgiref.util import FileWrapper
from django.conf import settings

from e_delegacje.models import (
    BtApplicationSettlement, 
    BtApplicationSettlementCost, 
    BtApplicationSettlementMileage
)
import csv
from datetime import datetime
from e_delegacje.tm_calculations import (
    settlement_cost_sum, 
    mileage_cost_sum,
    diet_reconciliation_poland,
    diet_reconciliation_abroad
    )
from e_delegacje.forms import BtAddInvoiceDataForm
from e_delegacje.enums import BtCostCategory, BtBookingStatus, BtTaxCategory
from setup.models import BtGLAccounts
from e_delegacje.models import BtApplication
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

def set_application_as_booked_manually(request, pk):
    """Sets the field in BtApplication model 'booked' to booked_manually"""
    application = BtApplication.objects.get(id=pk)
    application.booked = BtBookingStatus.booked_manually.value
    application.save()
    return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-list"))

def set_application_as_booked_upload(request, pk):
    """Sets the field in BtApplication model 'booked' to booked_upload"""
    application = BtApplication.objects.get(id=pk)
    application.booked = BtBookingStatus.booked_upload.value
    application.save()
    return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-list"))

def set_application_as_no_booking_needed(request, pk):
    """Sets the field in BtApplication model 'booked' to booked_upload"""
    application = BtApplication.objects.get(id=pk)
    application.booked = BtBookingStatus.no_booking_needed.value
    application.save()
    return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-list"))

def set_cost_tax_deductable(request, pk):
    cost = BtApplicationSettlementCost.objects.get(id=pk)
    cost.tax_deductible = BtTaxCategory.KUP.value
    cost.save()
    return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-details",
    args=[cost.bt_application_settlement.id]))

def set_cost_non_tax_deductable(request, pk):
    cost = BtApplicationSettlementCost.objects.get(id=pk)
    cost.tax_deductible = BtTaxCategory.NKUP.value
    cost.save()
    return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-details",
    args=[cost.bt_application_settlement.id]))

class Upload():
    """ Creates upload prepared for booking travel reconciliation in SAP system"""
    def __init__(self, settlement, cost=None) -> None:
        self.settlement = settlement
        if cost is not None:
            self.cost = cost
        self.application = BtApplication.objects.get(id=self.settlement.bt_application_id.id)
        self.file_name = f'media/uploads/upload_delegation_TM_{self.application.id}.csv'
        self.header_1 = [
            '/BBKPF', 
            'TCODE', 
            'BUKRS', 
            'BLART', 
            'XBLNR', 
            'BUDAT', 
            'BLDAT', 
            'VATDATE',
            'WAERS',
            '','','']
        self.header_2 = [
            '/BBSEG', 
            'NEWBS', 
            'NEWKO', 
            'WRBTR', 
            'WMWST', 
            'MWSKZ', 
            'KOSTL', 
            'SGTXT', 
            'ZFBDT', 
            'PRCTR', 
            'AUFNR', 
            'ZUONR']
        self.today = datetime.now().strftime("%Y%m%d")
        self.mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=self.settlement.id)))
        self.cost_sum = self.get_cost_sum()
        if self.settlement.bt_application_id.advance_payment_currency.code == "PLN":
                self.diet = float(self.application.bt_application_settlement_info.diet_amount)
        else:
            self.diet = round(float(self.application.bt_application_settlement_info.diet_amount)\
                        *float(self.application.bt_application_settlement_info.settlement_exchange_rate), 2)
        self.invoice_required_cost_categories = [
            BtCostCategory.accommodation, 
            BtCostCategory.consumption_invoice,
            BtCostCategory.taxi,
            BtCostCategory.parking,
            BtCostCategory.transport,
            BtCostCategory.consumption,
            ]
        self.total_costs = round((self.cost_sum + self.mileage_cost + self.diet),2)
        self.approval_date = self.settlement.bt_application_info.approval_date.replace("-","")
        self.cost_list = self.get_cost_list()
        self.invoice_required_cost_list = self.get_invoice_required_cost_list()
        self.vat_rates = {'W1' : 1.23, 'W8' : 1.08, 'WN' : 1, 'W0' : 1}
        self.file_name = f'/media/uploads/upload_delegation_TM_{self.application.id}.csv'

    def get_cost_sum(self):
        """Calculating sum of costs which are not invoice required costs"""
        invoice_required_costs = [
            BtCostCategory.accommodation, 
            BtCostCategory.consumption_invoice
            ]
        if self.settlement.bt_application_settlement_costs is not None:
            cost_sum = 0
            for cost in self.settlement.bt_application_settlement_costs.all():
                cost_sum+= round(cost.bt_cost_amount,2)
        if self.application.advance_payment_currency != 'PLN':
            cost_sum *= self.application.bt_application_settlement_info.settlement_exchange_rate

        return float(cost_sum)

    def get_cost_list(self):
        """list of costs that are to be booked in HT document - application reconciliation"""
        cost_list = [
            cost for cost in BtApplicationSettlementCost.objects.filter(
            bt_application_settlement = self.settlement.id
            ) if cost.bt_cost_category not in self.invoice_required_cost_categories
            ]
        return cost_list
    
    def get_invoice_required_cost_list(self):
        """costs that has categories for which it is needed to ceate separate booking of invoice"""

        cost_list = [
            cost for cost in BtApplicationSettlementCost.objects.filter(
            bt_application_settlement = self.settlement.id
            ) if cost.bt_cost_category in self.invoice_required_cost_categories
            ]
        return cost_list
    
    def get_function_from_category(self, category, cost):
        self.cost_create_mapping = {
            BtCostCategory.parking: self.create_transport_rows(cost=cost),
            BtCostCategory.parking_nkup: self.create_NKUP_row(cost=cost),
            BtCostCategory.taxi: self.create_KUP_row(cost=cost),
            BtCostCategory.taxi_nkup: self.create_NKUP_row(cost=cost),
            BtCostCategory.transport: self.create_transport_rows(cost=cost),
            BtCostCategory.transport_nkup: self.create_NKUP_row(cost=cost),
            BtCostCategory.tickets: self.create_KUP_row(cost=cost),
            BtCostCategory.consumption: self.create_KUP_row(cost=cost),
            BtCostCategory.consumption_invoice: self.create_KUP_row(cost=cost),
            BtCostCategory.consumption_nkup: self.create_NKUP_row(cost=cost),
            BtCostCategory.accommodation: self.create_KUP_row(cost=cost),
        }
        return self.cost_create_mapping[category]

    def create_header_row(self):
        """Creates header row of booking in SAP"""
        BBKPF_row = [
            'BBKPF',  # upload row category
            "",  # empty cell
            self.application.bt_company_code.company_code,  # Company code 
            'HT',  # Document type
            'TM/' + str(self.application.id),  # Reference 
            self.today,  # posting Date - currently today, później mozna dac możliwośc wprowadenia z ekranu
            self.approval_date,  # Document date
            self.approval_date,  # VAT date
            "PLN",  # Currency
            "",  # empty cell
            'TM/' + str(self.application.id),  # assignment
            ""
            ]
        return BBKPF_row

    def create_header_row_invoice(self, reference=None, cost=None, vat_date=None):
        cost = BtApplicationSettlementCost.objects.get(id=cost)
        """Creates header row of invoice booking in SAP"""
        BBKPF_row = [
            'BBKPF',  # upload row category
            "",  # empty cell
            self.application.bt_company_code.company_code,  # Company code 
            'K8',  # Document type
            reference,  # Reference 
            self.today,  # posting Date - currently today, później mozna dac możliwośc wprowadenia z ekranu
            cost.bt_cost_document_date.strftime("%Y%m%d"),  # Document date
            vat_date.strftime("%Y%m%d"),  # VAT date
            "PLN",  # Currency
            "",  # empty cell
            'TM/' + str(self.application.id),  # assignment
            ""
            ]
        return BBKPF_row
    
    def create_employee_vendor_row(self):
        """Creates first Line of booking- emploee - vendor"""
        BBSEG_vendor_row = [
            'BBSEG',  # upload row category
            '31',  # posting key
            self.application.target_user.vendor_id,  # account- vendor number
            str(self.total_costs).replace('.', ','),  # Amount - gross amount booked on vendor
            '',  # empty cell
            '**',  # Tax code - on Vendor - None = **
            '',  # empty cell
            'Rozliczenie delegacji TM/' + str(self.application.id),  # text
            self.approval_date,  # Baseline date
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            '',  # empty cell(order-only in P&L line)
            'TM/' + str(self.application.id),  # assignment
            ]
        return BBSEG_vendor_row

    def create_invoice_vendor_row(self, vendor=None, cost=None):
        """Creates first Line of booking- emploee - vendor"""
        cost = BtApplicationSettlementCost.objects.get(id=cost)
        BBSEG_vendor_row = [
            'BBSEG',  # upload row category
            '31',  # posting key
            vendor,  # account- vendor number
            str(cost.bt_cost_amount).replace('.', ','),  # Amount - gross amount booked on vendor
            '',  # empty cell
            '**',  # Tax code - on Vendor - None = **
            '',  # empty cell
            cost.bt_cost_description,  # text
            cost.bt_cost_document_date.strftime("%Y%m%d"),  # Baseline date
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            '',  # empty cell(order-only in P&L line)
            'TM/' + str(self.application.id),  # assignment
            ]
        return BBSEG_vendor_row

    def create_diet_row(self):
        """Creates Line of booking- diet"""
        if self.application.CostCenter.order is None:
            order = " "
        else:
            order = self.application.CostCenter.order.order,  # order

        BBSEG_diet_row = [
            'BBSEG',  # upload row category
            '40',  # posting key
            BtGLAccounts.objects.get(cost_category=BtCostCategory.diet).gl_account_number,  # account- diet
            str(self.diet).replace('.', ','),  # Amount - gross amount booked on vendor
            "",  # Empty cell
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
            'Dieta - ' 
                +  self.application.target_user.last_name,  # text
            '',  # empty cell
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],  # empty cell(order-only in P&L line)
            'TM/' + str(self.application.id),  # assignment
            ]
        return BBSEG_diet_row

    def create_transport_rows(self, cost):
        gl_account_KUP = BtGLAccounts.objects.get(
            cost_category=BtCostCategory.transport, tax_category=BtTaxCategory.KUP)
        gl_account_NKUP = BtGLAccounts.objects.get(
            cost_category=BtCostCategory.transport, tax_category=BtTaxCategory.NKUP) 
        net_amount = round(float(cost.bt_cost_amount) / self.vat_rates[cost.bt_cost_VAT_rate],2)
        vat_amount = float(cost.bt_cost_amount) - net_amount
        net_amount_NKUP = round((net_amount +  vat_amount/2) * 0.25,2)
        vat_amount_KUP = round((vat_amount/2),2)
        net_amount_KUP_tax = round(net_amount/2,2)
        net_amount_WN = round(net_amount - net_amount_NKUP - net_amount_KUP_tax + (vat_amount - vat_amount_KUP),2)

        if self.application.CostCenter.order is None:
            order = " "
        else:
            order = self.application.CostCenter.order.order,  # order
        
        row1 = [
            'BBSEG',  # upload row category
            '40',  # posting key
            gl_account_KUP.gl_account_number,  # GL account
            str(net_amount_KUP_tax).replace('.', ','),  # Amount
            # net_amount_KUP,  # Amount
            str(vat_amount_KUP).replace('.', ','),  # VAT amount
            cost.bt_cost_VAT_rate,  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
            cost.bt_cost_description + " - " 
            +  unicodedata.normalize("NFKD",self.application.target_user.last_name),  # text - cost decription
            '',
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],
            'TM/' + str(self.application.id),  # assignment
        ]
        
        row2 = [
            'BBSEG',  # upload row category
            '40',  # posting key
            gl_account_KUP.gl_account_number,  # GL account
            str(net_amount_WN).replace('.', ','),  # Amount
            "",  # Empty cell
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
             cost.bt_cost_description + " - "  
                +  unicodedata.normalize("NFKD",self.application.target_user.last_name),  # text - cost decription
            '',
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],
            'TM/' + str(self.application.id),  # assignment
        ]
        row3 = [
            'BBSEG',  # upload row category
            '40',  # posting key
            gl_account_NKUP.gl_account_number,  # GL account
            str(net_amount_NKUP).replace('.', ','),  # Amount
            "",  # Empty cell
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
             cost.bt_cost_description + " - " 
                +  self.application.target_user.last_name,  # text - cost decription
            '',
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],
            'TM/' + str(self.application.id),  # assignment
        ]
        BBSEG_Cost_rows = [row3, row1, row2]
        return BBSEG_Cost_rows
    
    def create_NKUP_row(self, cost):           
        gl_account = BtGLAccounts.objects.get(
            cost_category=cost.bt_cost_category, tax_category=BtTaxCategory.NKUP)

        if self.application.CostCenter.order is None:
                order = " "
        else:
            order = self.application.CostCenter.order.order,  # order
        cost_amount = cost.bt_cost_amount
        if self.application.advance_payment_currency != 'PLN':
            cost_amount *= self.application.bt_application_settlement_info.settlement_exchange_rate

        BBSEG_Cost_row = [
            'BBSEG',  # upload row category
            '40',  # posting key
            gl_account.gl_account_number,  # GL account
            str(round(cost_amount,2)).replace('.', ','),  # Amount
            "",  # Vat amount
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
             cost.bt_cost_description + " - " 
                +  unicodedata.normalize("NFD",self.application.target_user.last_name),  # text - cost decription
            '',
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],
            'TM/' + str(self.application.id),  # assignment
        ]
        return [BBSEG_Cost_row]
    
    def create_KUP_row(self, cost):        
        gl_account = BtGLAccounts.objects.get(
            cost_category=cost.bt_cost_category, tax_category=BtTaxCategory.KUP)

        if self.application.CostCenter.order is None:
                order = " "
        else:
            order = self.application.CostCenter.order.order,  # order
        cost_amount = cost.bt_cost_amount
        if self.application.advance_payment_currency != 'PLN':
            cost_amount *= self.application.bt_application_settlement_info.settlement_exchange_rate

        BBSEG_Cost_row = [
            'BBSEG',  # upload row category
            '40',  # posting key
            gl_account.gl_account_number,  # GL account
            str(round(cost_amount,2)).replace('.', ','),  # Amount
            "",  # Vat amount
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
             cost.bt_cost_description + " - " 
                +  self.application.target_user.last_name,  # text - cost decription
            '',
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],
            'TM/' + str(self.application.id),  # assignment
        ]
        return [BBSEG_Cost_row]

    def create_cost_rows(self):
        """Creates list of rows for each cost, diet, mileage lum sum for travel reconciliation"""
        BBSEG_Cost_rows = []
        for cost in self.cost_list:
            data = self.get_function_from_category(cost.bt_cost_category, cost)
            for row in data:
                BBSEG_Cost_rows.append(row)
            cost.in_upload = 'tak'
            cost.save()

        return BBSEG_Cost_rows

    def create_invoice_cost_row(self, cost=None):
        """Creates row for net - P&L invoice cost """
        
        cost = BtApplicationSettlementCost.objects.get(id=cost)
        BBSEG_Cost_row = self.get_function_from_category(cost.bt_cost_category, cost)
        
        return BBSEG_Cost_row

    def create_mileage_row(self):
        """Creates Line of booking- Mileage"""
        if self.application.CostCenter.order is None:
            order = " "
        else:
            order = self.application.CostCenter.order.order,  # order
        BBSEG_mileage_row = [
            'BBSEG',  # upload row category
            '40',  # posting key
            BtGLAccounts.objects.get(cost_category=BtCostCategory.mileage).gl_account_number,  # account- mileage
            str(self.mileage_cost).replace('.', ','),  # Amount - mileage_cost a
            "",  # Empty cell
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
            'Ryczalt - '  
                +  unicodedata.normalize("NFD",self.application.target_user.last_name),  # text
            '',  # empty cell
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            order[0],  
            'TM/' + str(self.application.id),  # assignment
            ]
        return BBSEG_mileage_row

    def create_recinciliation_row(self):
        """Creates Line of booking- reconciliation fow for invoice-required costs"""
        cost_list = []
        for cost in self.invoice_required_cost_list:
            cost_amount = round(
                cost.bt_cost_amount * self.application.bt_application_settlement_info.settlement_exchange_rate, 
                2)
            BBSEG_reconciliation_row = [
                'BBSEG',  # upload row category
                '21',  # posting key
                self.application.target_user.vendor_id,  # account- vendor number
                str(cost_amount).replace('.', ','),  # Amount - gross amount booked on vendor
                '',  # empty cell
                '**',  # Tax code - on Vendor - None = **
                '',  # empty cell
                cost.bt_cost_description + " - " 
                +  self.application.target_user.last_name,  # text - description
                self.approval_date,  # Baseline date
                self.application.CostCenter.profit_center_id.profit_center,  # profit center
                '',  # empty cell(order-only in P&L line)
                'TM/' + str(self.application.id),  # assignment
                ]
            cost_list.append(BBSEG_reconciliation_row)

        return cost_list      
        
    def create_ht_document_upload(self):
        """Creates HT document type upload"""
        
        file_name = f'media/uploads/upload_delegation_TM_{self.application.id}.csv'
        with open(file_name, 'w', encoding='UTF8', newline='') as csv_file:
            writer = csv.writer(csv_file,delimiter=';')
            writer.writerow(self.header_1)
            writer.writerow(self.header_2)
            writer.writerow(self.create_header_row())
            writer.writerow(self.create_employee_vendor_row())
            writer.writerow(self.create_diet_row())
            if self.settlement.bt_application_settlement_mileages.count()>0:
                writer.writerow(self.create_mileage_row())
            if self.settlement.bt_application_settlement_costs.count()>0:
                writer.writerows(self.create_cost_rows())
                writer.writerows(self.create_recinciliation_row())
    
    def create_invoice_document_upload(self, cost, vendor, vat_date, reference):
        """Creates invoice document type upload"""
        
        file_name = f'media/uploads/upload_delegation_TM_{self.application.id}.csv'
        with open(file_name, 'a+', encoding='UTF8', newline='') as csv_file:
            writer = csv.writer(csv_file,delimiter=';')
            writer.writerow(self.create_header_row_invoice(vat_date=vat_date, cost=cost, reference=reference))
            writer.writerow(self.create_invoice_vendor_row(cost=cost, vendor=vendor))
            writer.writerows(self.create_invoice_cost_row(cost=cost))

    def read_upload_file(self):
        file_name = f'media/uploads/upload_delegation_TM_{self.application.id}.csv'
        with open(file_name, 'r', encoding='UTF8', newline='') as csv_file:
            csvreader = csv.reader(csv_file, delimiter=';')
            rows = []
            for row in csvreader:
                    rows.append(row)
        return rows

    def save_upload_file(self):
        file_name = f'media/uploads/upload_delegation_TM_{self.application.id}.csv'
        
        response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': 
            f'attachment; filename=upload_delegation_TM_{self.application.id}.csv'},
        )
        with open(file_name, 'r', encoding='UTF8', newline='') as csv_file:
            csvreader = csv.reader(csv_file, delimiter=';')
            writer = csv.writer(response, delimiter=';')
            for row in csvreader:
                read_row = row
                writer.writerow(read_row)
        return response

    
def prepare_ht_document_upload(request, pk):
    """Preparing initial upload for further verification"""
    settlement = BtApplicationSettlement.objects.get(id=pk)
    for cost in settlement.bt_application_settlement_costs.all():
        cost.in_upload = 'nie'
        cost.save()
    upl = Upload(settlement)
    upl.create_ht_document_upload()
    return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-details",
    args=[settlement.id]))
    
def create_invoice_document_upload(request, pk):
    """Creates lines of upload for invoice posting as a new document"""
    cost = BtApplicationSettlementCost.objects.get(id=pk)
    settlement = BtApplicationSettlement.objects.get(id=cost.bt_application_settlement.id)
    upload = Upload(settlement)
    
    if request.method == 'POST':
        form = BtAddInvoiceDataForm(request.POST)
        if form.is_valid():
            reference = form.cleaned_data['reference']
            vat_date = form.cleaned_data['vat_date']
            vendor = form.cleaned_data['vendor']
            upload.create_invoice_document_upload(cost=cost.id,reference=reference, vat_date=vat_date, vendor=vendor)
            cost.in_upload = 'tak'
            cost.save()
            return HttpResponseRedirect(reverse("e_delegacje:ApplicationsToBeBooked-details", 
            args=[settlement.id]))
    else:
        form = BtAddInvoiceDataForm()
    return render(
        request, 
        'CreateCSV/bt_application_to_be_booked_add_invoice_data.html', 
        {'form': form, 'cost':cost}
        )

def download_upload(request, pk):
    settlement = BtApplicationSettlement.objects.get(id=pk)
    upl = Upload(settlement)
    return upl.save_upload_file()


  