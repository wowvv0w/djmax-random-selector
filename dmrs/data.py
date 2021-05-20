import csv
import json
from json.decoder import JSONDecodeError
import pandas as pd
import requests


_column = ('Title', 'Artist', 'Series',
    '4BNM', '4BHD', '4BMX', '4BSC', '5BNM', '5BHD', '5BMX', '5BSC',
    '6BNM', '6BHD', '6BMX', '6BSC', '8BNM', '8BHD', '8BMX', '8BSC')

_keys = {
    '4B', '5B', '6B', '8B', 'NM', 'HD', 'MX', 'SC',
    'RP', 'P1', 'P2', 'P3', 'TR', 'CE', 'BS', 'VE',
    'ES', 'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY',
    'GF', 'CHU',
    'MIN', 'MAX', 'BEGINNER', 'MASTER', 'FREESTYLE',
    'INPUT DELAY', 'PREVIOUS', 'TRAY', 'FAVORITE'
    }

ALL_TRACK_DATA = './data/AllTrackData.csv'
YOUR_DATA = './data/YourData.csv'
TEST_DATA = './test_data.csv'
VERSION_TXT = './data/version.txt'
PRESET_PATH = './data/presets'

YOUR_CONFIG = './data/config.json'
TEST_CONFIG = './test_config.json'

VERSION_URL = "https://raw.githubusercontent.com/wowvv0w/DJMAX_Random_Selector/main/data/version.txt"
DATABASE_URL = 'https://raw.githubusercontent.com/wowvv0w/DJMAX_Random_Selector/main/data/AllTrackData.csv'

def read_data(test):
    """
    Return dataframe.

    - `test` defines if this run is for test or not.

    If `test` is True, return `TEST_DATA`. Otherwise, return `YOUR_DATA`.
    """

    if not test:
        data = pd.read_csv(YOUR_DATA, names = _column)
    else:
        data = pd.read_csv(TEST_DATA, names = _column)

    return data

def edit_data(series_filter, test):
    """
    Edit YourData.csv
    """

    if not test:
        db = YOUR_DATA
    else:
        db = TEST_DATA
    
    title_filter = _generate_title_filter(series_filter)

    data = pd.read_csv(ALL_TRACK_DATA)
    filtered = data[data['Series'].isin(series_filter)]
    filtered = filtered[filtered['Title'].isin(title_filter) == False]

    filtered.to_csv(db, index=None, header=None)

def update_database():
    """
    Updates database from remote repository.
    """

    try:
        response = requests.get(DATABASE_URL)
        if response.status_code == requests.codes.ok:
            with open(ALL_TRACK_DATA, 'w', encoding='UTF-8') as file:
                file.write(response.text)
        else:
            print('there is something wrong')
    except:
        print('db failed')
        return

def update_check():
    try:
        response = requests.get(VERSION_URL)
        if response.status_code == requests.codes.ok:
            last_ver = response.text
            rs_last_ver, db_last_ver = map(int, last_ver.split(','))
        else:
            print('there is something wrong')
    except:
        print('ver failed')
        return 0, 0, 0, 0
    
    with open(VERSION_TXT, 'r') as f:
        curr_ver = f.read()
        rs_curr_ver, db_curr_ver = map(int, curr_ver.split(','))
    
    return rs_curr_ver, rs_last_ver, db_curr_ver, db_last_ver

def update_version(rs, db):
    with open(VERSION_TXT, 'w') as f:
        f.write(f'{rs},{db}')
        

def import_config(cls, json_, init=False):
    """
    Import config.
    """

    cls.is_init = True

    with open(json_, 'r') as f:
        config = json.load(f)

    for val, cb in cls.btn_diff:
        cb.setChecked(config[val])

    for val, cb, _ in cls.categories:
        cb.setChecked(config[val])

    cls.lvl_min.setValue(config['MIN'])
    cls.lvl_max.setValue(config['MAX'])
    if config['BEGINNER']:
        cls.cb_bgn.setChecked(True)
    elif config['MASTER']:
        cls.cb_mst.setChecked(True)
    else:
        cls.cb_std.setChecked(True)

    if config['FREESTYLE']:
        cls.cb_freestyle.setChecked(True)
    else:
        cls.cb_online.setChecked(True)

    if init:
        cls.delay_slider.setValue(config['INPUT DELAY'])
        cls.erm_slider.setValue(config['PREVIOUS'])
        cls.tray_button.setChecked(config['TRAY'])
    cls.favorite_button.setChecked(config['FAVORITE']['Enabled'])
    cls.favorite = set(config['FAVORITE']['List'])
    cls.is_favor_black = config['FAVORITE']['Black']

    cls.filtering()
    cls.erm_initialize()

    cls.is_init = False

def export_config(cls, json_):
    """
    Export config.
    """

    config = {}

    for val, cb in cls.btn_diff:
        config[val] = cb.isChecked()

    for val, cb, _ in cls.categories:
        config[val] = cb.isChecked()

    config['MIN'] = cls.lvl_min.value()
    config['MAX'] = cls.lvl_max.value()
    config['BEGINNER'] = cls.cb_bgn.isChecked()
    config['MASTER'] = cls.cb_mst.isChecked()
    config['FREESTYLE'] = cls.cb_freestyle.isChecked()

    config['INPUT DELAY'] = cls.delay_slider.value()
    config['PREVIOUS'] = cls.erm_slider.value()
    config['TRAY'] = cls.is_tray
    config['FAVORITE'] = {}
    config['FAVORITE']['Enabled'] = cls.is_favor
    config['FAVORITE']['List'] = list(cls.favorite)
    config['FAVORITE']['Black'] = cls.is_favor_black

    with open(json_, 'w') as f:
        json.dump(config, f, indent=4)

def lock_series(categories, enabled):
    for val, cb, lck in categories:
        if val in enabled:
            cb.setEnabled(True)
            lck.setVisible(False)
        else:
            cb.setChecked(False)
            cb.setEnabled(False)
            lck.setVisible(True)

def check_config(json_):
    with open(json_, 'r') as f:
        try:
            config = json.load(f)
        except JSONDecodeError:
            return False
    
    if set(config.keys()) == _keys:
        return True
    else:
        return False




def generate_title_list():
    with open(ALL_TRACK_DATA, 'r', encoding='UTF-8') as file:
        data = csv.reader(file)
        next(data)

        list_ = [i[0] for i in data]
    
    return list_


def _generate_title_filter(series):
    """
    Generates title filter.
    """

    title_filter = set()
    # RP in DLC
    if 'P3' not in series:
        title_filter.add('glory day (Mintorment Remix)')
        title_filter.add('glory day -JHS Remix-')
    if 'TR' not in series:
        title_filter.add('Nevermind')
    if 'CE' not in series:
        title_filter.add('Rising The Sonic')
    if 'BS' not in series:
        title_filter.add('ANALYS')
    if 'T1' not in series:
        title_filter.add('Do you want it')
    if 'T2' not in series:
        title_filter.add('End of Mythology')
    if 'T3' not in series:
        title_filter.add('ALiCE')

    # Link Disc
    if 'CE' in series and 'BS' not in series and 'T1' not in series:
        title_filter.add('Here in the Moment ~Extended Mix~')
    if 'CE' not in series and 'BS' in series and 'T1' not in series:
        title_filter.add('Airwave ~Extended Mix~')
    if 'CE' not in series and 'BS' not in series and 'T1' in series:
        title_filter.add('SON OF SUN ~Extended Mix~')

    return title_filter
