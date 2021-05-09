import random
import time
from string import ascii_letters

import keyboard as kb


_styles = ('NM', 'HD', 'MX', 'SC')

def is_alphabet(chr_):
    """
    Checkes whether `chr_` is alphabet.
    """
    
    return chr_ in ascii_letters

def filter_music(data, buttons, styles, series, diff_min, diff_max, is_freestyle):
    """
    Filter music.
    """

    filtered = data[data['Series'].isin(series)]
    candidate_list = []
    fil_title = filtered['Title'].values
    diff_list = [f'{bt}{st}' for bt in buttons for st in styles]
    len_title = len(fil_title)

    for diff in diff_list:
        fil_level = filtered[diff].values.reshape(len_title)
        fil_style = [diff] * len_title
        music_info = zip(fil_title, fil_style, fil_level)
        scan_candidate = [m for m in music_info if diff_min <= m[2] <= diff_max]
        candidate_list.extend(scan_candidate)

    try:
        candidate_title = set(cand[0] for cand in candidate_list)
        if not is_freestyle:
            candidate_list = list(candidate_title)
    except IndexError:
        candidate_title = []

    return filtered, candidate_list, candidate_title

def pick_music(data, filtered, candidate_list, is_freestyle, previous, prefer):
    """
    Pick music
    """

    if previous:
        if is_freestyle:
            candidate_list = [cand for cand in candidate_list if cand[0] not in previous]
        else:
            candidate_list = [cand for cand in candidate_list if cand not in previous]

    try:
        if is_freestyle:
            picked_title, picked_btst, __ = random.choice(candidate_list)
        else:
            picked_title = random.choice(candidate_list)
            picked_btst = 'FREE'
    except IndexError:
        return None, None, None, None, None, None

    if is_freestyle and prefer:
        same_tb_list = [cand for cand in candidate_list
            if cand[0] == picked_title and cand[1][0] == picked_btst[0]]
        if prefer == 'beginner':
            same_tb_list.sort(key=lambda x: _styles.index(x[1][2:]))
            picked_title, picked_btst, __ = min(same_tb_list, key=lambda x: x[2])
        elif prefer == 'master':
            same_tb_list.sort(key=lambda x: _styles.index(x[1][2:]), reverse=True)
            picked_title, picked_btst, __ = max(same_tb_list, key=lambda x: x[2])

    if not is_alphabet(picked_title[0]):
        init_input = 'a'
    else:
        init_input = picked_title[0].lower()

    title_list = data['Title'].values
    if not is_alphabet(picked_title[0]):
        same_init_list = [title for title in title_list if not is_alphabet(title[0])]
    else:
        same_init_list = [title for title in title_list if title[0].lower() == init_input]
    down_input = same_init_list.index(picked_title)

    if is_freestyle:
        find_same_music = filtered[filtered['Title'] == picked_title]
        find_btst = [
            '{0}{1}'.format(picked_btst[:2], _styles[i])
            for i in range(_styles.index(picked_btst[2:]) + 1)]
        find_same_music = find_same_music[[*find_btst]].values.reshape(len(find_btst)).tolist()
        sub_count = find_same_music.count(0)
        right_input = len(find_btst) - sub_count - 1

        bt_input = picked_btst[0]
    else:
        bt_input, right_input = None, None

    return picked_title, picked_btst, bt_input, init_input, down_input, right_input

def select_music(music, bt, init, down, right, input_delay, is_freestyle):
    """
    Select music in game by inputing keys automatically.

    - `music` is title of music.
    - `bt` is button of pattern (one of '4, 5, 6, 8').
    - `init` is the first letter of title.
    - `down` is the number of down arrow inputs.
    - `right` is the number of right arrow inputs.
    - `input delay` is delay.
    """

    def send_and_delay(key):
        kb.send(key)
        time.sleep(input_delay)

    if is_freestyle:
        send_and_delay(bt)
    send_and_delay('page up')
    send_and_delay(init)
    if not is_alphabet(music[0]):
        send_and_delay('page up')
        send_and_delay('page up')
        send_and_delay('page down')
    for __ in range(down):
        send_and_delay('down arrow')
    if is_freestyle:
        for __ in range(right):
            send_and_delay('right arrow')
