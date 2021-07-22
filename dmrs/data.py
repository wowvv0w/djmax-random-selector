import csv
import json
from json.decoder import JSONDecodeError
import pandas as pd
import requests
from .music import filter_music

_column = ('Title', 'Artist', 'Series',
    '4BNM', '4BHD', '4BMX', '4BSC', '5BNM', '5BHD', '5BMX', '5BSC',
    '6BNM', '6BHD', '6BMX', '6BSC', '8BNM', '8BHD', '8BMX', '8BSC')

_keys = {
    '4B', '5B', '6B', '8B', 'NM', 'HD', 'MX', 'SC',
    'RP', 'P1', 'P2', 'P3', 'TR', 'CE', 'BS', 'VE',
    'ES', 'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY',
    'GF', 'CHU', 'ESTI',
    'MIN', 'MAX', 'BEGINNER', 'MASTER', 'FREESTYLE',
    'INPUT DELAY', 'PREVIOUS', 'TRAY', 'FAVORITE', 'AUTO START'
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

    if not test:
        data = pd.read_csv(YOUR_DATA, names = _column)
    else:
        data = pd.read_csv(TEST_DATA, names = _column)

    return data

def edit_data(series_filter, test):

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


def filtering(func):

        def wrapper(self, *args):
            func(self, *args)

            if not hasattr(self, 'is_init'):
                self = self.parent_

            if not self.is_init:
                self.fil_yourdata, self.fil_list, self.fil_total = \
                        filter_music(
                            self.yourdata, self.bt_list, self.st_list, self.sr_list,
                            self.min, self.max, self.is_freestyle,
                            self.is_favor, self.is_favor_black, self.favorite
                            )
                
                erm = self.erm_slider
                if self.fil_total:
                    erm.setMaximum(self.fil_total - 1)
                else:
                    erm.setMaximum(0)
                
                if erm.value() < self.pre_cnt:
                    erm.setValue(self.pre_cnt)

        return wrapper


@filtering
def import_config(self, json_, init=False):

    self.is_init = True

    with open(json_, 'r') as f:
        config = json.load(f)

    for val, cb in self.btn_diff:
        cb.setChecked(config[val])

    for val, cb, _ in self.categories:
        cb.setChecked(config[val])

    self.lvl_min.setValue(config['MIN'])
    self.lvl_max.setValue(config['MAX'])
    if config['BEGINNER']:
        self.cb_bgn.setChecked(True)
    elif config['MASTER']:
        self.cb_mst.setChecked(True)
    else:
        self.cb_std.setChecked(True)

    if config['FREESTYLE']:
        self.cb_freestyle.setChecked(True)
    else:
        self.cb_online.setChecked(True)

    if init:
        self.delay_slider.setValue(config['INPUT DELAY'])
        self.tray_button.setChecked(config['TRAY'])
        self.autostart_button.setChecked(config['AUTO START'])
    self.erm_slider.setValue(config['PREVIOUS'])
    self.pre_cnt = config['PREVIOUS']
    self.favorite_button.setChecked(config['FAVORITE']['Enabled'])
    self.favorite = set(config['FAVORITE']['List'])
    self.is_favor_black = config['FAVORITE']['Black']

    self.is_init = False

def export_config(self, json_):

    config = {}

    for val, cb in self.btn_diff:
        config[val] = cb.isChecked()

    for val, cb, _ in self.categories:
        config[val] = cb.isChecked()

    config['MIN'] = self.lvl_min.value()
    config['MAX'] = self.lvl_max.value()
    config['BEGINNER'] = self.cb_bgn.isChecked()
    config['MASTER'] = self.cb_mst.isChecked()
    config['FREESTYLE'] = self.cb_freestyle.isChecked()

    config['INPUT DELAY'] = self.delay_slider.value()
    config['AUTO START'] = self.autostart_button.isChecked()
    config['PREVIOUS'] = self.erm_slider.value()
    config['TRAY'] = self.is_tray
    config['FAVORITE'] = {}
    config['FAVORITE']['Enabled'] = self.is_favor
    config['FAVORITE']['List'] = list(self.favorite)
    config['FAVORITE']['Black'] = self.is_favor_black

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
        else:
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
