import pandas as pd
import random
from string import ascii_letters
import time
import keyboard as kb

isnt_alphabet = lambda x: x not in ascii_letters
name = ('Title', 'Artist', 'Series',
    '4BNM', '4BHD', '4BMX', '4BSC', '5BNM', '5BHD', '5BMX', '5BSC',
    '6BNM', '6BHD', '6BMX', '6BSC', '8BNM', '8BHD', '8BMX', '8BSC')
_styles = ('NM', 'HD', 'MX', 'SC')

# YourData 읽기
def readYourData(debug):

    if debug:
        data = pd.read_csv("test_data.csv", names = name)
    else:
        data = pd.read_csv("YourData.csv", names = name)

    return data
    
# 곡 필터링
def filteringMusic(data, buttons, styles, series, diff_min, diff_max, isFreestyle):
    
    filtered = data[data['Series'].isin(series)]
    candidate_list = []
    fil_title = filtered['Title'].values
    diff_list = ['{0}{1}'.format(i, j) for i in buttons for j in styles]
    len_title = len(fil_title)

    for i in range(len(diff_list)):
        fil_level = filtered[diff_list[i]].values.reshape(len_title)
        fil_level_dup = [diff_list[i]] * len_title
        zip_title_level = zip(fil_title, fil_level_dup, fil_level)
        scan_candidate = [i for i in zip_title_level if diff_min <= i[2] <= diff_max]
        candidate_list.extend(scan_candidate)

    try:
        candidate_title = set(i[0] for i in candidate_list)
        if not isFreestyle:
            candidate_list = list(candidate_title)
    except IndexError:
        candidate_title = []
    
    return filtered, candidate_list, candidate_title

# 곡 무작위 선정
def selectingMusic(data, filtered, candidate_list, isFreestyle, previous):    
    
    if previous:
        if isFreestyle:
            candidate_list = [i for i in candidate_list if i[0] not in previous]
        else:
            candidate_list = [i for i in candidate_list if i not in previous]

    try:
        if isFreestyle:
            selected_title, selected_btst, _ = random.choice(candidate_list)
        else:
            selected_title = random.choice(candidate_list)
            selected_btst = 'FREE'
    except IndexError:
        return None, None, None, None, None, None
    
    if isnt_alphabet(selected_title[0]):
        init_input = 'a'
    else:
        init_input = selected_title[0].lower()
    
    title_list = data['Title'].values
    if isnt_alphabet(selected_title[0]):
        same_init_list = [i for i in title_list if isnt_alphabet(i[0])]
    else:
        same_init_list = [i for i in title_list if i[0].lower() == init_input]
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

    if debug:
        return

    def inputKey(key):
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
    if not 'TR' in series:
        df = df.drop(df[df['Title'] == 'Nevermind'].index)
    if not 'CE' in series:
        df = df.drop(df[df['Title'] == 'Rising The Sonic'].index)
    if not 'BS' in series:
        df = df.drop(df[df['Title'] == 'ANALYS'].index)
    if not 'T1' in series:
        df = df.drop(df[df['Title'] == 'Do you want it'].index)
    if not 'T2' in series:
        df = df.drop(df[df['Title'] == 'End of Mythology'].index)
    if not 'T3' in series:
        df = df.drop(df[df['Title'] == 'ALiCE'].index)

    # Link Disc 삭제 조건
    if 'CE' in series and not 'BS' in series and not 'T1' in series:
        df = df.drop(df[df['Title'] == 'Here in the Moment ~Extended Mix~'].index)
    if not 'CE' in series and 'BS' in series and not 'T1' in series:
        df = df.drop(df[df['Title'] == 'Airwave ~Extended Mix~'].index)
    if not 'CE' in series and not 'BS' in series and 'T1' in series:
        df = df.drop(df[df['Title'] == 'SON OF SUN ~Extended Mix~'].index)
    
    return df

# 실험
if __name__ == '__main__':
    import cProfile
    ex_data = pd.read_csv("AllTrackData.csv", names = name)
    ex_buttons = {'4B', '5B', '6B', '8B'}
    ex_styles = {'NM', 'HD', 'MX', 'SC'}
    ex_series = {'RP', 'P1', 'P2', 'TR', 'CE', 'BS', 'VE', 'ES', 'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY', 'GF', 'CHU'}
    ex_diff_min = 1
    ex_diff_max = 15
    ex_isFreestyle = 1
    ex_previous = []

    start = time.time()
    ex_filtered, ex_candidate_list, ex_candidate_title = filteringMusic(ex_data, ex_buttons, ex_styles, ex_series, ex_diff_min, ex_diff_max, ex_isFreestyle)
    print(time.time() - start)

    start = time.time()
    ex_title, ex_btst, ex_bt, ex_init, ex_down, ex_right = selectingMusic(ex_data, ex_filtered, ex_candidate_list, ex_isFreestyle, ex_previous)
    print(time.time() - start)
    print(ex_title + ' | ' + ex_btst)

    # cProfile.run('selectingMusic(ex_data, ex_filtered, ex_candidate_list, ex_isFreestyle, ex_previous)')