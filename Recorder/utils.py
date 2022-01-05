from datetime import date, datetime, tzinfo
from os.path import exists
import pytz

DATE_FORMAT = '%Y-%m-%d'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%s'
TIME_ZONE = 'US/Eastern'
PLUS = '+'
PIPE = '|'
EQUALS = '='

LABEL_TYPE_DEFAULT = 'DEFAULT'
LABEL_TYPE_DATE = 'DATE'
LABEL_TYPE_TAROT = 'TAROT'
LABEL_TYPE_CHOICES = ((LABEL_TYPE_DEFAULT, LABEL_TYPE_DEFAULT),
                      (LABEL_TYPE_DATE, LABEL_TYPE_DATE),
                      (LABEL_TYPE_TAROT, LABEL_TYPE_TAROT))


def get_current_date_str():
    return get_current_time().strftime(DATE_FORMAT)


def get_current_ts_str():
    return get_current_time().strftime(TIMESTAMP_FORMAT)


def get_current_time():
    return datetime.now(pytz.timezone(TIME_ZONE))


def is_date(date_str):
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False


def read_secret_keys():
    property_file_path = 'Recorder/secrets.properties'
    if not exists(property_file_path):
        raise FileExistsError("Add file secrets.properties under /Recorder")
    with open(property_file_path, 'r') as property_file:
        lines = property_file.readlines()
        properties = {}
        for line in lines:
            if EQUALS in line:
                properties[line.split(EQUALS)[0]] = line.split(EQUALS)[1]
        return properties


