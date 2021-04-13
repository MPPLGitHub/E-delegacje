from enum import Enum
from django.db import models


class BtTripCategory(models.TextChoices):
    kr = 'kr', 'krajowa'
    zg = 'zg', 'zagraniczna'


class BtApplicationStatus(models.TextChoices):
    saved = 'saved', 'Zapisany'
    in_progress = 'in_progress', 'W akceptacji'
    approved = 'approoved', 'Zaakcdptowany'
    settled = 'settled', 'Rozliczony'
    canceled = 'canceled', 'Anulowany'


class BtTransportType(models.TextChoices):
    train = 'train', "pociąg"
    plane = 'plane', 'samolot'
    company_car = 'company_car', 'samochód służbowy'
    own_car = 'own_car', 'własny samochód'
    other = 'other', 'inny'


class BtEmployeeLevel(models.TextChoices):
    lvl1 = 'lvl1', 'podstawowy'
    lvl2 = 'lvl2', 'kierownik'
    lvl3 = 'lvl3', 'dyrektor'
    lvl4 = 'lvl4', 'dyrektor regionu'
    lvl5 = 'lvl5', 'dyrektor dywizji'
    lvl6 = 'lvl6', 'członek zarządu'
    lvl7 = 'lvl7', 'prezes zarządu'


class BtCostCategory(models.TextChoices):
    accommodation = 'nocleg', 'nocleg'
    transport = 'dojazd', 'dojazd'
    luggage = 'bagaż', 'bagaż'
    other = 'inne', 'inne'


class BtVatRates(models.TextChoices):
    W1 = 'W1', '23 %'
    W8 = 'W8', '8 %'
    WN = 'WN', 'nie dotyczy'
    W0 = 'W0', 'zwolniony'


class BtMileageVehicleTypes(models.TextChoices):
    car_under_900cm3 = 'car_under_900cm3', 'auto o pojemności do 900cm3'
    car_above_900cm3 = 'car_above_900cm3', 'auto o pojemności powyżej 900cm3'
    motorbike = 'motorbike', 'motocykl'
    moped = 'moped', 'motorower'

