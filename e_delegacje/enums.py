""" Enumeration and Choices classes that are to be used in model's choice fields"""
from enum import Enum
from django.db import models


class BtApplicationStatus(models.TextChoices):
    """Statuses for applications"""
    saved = 'saved', 'zapisany'
    in_progress = 'in_progress', 'w akceptacji'
    approved = 'approved', 'zaakceptowany'
    rejected = 'rejected', 'odrzucony'
    settlement_in_progress = 'settlement_in_progress', "W rozliczeniu"
    settled = 'settled', 'rozliczony'
    canceled = 'canceled', 'anulowany'


class BtTransportType(models.TextChoices):
    """Types of transport"""
    train = 'train', "pociąg"
    plane = 'plane', 'samolot'
    company_car = 'company_car', 'samochód służbowy'
    own_car = 'own_car', 'własny samochód'
    other = 'other', 'inny'


class BtEmployeeLevel(models.TextChoices):
    """Emploee levels"""
    lvl1 = 'lvl1', 'podstawowy'
    lvl2 = 'lvl2', 'kierownik'
    lvl3 = 'lvl3', 'dyrektor'
    lvl4 = 'lvl4', 'dyrektor regionu'
    lvl5 = 'lvl5', 'dyrektor dywizji'
    lvl6 = 'lvl6', 'członek zarządu'
    lvl7 = 'lvl7', 'prezes zarządu'


class BtCostCategory(models.TextChoices):
    """Cost Categories"""
    accommodation = 'accommodation', 'nocleg'
    transport = 'transport', 'dojazd'
    luggage = 'luggage', 'bagaż'
    consumption = 'consumption', 'konsumpcja'


class BtVatRates(models.TextChoices):
    """VAT rates"""
    W1 = 'W1', '23 %'
    W8 = 'W8', '8 %'
    WN = 'WN', 'nie dotyczy'
    W0 = 'W0', 'zwolniony'


class BtMileageVehicleTypes(models.TextChoices):
    """Vehicle types for mileage calculation"""
    car_under_900cm3 = 'car_under_900cm3', 'auto o pojemności do 900cm3'
    car_above_900cm3 = 'car_above_900cm3', 'auto o pojemności powyżej 900cm3'
    motorbike = 'motorbike', 'motocykl'
    moped = 'moped', 'motorower'

