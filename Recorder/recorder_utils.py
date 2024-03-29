from datetime import date, datetime, tzinfo, timedelta
from os.path import exists
import pytz
from pathlib import Path
import time

DATE_FORMAT = '%Y-%m-%d'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_ZONE = 'US/Eastern'
TZ = pytz.timezone(TIME_ZONE)
PLUS = '+'
PIPE = '|'
EQUALS = '='

LABEL_TYPE_DEFAULT = 'DEFAULT'
LABEL_TYPE_DATE = 'DATE'
LABEL_TYPE_TAROT = 'TAROT'
LABEL_TYPE_CHOICES = ((LABEL_TYPE_DATE, LABEL_TYPE_DATE),
                      (LABEL_TYPE_TAROT, LABEL_TYPE_TAROT),
                      (LABEL_TYPE_DEFAULT, LABEL_TYPE_DEFAULT))

TAROT_NAMES = ('00_the_fool', '01_the_magician', '02_the_high_priestess', '03_the_empress', '04_the_emperor',
               '05_the_hierophant', '06_the_lovers', '07_the_chariot', '08_strength', '09_the_hermit',
               '10_wheel_of_fortune', '11_justice', '12_the_hanged_man', '13_death', '14_temperance',
               '15_the_devil', '16_the_tower', '17_the_star', '18_the_moon', '19_the_sun',
               '20_judgement', '21_the_world',

               'cup_01', 'cup_02', 'cup_03', 'cup_04', 'cup_05', 'cup_06', 'cup_07', 'cup_08', 'cup_09', 'cup_10',
               'cup_11_page', 'cup_12_knight', 'cup_13_queen', 'cup_14_king',

               'pentacle_01', 'pentacle_02', 'pentacle_03', 'pentacle_04', 'pentacle_05', 'pentacle_06', 'pentacle_07',
               'pentacle_08', 'pentacle_09', 'pentacle_10', 'pentacle_11_page', 'pentacle_12_knight',
               'pentacle_13_queen', 'pentacle_14_king',

               'sword_01', 'sword_02', 'sword_03', 'sword_04', 'sword_05', 'sword_06', 'sword_07', 'sword_08',
               'sword_09', 'sword_10', 'sword_11_page', 'sword_12_knight', 'sword_13_queen', 'sword_14_king',

               'wand_01', 'wand_02', 'wand_03', 'wand_04', 'wand_05', 'wand_06', 'wand_07', 'wand_08',
               'wand_09', 'wand_10', 'wand_11_page', 'wand_12_knight', 'wand_13_queen', 'wand_14_king')

BASE_DIR = Path(__file__).resolve().parent.parent


def get_current_date_str():
    return get_current_time().strftime(DATE_FORMAT)


def get_current_ts_str():
    return get_current_time().strftime(TIMESTAMP_FORMAT)


def get_current_time():
    return datetime.now(TZ)


def get_current_milli():
    return round(time.time() * 1000)

def is_date(date_str):
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False


def abs_path(relative_path: str):
    if not relative_path.startswith('/'):
        return str(BASE_DIR) + '/' + relative_path
    else:
        return relative_path


def read_secret_keys():
    property_file_path = abs_path('Recorder/secrets.properties')
    if not exists(property_file_path):
        raise FileExistsError("Add file secrets.properties under /Recorder")
    with open(property_file_path, 'r') as property_file:
        lines = property_file.readlines()
        properties = {}
        for line in lines:
            line = line.strip()
            if EQUALS in line:
                properties[line.split(EQUALS)[0]] = line.split(EQUALS)[1]
        return properties


def is_tarot_name(name):
    if isinstance(name, str):
        if name.endswith('_R'):
            name = name[:-2]
    return name in TAROT_NAMES


def is_reversed_tarot_name(name):
    return is_tarot_name(name) and name.endswith('_R')


def reverse_tarot_name(name):
    if is_tarot_name(name):
        if name.endswith('_R'):
            return name[:-2]
        else:
            return name + '_R'
    return None


def add_days_to_datetime(dt: datetime, days: int):
    return dt + timedelta(days=days)


def replace_datetime_to_nine(dt: datetime):
    # return dt.replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone(TIME_ZONE))
    return TZ.localize(dt.replace(hour=9, minute=0, second=0, microsecond=0))


def read_datetime_from_ts(ts):
    if ' ' in ts:
        return TZ.localize(datetime.strptime(ts, TIMESTAMP_FORMAT))
    else:
        return TZ.localize(datetime.strptime(ts, DATE_FORMAT))


def is_in_next_24h(dt: datetime):
    return get_current_time() <= dt < (get_current_time() + timedelta(days=1))



