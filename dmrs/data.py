import pandas as pd
from requests import get, codes


_name = ('Title', 'Artist', 'Series',
    '4BNM', '4BHD', '4BMX', '4BSC', '5BNM', '5BHD', '5BMX', '5BSC',
    '6BNM', '6BHD', '6BMX', '6BSC', '8BNM', '8BHD', '8BMX', '8BSC')

ALL_TRACK_DATA = './AllTrackData.csv'
TEST_DATA = './test_data.csv'
YOUR_DATA = './data/YourData.csv'

ALL_TRACK_DATA_URL = 'https://raw.githubusercontent.com/wowvv0w/DJMAX_Random_Selector/main/AllTrackData.csv'

def read_data(test):
    """
    Return csv file created from "AllTrackData.csv".

    - `test` defines if this run is for test or not.

    If `test` is True, return "test_data.csv". Otherwise, return "data\\YourData.csv".
    """

    if test:
        data = pd.read_csv(TEST_DATA, names = _name)
    else:
        data = pd.read_csv(YOUR_DATA, names = _name)

    return data

def edit_data(series, test):
    """
    Edit YourData.csv
    """

    data = pd.read_csv(ALL_TRACK_DATA, names = _name)

    filtered = data[data['Series'].isin(series)]

    filtered = _filter_special_music(filtered, series)

    if test:
        filtered.to_csv(TEST_DATA, index=None, header=None)
    else:
        filtered.to_csv(YOUR_DATA, index=None, header=None)

def _filter_special_music(df, series):
    """
    Exclude music which has complicated condition
    """

    # RP in DLC
    if 'P3' not in series:
        df = df.drop(df[df['Title'] == 'glory day (Mintorment Remix)'].index)
        df = df.drop(df[df['Title'] == 'glory day -JHS Remix-'].index)
    if 'TR' not in series:
        df = df.drop(df[df['Title'] == 'Nevermind'].index)
    if 'CE' not in series:
        df = df.drop(df[df['Title'] == 'Rising The Sonic'].index)
    if 'BS' not in series:
        df = df.drop(df[df['Title'] == 'ANALYS'].index)
    if 'T1' not in series:
        df = df.drop(df[df['Title'] == 'Do you want it'].index)
    if 'T2' not in series:
        df = df.drop(df[df['Title'] == 'End of Mythology'].index)
    if 'T3' not in series:
        df = df.drop(df[df['Title'] == 'ALiCE'].index)

    # Link Disc
    if 'CE' in series and 'BS' not in series and 'T1' not in series:
        df = df.drop(df[df['Title'] == 'Here in the Moment ~Extended Mix~'].index)
    if 'CE' not in series and 'BS' in series and 'T1' not in series:
        df = df.drop(df[df['Title'] == 'Airwave ~Extended Mix~'].index)
    if 'CE' not in series and 'BS' not in series and 'T1' in series:
        df = df.drop(df[df['Title'] == 'SON OF SUN ~Extended Mix~'].index)

    return df

def _update_database():
    """
    Updates AllTrackData.csv from remote repository.
    """

    try:
        response = get(ALL_TRACK_DATA_URL)
    except:
        print('failed')
        return

    if response.status_code == codes.ok:
        with open('test1.csv', 'w', encoding='UTF-8') as file:
            file.write(response.text)
        print('updated')
    else:
        print('there is something wrong')



if __name__ == '__main__':
    _update_database()