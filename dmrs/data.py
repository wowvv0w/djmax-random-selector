import csv
import pandas as pd
import requests


_column = ('Title', 'Artist', 'Series',
    '4BNM', '4BHD', '4BMX', '4BSC', '5BNM', '5BHD', '5BMX', '5BSC',
    '6BNM', '6BHD', '6BMX', '6BSC', '8BNM', '8BHD', '8BMX', '8BSC')

ALL_TRACK_DATA = './data/AllTrackData.csv'
YOUR_DATA = './data/YourData.csv'
TEST_DATA = './test_data.csv'

DATABASE_URL = 'https://raw.githubusercontent.com/wowvv0w/DJMAX_Random_Selector/main/AllTrackData.csv'

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
    except:
        print('failed')
        return

    if response.status_code == requests.codes.ok:
        with open(ALL_TRACK_DATA, 'w', encoding='UTF-8') as file:
            file.write(response.text)
        print('updated')
    else:
        print('there is something wrong')

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
