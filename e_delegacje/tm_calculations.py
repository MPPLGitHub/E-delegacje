"""Module containig calculation functions"""
from e_delegacje.enums import BtApplicationStatus
from e_delegacje.models import (
    BtApplicationSettlementCost, 
    BtApplicationSettlementMileage, 
    )
from setup.models import BtDelegationRate
import datetime

def settlement_cost_sum(settlement):
    """"""
    cost_sum = 0
    cost_list = BtApplicationSettlementCost.objects.filter(bt_application_settlement=settlement)
    for cost in cost_list:
        cost_sum += cost.bt_cost_amount
    return round(cost_sum, 2)


def mileage_cost_sum(settlement):
    mileage_cost = 0
    mileage_cost_list = BtApplicationSettlementMileage.objects.filter(bt_application_settlement=settlement)
    for mileage in mileage_cost_list:
        mileage_cost = mileage_cost + mileage.bt_mileage_rate.rate * mileage.mileage
    return round(mileage_cost, 2)

def trip_duration(settlement):
    try:
        start_date = settlement.bt_application_info.bt_start_date
        start_time = settlement.bt_application_info.bt_start_time
        end_date = settlement.bt_application_info.bt_end_date
        end_time = settlement.bt_application_info.bt_end_time
        bt_start = datetime.datetime(start_date.year,
                                     start_date.month,
                                     start_date.day,
                                     start_time.hour,
                                     start_time.minute)
        bt_end = datetime.datetime(end_date.year, end_date.month, end_date.day, end_time.hour, end_time.minute)
    except:
        bt_start = datetime.datetime.now()
        bt_end = datetime.datetime.now()
    # print(f'{settlement.bt_application_id.trip_purpose_text} trip duration: {bt_end - bt_start}')
    return bt_end - bt_start


def get_diet_amount_poland(settlement):
    bt_duration = trip_duration(settlement)
    diet = 0
    country = settlement.bt_application_id.bt_country
    if bt_duration.days < 1:
        if (bt_duration.seconds / 3600) < 8:
            diet = 0
        elif 8 <= (bt_duration.seconds / 3600) <= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif (bt_duration.seconds / 3600) >= 12:
            diet = BtDelegationRate.objects.get(country=country).delagation_rate
        else:
            print('pol poni??ej ??aden if')
    elif bt_duration.days >= 1:
        if (bt_duration.seconds / 3600) <= 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif 8 < (bt_duration.seconds / 3600):
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        # elif (bt_duration.seconds / 3600) >= 12:
        #     diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        # else:
        #     print('pol powy??ej ??aden if')
    return diet


def diet_reconciliation_poland(settlement):
    diet = get_diet_amount_poland(settlement)
    country = settlement.bt_application_id.bt_country
    if diet > 0:
        try:
            breakfasts_correction = settlement.bt_application_settlement_feeding.breakfast_quantity * \
                                    BtDelegationRate.objects.get(country=country).delagation_rate * 0.25
            dinners_correction = settlement.bt_application_settlement_feeding.dinner_quantity * \
                                 BtDelegationRate.objects.get(country=country).delagation_rate * 0.5
            suppers_correction = settlement.bt_application_settlement_feeding.supper_quantity * \
                                 BtDelegationRate.objects.get(country=country).delagation_rate * 0.25
        except:
            breakfasts_correction = 0
            dinners_correction = 0
            suppers_correction = 0
        return round(diet - breakfasts_correction - dinners_correction - suppers_correction, 2)
    else:
        return 0


def get_diet_amount_abroad(settlement):
    bt_duration = trip_duration(settlement)
    country = settlement.bt_application_id.bt_country
    diet = 0
    if bt_duration.days < 1:
        if (bt_duration.seconds / 3600) <= 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 3
        elif 8 < (bt_duration.seconds / 3600) <= 12:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif (bt_duration.seconds / 3600) > 12:
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        else:
            print('poni??ej ??aden if')

    elif bt_duration.days >= 1:
        if (bt_duration.seconds / 3600) <= 8:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 3
        elif 8 < (bt_duration.seconds / 3600) <= 12:
            diet = bt_duration.days * BtDelegationRate.objects.get(country=country).delagation_rate + \
                   BtDelegationRate.objects.get(country=country).delagation_rate / 2
        elif 12 < (bt_duration.seconds / 3600):
            diet = (bt_duration.days + 1) * BtDelegationRate.objects.get(country=country).delagation_rate
        else:
            print('z powy??ej ??aden if')
    return diet


def diet_reconciliation_abroad(settlement):
    diet = get_diet_amount_abroad(settlement)
    country = settlement.bt_application_id.bt_country
    try:
        breakfasts_correction = settlement.bt_application_settlement_feeding.breakfast_quantity * \
                                BtDelegationRate.objects.get(country=country).delagation_rate * 0.15
        dinners_correction = settlement.bt_application_settlement_feeding.dinner_quantity * \
                             BtDelegationRate.objects.get(country=country).delagation_rate * 0.30
        suppers_correction = settlement.bt_application_settlement_feeding.supper_quantity * \
                             BtDelegationRate.objects.get(country=country).delagation_rate * 0.30
    except:
        breakfasts_correction = 0
        dinners_correction = 0
        suppers_correction = 0
    return round(diet - breakfasts_correction - dinners_correction - suppers_correction, 2)
