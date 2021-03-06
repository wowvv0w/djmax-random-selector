import pandas as pd
import random
from string import ascii_letters
import time
import keyboard as kb

isnt_alphabet = lambda x: x not in ascii_letters
name = ('Title', 'Artist', 'Genre', 'Series', '4BNM', '4BHD', '4BMX', '4BSC',
    '5BNM', '5BHD', '5BMX', '5BSC', '6BNM', '6BHD', '6BMX', '6BSC',
    '8BNM', '8BHD', '8BMX', '8BSC', 'Length')
_styles = ('NM', 'HD', 'MX', 'SC')

# YourData 읽기
def readYourData():

    # data = pd.read_csv("YourData.csv", names = name)
    data = pd.read_csv("test_data.csv", names = name)

    return data

# 곡 무작위 선정
def selectingMusic(data, buttons, styles, series, diff_min, diff_max, isFreestyle):

    filtered = data[data['Series'].isin(series)]
    if isFreestyle:
        diff_list = ['{0}B{1}'.format(i, j) for i in buttons for j in styles]
        filtered = filtered.reset_index(drop=True)
        candidate_list = ['{0} {1}'.format(filtered.loc[i, 'Title'], j) for i in range(len(filtered))
                for j in diff_list if filtered.loc[i, j] >= diff_min and filtered.loc[i, j] <= diff_max]
    else:
        candidate_list = filtered['Title'].tolist()
    

    try:
        selected = random.choice(candidate_list)
    except IndexError:
        return 'None', None, None, None, None


    if isnt_alphabet(selected[0]):
        init_input = 'a'
    else:
        init_input = selected[0].lower()

    find_sinit = data['Title'].tolist()
    if isnt_alphabet(selected[0]):
        sinit_list = [find_sinit[i] for i in range(len(find_sinit)) if isnt_alphabet(find_sinit[i][0])]
    else:
        sinit_list = [find_sinit[i] for i in range(len(find_sinit)) if find_sinit[i][0] == selected[0].lower()
                                                                    or find_sinit[i][0] == selected[0].upper()]
    if isFreestyle:
        down_input = sinit_list.index(selected[:-5])
    else:
        down_input = sinit_list.index(selected)
    

    if isFreestyle:
        bt_input = selected[-4]
        find_btst = ['{0}B{1}'.format(selected[-4], _styles[i]) for i in range(_styles.index(selected[-2:]) + 1)]
        find_smusic = filtered[filtered['Title'] == selected[:-5]]
        find_smusic = find_smusic[[*find_btst]]
        find_smusic = find_smusic.values.tolist()[0][:len(find_btst)]
        sub_count = find_smusic.count(0)
        right_input = len(find_btst) - sub_count - 1
    else:
        bt_input, right_input = None, None

    return selected, bt_input, init_input, down_input, right_input

# 키보드 자동 입력
def inputKeyboard(music, bt, init, down, right, input_delay, isFreestyle):
    
    delay = lambda: time.sleep(input_delay)
    press = lambda key: kb.press_and_release(key)

    if isFreestyle:
        press(bt)
        delay()
    press('page up')
    delay()
    press(init)
    delay()
    if isnt_alphabet(music[0]):
        press('page up')
        delay()
        press('page up')
        delay()
        press('page down')
        delay()
    for i in range(down):
        press("down arrow")
        delay()
    if isFreestyle:
        for i in range(right):
            press("right arrow")
            delay()

# YourData 수정
def modifyYourData(series):

    data = pd.read_csv("AllTrackData.csv", names = name)

    filtered = data[data['Series'].isin(series)]

    filtered = specialMusicFilter(filtered, series)
    
    # filtered.to_csv("YourData.csv", index=None, header=None)
    filtered.to_csv("test_data.csv", index=None, header=None)

def specialMusicFilter(df, series):

    # RP in DLC 삭제 조건
    if not series > {'TR'}:
        df = df.drop(df[df['Title'] == 'Nevermind'].index)
    if not series > {'CE'}:
        df = df.drop(df[df['Title'] == 'Rising The Sonic'].index)
    if not series > {'BS'}:
        df = df.drop(df[df['Title'] == 'ANALYS'].index)
    if not series > {'T1'}:
        df = df.drop(df[df['Title'] == 'Do you want it'].index)
    if not series > {'T2'}:
        df = df.drop(df[df['Title'] == 'End of Mythology'].index)
    if not series > {'T3'}:
        df = df.drop(df[df['Title'] == 'ALiCE'].index)

    # Link Disc 삭제 조건
    if series > {'CE'} and not series > {'BS'} and not series > {'T1'}:
        df = df.drop(df[df['Title'] == 'Here in the Moment ~Extended Mix~'].index)
    if not series > {'CE'} and series > {'BS'} and not series > {'T1'}:
        df = df.drop(df[df['Title'] == 'Airwave ~Extended Mix~'].index)
    if not series > {'CE'} and not series > {'BS'} and series > {'T1'}:
        df = df.drop(df[df['Title'] == 'SON OF SUN ~Extended Mix~'].index)
    
    return df