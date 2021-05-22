import random
import time
import math
from string import ascii_letters
from typing import Any, Iterable, List, Tuple, Union, Deque
import keyboard as kb


_styles = ('NM', 'HD', 'MX', 'SC')

def check_alphabet(word: str) -> bool:
    """
    Checkes whether `word` is alphabet.
    """
    
    return word in ascii_letters

def filter_music(
    data: Any,
    buttons: Iterable,
    styles: Iterable,
    series: Iterable,
    diff_min: int,
    diff_max: int,
    is_freestyle: bool,
    is_favor: bool,
    is_favor_black: bool,
    favorite: Iterable
) -> Tuple[Any, list, int]:
    """
    Filter music.
    """

    filtered = data[data['Series'].isin(series)]
    if is_favor:
        if is_favor_black:
            filtered = filtered[filtered['Title'].isin(favorite) == False]
        else:
            filtered = filtered[filtered['Title'].isin(favorite)]

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
        candidate_title = {cand[0] for cand in candidate_list}
        if not is_freestyle:
            candidate_list = list(candidate_title)
    except IndexError:
        candidate_title = []

    return filtered, candidate_list, len(candidate_title)

def pick_music(
    data: Any,
    filtered: Any,
    candidate_list: Iterable,
    prefer: Union[str, None],
    is_freestyle: bool,
    previous: Deque,
    auto_start: bool
) -> Union[Tuple[str, str, List[bool], Tuple[str, str, int, int]], List[None]]:
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
            if prefer:
                list_ = list({(cand[0], cand[1][0]) for cand in candidate_list})
                picked_title, picked_btst = random.choice(list_)
            else:
                picked_title, picked_btst, _ = random.choice(candidate_list)
        else:
            picked_title = random.choice(candidate_list)
            picked_btst = 'FREE'
    except IndexError:
        return [None] * 4

    if prefer and is_freestyle:
        same_tb_list = [
            cand for cand in candidate_list if cand[0] == picked_title and cand[1][0] == picked_btst
            ]
        if prefer == 'beginner':
            same_tb_list.sort(key=lambda x: _styles.index(x[1][2:]))
            picked_title, picked_btst, _ = min(same_tb_list, key=lambda x: x[2])
        else:
            same_tb_list.sort(key=lambda x: _styles.index(x[1][2:]), reverse=True)
            picked_title, picked_btst, _ = max(same_tb_list, key=lambda x: x[2])


    initial = picked_title[0].lower()
    is_alphabet = check_alphabet(initial)

    title_list = data['Title'].values
    if is_alphabet:
        same_init_list = [title for title in title_list if title[0].lower() == initial]
    else:
        same_init_list = [title for title in title_list if not check_alphabet(title[0])]
    
    whereisit = same_init_list.index(picked_title)
    cnt = len(same_init_list)
    is_forward = whereisit <= math.ceil(cnt / 2) or initial in 'wxyz'
    if is_forward:
        if is_alphabet:
            initial_input = initial
        else:
            initial_input = 'a'
        vertical_input = whereisit
    else:
        if is_alphabet:
            initial_input = chr(ord(initial) + 1)
        else:
            initial_input = 'a'
        vertical_input = cnt - whereisit
    

    if is_freestyle:
        find_same_music = filtered[filtered['Title'] == picked_title]
        find_btst = [
            '{0}{1}'.format(picked_btst[:2], _styles[i])
            for i in range(_styles.index(picked_btst[2:]) + 1)]
        find_same_music = find_same_music[[*find_btst]].values.reshape(len(find_btst)).tolist()
        sub_count = find_same_music.count(0)
        right_input = len(find_btst) - sub_count - 1

        bt_input = picked_btst[0]
        is_autostart = auto_start
    else:
        bt_input, right_input, is_autostart = None, 0, False

    
    check_list = [is_alphabet, is_forward, is_autostart]
    input_list = (bt_input, initial_input, vertical_input, right_input)

    return picked_title, picked_btst, check_list, input_list

def select_music(
    input_delay: float,
    check_list: List[bool],
    input_list: Tuple[str, str, int, int]
) -> None:
    """
    Select music in game by inputing keys automatically.
    """

    alphabet, forward, start = check_list
    bt, init, vert, right = input_list
    if forward:
        direction = 'down arrow'
    else:
        direction = 'up arrow'
    def typing(key):
        kb.send(key)
        time.sleep(input_delay)

    if bt:
        typing(bt)
    typing('page up')
    typing(init)
    if not alphabet and forward:
        typing('page up')
        typing('page up')
        typing('page down')
    for _ in range(vert):
        typing(direction)
    for _ in range(right):
        typing('right arrow')
    if start:
        time.sleep(0.8 - input_delay)
        kb.send('f5')
        
