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
def readYourData(debug):

    if debug:
        data = pd.read_csv("test_data.csv", names = name)
    else:
        data = pd.read_csv("YourData.csv", names = name)

    return data
    
# 곡 필터링
def filteringMusic(data, buttons, styles, series, diff_min, diff_max):

    filtered = data[data['Series'].isin(series)]
    candidate_list = []
    fil_title = filtered['Title'].values
    diff_list = ['{0}{1}'.format(i, j) for i in buttons for j in styles]
    for i in range(len(diff_list)):
        fil_level = filtered[diff_list[i]].values.reshape(len(fil_title))
        fil_level_dup = [diff_list[i]] * len(fil_title)
        zip_title_level = list(zip(fil_title, fil_level_dup, fil_level))
        scan_candidate = list(filter(lambda x: x[2] >= diff_min and x[2] <= diff_max, zip_title_level))
        candidate_list.extend(scan_candidate)
    
    print(len(candidate_list))
    return filtered, candidate_list

# 곡 무작위 선정
def selectingMusic(data, filtered, candidate_list, isFreestyle):    

    try:
        selected_title, selected_btst, _ = random.choice(candidate_list)
    except IndexError:
        return None, None, None, None, None, None
    
    if isnt_alphabet(selected_title[0]):
        init_input = 'a'
    else:
        init_input = selected_title[0].lower()

    title_list = data['Title'].values
    if isnt_alphabet(selected_title[0]):
        same_init_list = list(filter(lambda x: isnt_alphabet(x), title_list))
    else:
        same_init_list = list(filter(lambda x: x[0].lower() == init_input, title_list))
    down_input = same_init_list.index(selected_title)

    if isFreestyle:
        find_same_music = filtered[filtered['Title'] == selected_title]
        find_btst = ['{0}{1}'.format(selected_btst[:2], _styles[i]) for i in range(_styles.index(selected_btst[2:]) + 1)]
        find_same_music = find_same_music[[*find_btst]].values.reshape(len(find_btst)).tolist()
        sub_count = find_same_music.count(0)
        right_input = len(find_btst) - sub_count - 1

        bt_input = selected_btst[0]
    else:
        bt_input, right_input = None, None

    return selected_title, selected_btst, bt_input, init_input, down_input, right_input

# 키보드 자동 입력
def inputKeyboard(music, bt, init, down, right, input_delay, isFreestyle, debug):

    def inputKey(key):
        if debug:
            print(key)
            time.sleep(input_delay)
        else:
            kb.press_and_release(key)
            time.sleep(input_delay)

    if isFreestyle:
        inputKey(bt)
    inputKey('page up')
    inputKey(init)
    if isnt_alphabet(music[0]):
        inputKey('page up')
        inputKey('page up')
        inputKey('page down')
    for i in range(down):
        inputKey('down arrow')
    if isFreestyle:
        for i in range(right):
            inputKey('right arrow')

# YourData 수정
def modifyYourData(series, debug):

    data = pd.read_csv("AllTrackData.csv", names = name)

    filtered = data[data['Series'].isin(series)]

    filtered = specialMusicFilter(filtered, series)
    
    if debug:
        filtered.to_csv("test_data.csv", index=None, header=None)
    else:
        filtered.to_csv("YourData.csv", index=None, header=None)

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

if __name__ == '__main__':
    import cProfile
    ex_data = readYourData()
    ex_buttons = ['4B', '5B', '6B', '8B']
    ex_styles = ['NM', 'HD', 'MX', 'SC']
    ex_series = {'RP', 'P1', 'P2', 'TR', 'CE', 'BS', 'VE', 'ES', 'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY', 'GF', 'CHU'}
    ex_diff_min = 1
    ex_diff_max = 15
    ex_title, ex_btst, ex_bt, ex_init, ex_down, ex_right = selectingMusic(ex_data, ex_buttons, ex_styles, ex_series, ex_diff_min, ex_diff_max, True)
    print(ex_title, ex_btst)
    # cProfile.run('selectingMusic(ex_data, ex_buttons, ex_styles, ex_series, ex_diff_min, ex_diff_max, True)')