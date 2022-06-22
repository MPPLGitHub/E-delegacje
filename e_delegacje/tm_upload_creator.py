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
from e_delegacje.enums import BtCostCategory
from setup.models import BtGLAccounts


class Upload():
    """ Creates upload prepared for booking travel reconciliation in SAP system"""
    def __init__(self, application) -> None:
        self.application = application
        self.settlement = BtApplicationSettlement.objects.get(id=self.application.bt_applications_settlements.id)
        self.header_1 = ['/BBKPF', 'TCODE', 'BUKRS', 'BLART', 'XBLNR', 'BUDAT', 'BLDAT', 'VATDATE','WAERS']
        self.header_2 = ['/BBSEG', 'NEWBS', 'NEWKO', 'WRBTR', 'WMWST', 'MWSKZ', 'KOSTL', 'SGTXT', 'ZFBDT', 'PRCTR', 'AUFNR', 'ZUONR']
        self.today = datetime.now().strftime("%Y%m%d")
        self.cost_sum = float(settlement_cost_sum(BtApplicationSettlement.objects.get(pk=self.settlement.id)))
        self.mileage_cost = float(mileage_cost_sum(BtApplicationSettlement.objects.get(pk=self.settlement.id)))
        if self.settlement.bt_application_id.bt_country.country_name.lower() == 'polska':
            self.diet = round(diet_reconciliation_poland(self.settlement), 2)
        else:
            self.diet = round(diet_reconciliation_abroad(self.settlement), 2)
        self.total_costs = str(self.cost_sum + self.mileage_cost + self.diet).replace('.', ',')
        self.approval_date = self.settlement.bt_application_info.approval_date.strftime("%Y%m%d")
        self.cost_list = [cost for cost in BtApplicationSettlementCost.objects.filter(
            bt_application_settlement = self.settlement.id
            )]
        file_name = f'/media/uploads/upload_delegation_TM_{self.application.id}.csv'

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
            self.application.advance_payment_currency.code,  # Currency
            "",  # empty cell
            'TM/' + str(self.application.id),  # assignment
            ]
        return BBKPF_row
    
    def create_vendor_row(self):
        """Creates first Line of booking- emploee - vendor"""
        BBSEG_vendor_row = [
            'BBSEG',  # upload row category
            '31',  # posting key
            self.application.target_user.vendor_id,  # account- vendor number ? to be changed in invoice uload creator
            self.total_costs,  # Amount - gross amount booked on vendor
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

    def create_diet_row(self):
        """Creates Line of booking- diet"""
        BBSEG_diet_row = [
            'BBSEG',  # upload row category
            '40',  # posting key
            BtGLAccounts.objects.get(cost_category=BtCostCategory.diet).gl_account_number,  # account- diet
            str(self.diet).replace('.', ','),  # Amount - gross amount booked on vendor
            "",  # Empty cell
            "WN",  # tax Code
            self.application.CostCenter.cost_center_number,  # Cost Center
            'Dieta - delegacja TM/' + str(self.application.id),  # text
            '',  # empty cell
            self.application.CostCenter.profit_center_id.profit_center,  # profit center
            '',  # empty cell(order-only in P&L line)
            'TM/' + str(self.application.id),  # assignment
            ]
        return BBSEG_diet_row


    def create_cost_rows(self):
        """Create list of rows for each cost, diet, mileage lum sum for travel reconciliation"""
        BBSEG_Cost_rows = []
        for cost in self.cost_list:
            gl_account = BtGLAccounts.objects.get(cost_category=cost.bt_cost_category)
            if self.application.CostCenter.order is None:
                order = None
            else:
                order = self.application.CostCenter.order.order,  # order

            data = [
                'BBSEG',  # upload row category
                '40',  # posting key
                gl_account.gl_account_number,  # GL account
                str(cost.bt_cost_amount).replace('.', ','),  # Amount
                "",  # Empty cell
                "WN",  # tax Code
                self.application.CostCenter.cost_center_number,  # Cost Center
                cost.bt_cost_description,  # text - cost decription
                '',
                self.application.CostCenter.profit_center_id.profit_center,  # profit center
                order,
                'TM/' + str(self.application.id),  # assignment
            ]
            BBSEG_Cost_rows.append(data)
        return BBSEG_Cost_rows



    def create_ht_document_upload(self):
        """Creates HT document type upload"""
        file_name = f'media/uploads/upload_delegation_TM_{self.application.id}.csv'

        with open(file_name, 'w', encoding='UTF8', newline='') as csv_file:
            writer = csv.writer(csv_file,delimiter=';')
            writer.writerow(self.header_1)
            writer.writerow(self.header_2)
            writer.writerow(self.create_header_row())
            writer.writerow(self.create_vendor_row())
            writer.writerow(self.create_diet_row())
            writer.writerows(self.create_cost_rows())

        