import pandas as pd


_name = ('Title', 'Artist', 'Series',
    '4BNM', '4BHD', '4BMX', '4BSC', '5BNM', '5BHD', '5BMX', '5BSC',
    '6BNM', '6BHD', '6BMX', '6BSC', '8BNM', '8BHD', '8BMX', '8BSC')

def read_data(test):
    """
    Return csv file created from "AllTrackData.csv".

    - `test` defines if this run is for test or not.

    If `test` is True, return "test_data.csv". Otherwise, return "data\\YourData.csv".
    """

    if test:
        data = pd.read_csv("./test_data.csv", names = _name)
    else:
        data = pd.read_csv("./data/YourData.csv", names = _name)

    return data

def edit_data(series, test):
    """
    Edit YourData.csv
    """

    data = pd.read_csv("./AllTrackData.csv", names = _name)

    filtered = data[data['Series'].isin(series)]

    filtered = filter_special_music(filtered, series)

    if test:
        filtered.to_csv("./test_data.csv", index=None, header=None)
    else:
        filtered.to_csv("./data/YourData.csv", index=None, header=None)

def filter_special_music(df, series):
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
