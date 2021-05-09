import sys
import json
from threading import Thread
from collections import deque
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QSystemTrayIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFontDatabase
import keyboard as kb
import dmrs


main_ui = uic.loadUiType("./ui/selector_ui.ui")[0]

class SelectorUi(QMainWindow, main_ui):
    """
    Main Window
    """

    # You can change these constants when you test codes.
    IS_TEST = True  # Use test csv and config
    IS_KEY_TEST = True  # Ignore `dmrs.select_music`

    def __init__(self):

        super().__init__()

        self.is_running = False
        self.is_init = True
        self.is_tray = False

        self.yourdata = dmrs.read_data(self.IS_TEST)
        self.previous = deque([])

        self.bt_list = set()
        self.st_list = set()
        self.sr_list = set()
        self.min = 1
        self.max = 15
        self.prefer = None
        self.is_freestyle = True
        self.input_delay = 0.03

        self.fil_yourdata = None
        self.fil_list = None
        self.fil_title = None

        self.setupUi(self)
        self.dataui = DataUi(self)
        self.history = HistoryUi(self)

        self.ui_signal()
        self.filter_signal()
        self.import_config()

        kb.add_hotkey('f7', self.check_state, suppress=True)


    def check_state(self):
        """
        Checkes availability to start.
        """

        if not self.is_running:
            print('start')
            thd_rs = Thread(target=self.random_start)
            thd_rs.start()
        else:
            print('denied')

    def random_start(self):
        """
        Starts random select.
        """

        self.is_running = True
        picked_title, picked_btst, bt_input, init_input, down_input, right_input = \
            dmrs.pick_music(
                self.yourdata, self.fil_yourdata, self.fil_list,
                self.is_freestyle, self.previous, self.prefer
                )
        print(picked_title, ' | ', picked_btst)

        if picked_title:
            print('macro activate')
            if not self.IS_KEY_TEST:
                dmrs.select_music(
                    picked_title, bt_input, init_input, down_input, right_input,
                    self.input_delay, self.is_freestyle
                    )

            _str = picked_title + '  |  ' + picked_btst
            self.history_scrollbar.setMaximum(self.history_scrollbar.maximum() + 1)
            self.history.history_list.addItem(_str)
            self.history_scrollbar.setValue(self.history_scrollbar.maximum())

            if self.erm_slider.value():
                self.previous.append(picked_title)
                if len(self.previous) > self.erm_slider.value():
                    self.previous.popleft()

        self.is_running = False
        print('finish')


    def ui_signal(self):
        """
        Defines signals related to visual design. (and sets fonts)
        """

        # FontDB
        self.fontDB = QFontDatabase()
        self.fontDB.addApplicationFont('./fonts/Lato-Black.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Bold.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Light.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Regular.ttf')
        self.fontDB.addApplicationFont('./fonts/Lato-Thin.ttf')
        # Window
        self.setWindowIcon(QIcon('./images/icon.ico'))
        self.setWindowFlags(Qt.FramelessWindowHint)
        # System tray
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon('./images/icon.ico'))
        self.tray.activated.connect(self.show)
        self.tray.activated.connect(self.tray.hide)
        self.tray.hide()
        # Top bar
        self.minimize_button.clicked.connect(self.minimize_signal)
        self.close_button.clicked.connect(self.close)
        def move_window(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = move_window
        # Tab
        self.filter_tab_bt.toggled.connect(self.tab_signal)

        # Level
        self.lvl_min.valueChanged.connect(lambda: self.lvl_signal(self.lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.lvl_signal(self.lvl_max))
        # Collaboration
        self.cb_collab.clicked.connect(self.collab_signal)
        self.cb_gg.toggled.connect(lambda: self.collab_child_signal(self.cb_gg))
        self.cb_gc.toggled.connect(lambda: self.collab_child_signal(self.cb_gc))
        self.cb_dm.toggled.connect(lambda: self.collab_child_signal(self.cb_dm))
        self.cb_cy.toggled.connect(lambda: self.collab_child_signal(self.cb_cy))
        self.cb_gf.toggled.connect(lambda: self.collab_child_signal(self.cb_gf))
        self.cb_chu.toggled.connect(lambda: self.collab_child_signal(self.cb_chu))
        # Modify data
        self.data_button.clicked.connect(lambda: self.dataui.show_data_ui(self))

        # Input delay
        self.delay_ms.setText(f'{self.delay_slider.value()}ms')
        self.delay_slider.valueChanged.connect(
            lambda: self.delay_ms.setText(f'{self.delay_slider.value()}ms'))
        self.delay_lb.clicked.connect(
            lambda: self.delay_slider.setValue(self.delay_slider.value() - 10))
        self.delay_rb.clicked.connect(
            lambda: self.delay_slider.setValue(self.delay_slider.value() + 10))
        # History
        self.history_button.toggled.connect(self.history_signal)
        self.history_scrollbar = \
            self.history.history_list.verticalScrollBar()
        # Exclude recent music (erm)
        self.erm_num.setText(f'{self.erm_slider.value()}')
        self.erm_slider.valueChanged.connect(
            lambda: self.erm_num.setText(f'{self.erm_slider.value()}'))
        # System tray
        self.tray_button.toggled.connect(self.tray_signal)

    def filter_signal(self):
        """
        Defines signals related to filter.
        """

        # BUTTON TUNES
        self.cb_4b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_4b, '4B'))
        self.cb_5b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_5b, '5B'))
        self.cb_6b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_6b, '6B'))
        self.cb_8b.toggled.connect(lambda: self.is_checked(self.bt_list, self.cb_8b, '8B'))
        # DIFFICULTY
        self.lvl_min.valueChanged.connect(lambda: self.is_value_changed(self.lvl_min))
        self.lvl_max.valueChanged.connect(lambda: self.is_value_changed(self.lvl_max))
        self.cb_nm.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_nm, 'NM'))
        self.cb_hd.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_hd, 'HD'))
        self.cb_mx.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_mx, 'MX'))
        self.cb_sc.toggled.connect(lambda: self.is_checked(self.st_list, self.cb_sc, 'SC'))
        self.cb_bgn.toggled.connect(self.is_prefer_checked)
        self.cb_mst.toggled.connect(self.is_prefer_checked)
        # MODE
        self.cb_freestyle.toggled.connect(self.is_fs_checked)
        # CATEGORIES
        self.cb_rp.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_rp, 'RP'))
        self.cb_p1.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p1, 'P1'))
        self.cb_p2.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p2, 'P2'))
        self.cb_p3.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p3, 'P3'))
        self.cb_tr.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_tr, 'TR'))
        self.cb_ce.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_ce, 'CE'))
        self.cb_bs.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_bs, 'BS'))
        self.cb_ve.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_ve, 'VE'))
        self.cb_es.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_es, 'ES'))
        self.cb_t1.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_t1, 'T1'))
        self.cb_t2.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_t2, 'T2'))
        self.cb_t3.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_t3, 'T3'))
        self.cb_p3.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_p3, 'P3'))
        self.cb_gg.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_gg, 'GG'))
        self.cb_gc.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_gc, 'GC'))
        self.cb_dm.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_dm, 'DM'))
        self.cb_cy.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_cy, 'CY'))
        self.cb_gf.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_gf, 'GF'))
        self.cb_chu.toggled.connect(lambda: self.is_checked(self.sr_list, self.cb_chu, 'CHU'))
        # ADVANCED
        self.delay_slider.valueChanged.connect(lambda: self.is_value_changed(self.delay_slider))
        self.erm_slider.valueChanged.connect(self.erm_initialize)

    def lvl_signal(self, lvl):
        """
        Changes current level range ui: 15 stars in 'Difficulty.'
        """

        indicators = [None, self.d1, self.d2, self.d3, self.d4, self.d5,
                            self.d6, self.d7, self.d8, self.d9, self.d10,
                            self.d11,self.d12,self.d13,self.d14,self.d15]
        d = lvl.value()
        if lvl == self.lvl_min:
            for i in range(1, d):
                indicators[i].setChecked(False)
            for i in range(d, self.max+1):
                indicators[i].setChecked(True)
            self.lvl_max.setMinimum(d)
        else:
            for i in range(15, d, -1):
                indicators[i].setChecked(False)
            for i in range(d, self.min-1, -1):
                indicators[i].setChecked(True)
            self.lvl_min.setMaximum(d)

    def tab_signal(self):
        """
        Highlights which tab has selected.
        """

        if self.filter_tab_bt.isChecked():
            self.tabWidget.setCurrentIndex(0)
            self.current_tab.setText('FILTER')
        else:
            self.tabWidget.setCurrentIndex(1)
            self.current_tab.setText('ADVANCED')

    def collab_signal(self):
        """
        Checkes or uncheckes all categories in 'COLLABORATION' when
        'COLLABORATION' button is clicked.
        """

        self.is_init = True
        checkboxes = [self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy, self.cb_gf, self.cb_chu]
        if self.cb_collab.isChecked():
            for i in checkboxes:
                i.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            for i in checkboxes:
                i.setChecked(False)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')
        self.is_init = False
        self.filtering()

    def collab_child_signal(self, child):
        """
        Changes 'COLLABORATION' background color and check state depend on
        whether all categories in 'COLLABORATION' are checked or not.
        """

        if child.isChecked():
            self.cb_collab.setChecked(True)
            self.collab_frame.setStyleSheet('QFrame{\n	background-color: #1e1e1e;\n}')
        else:
            if not self.cb_gg.isChecked() and not self.cb_gc.isChecked() \
                and not self.cb_dm.isChecked() and not self.cb_cy.isChecked() \
                and not self.cb_gf.isChecked() and not self.cb_chu.isChecked():
                    self.cb_collab.setChecked(False)
                    self.collab_frame.setStyleSheet('QFrame{\n	background-color: rgba(0, 0, 0, 87);\n}')

    def history_signal(self):
        """
        Opens or closes 'History' window when 'SHOW HISTORY' button is clicked.
        """

        if self.history_button.isChecked():
            self.history.show()
            self.history_button.setText('ON')
        else:
            self.history.close()
            self.history_button.setText('OFF')

    def minimize_signal(self):
        """
        Turns to system tray or minimizes window depending on
        whether 'SYSTEM TRAY' button is checked or not.
        """

        if self.is_tray:
            self.hide()
            self.tray.show()
        else:
            self.showMinimized()

    def tray_signal(self):
        """
        Changes 'SYSTEM TRAY' button's label.
        """

        if self.tray_button.isChecked():
            self.is_tray = True
            self.tray_button.setText('ON')
        else:
            self.is_tray = False
            self.tray_button.setText('OFF')


    def is_checked(self, list_, obj, value):
        """
        Checkes `obj` is checked.
        """

        if obj.isChecked():
            list_.add(value)
        else:
            list_.discard(value)

        if not self.is_init:
            self.filtering()
            self.erm_initialize()

    def is_value_changed(self, obj):
        """
        Checkes `obj`'s value.
        """

        if obj == self.lvl_min:
            self.min = obj.value()
        elif obj == self.lvl_max:
            self.max = obj.value()
        else:
            self.input_delay = obj.value() / 1000

        if not self.is_init and obj != self.delay_slider:
            self.filtering()
            self.erm_initialize()

    def is_fs_checked(self):
        """
        Checkes 'Freestyle' button in 'MODE' is checked.
        """

        self.is_freestyle = self.cb_freestyle.isChecked()

        if not self.is_init:
            self.filtering()
            self.erm_initialize()

    def is_prefer_checked(self):
        """
        Checkes prefer
        """

        if self.cb_bgn.isChecked():
            self.prefer = 'beginner'
        elif self.cb_mst.isChecked():
            self.prefer = 'master'
        else:
            self.prefer = None


    def filtering(self):
        """
        Return music list filtered.
        """

        self.fil_yourdata, self.fil_list, self.fil_title = \
                dmrs.filter_music(
                    self.yourdata, self.bt_list, self.st_list,
                    self.sr_list, self.min, self.max, self.is_freestyle)
        if self.fil_title:
            self.erm_slider.setMaximum(len(self.fil_title) - 1)
        else:
            self.erm_slider.setMaximum(0)

    def erm_initialize(self):
        """
        Initializes `previous`
        """
        if self.previous:
            self.previous = deque([])
            print('initialized')


    def import_config(self):
        """
        Import config.
        """

        if self.IS_TEST:
            with open('./test_config.json', 'r') as f:
                config = json.load(f)
        else:
            with open('./data/config.json', 'r') as f:
                config = json.load(f)

        self.values = [
            '4B', '5B', '6B', '8B', 'NM', 'HD', 'MX', 'SC',
            'RP', 'P1', 'P2', 'P3', 'TR', 'CE', 'BS', 'VE',
            'ES', 'T1', 'T2', 'T3', 'GG', 'GC', 'DM', 'CY',
            'GF', 'CHU'
            ]
        self.checkboxes = [
            self.cb_4b, self.cb_5b, self.cb_6b, self.cb_8b, self.cb_nm, self.cb_hd, self.cb_mx, self.cb_sc,
            self.cb_rp, self.cb_p1, self.cb_p2, self.cb_p3, self.cb_tr, self.cb_ce, self.cb_bs, self.cb_ve,
            self.cb_es, self.cb_t1, self.cb_t2, self.cb_t3, self.cb_gg, self.cb_gc, self.cb_dm, self.cb_cy,
            self.cb_gf, self.cb_chu
            ]
        self.locks = [
            None, None, None, None, None, None, None, None,
            None, None, None, self.lock_p3, self.lock_tr, self.lock_ce, self.lock_bs, self.lock_ve,
            self.lock_es, self.lock_t1, self.lock_t2, self.lock_t3, None, self.lock_gc, self.lock_dm, self.lock_cy,
            self.lock_gf, self.lock_chu
            ]

        self.locks_left_check = {self.lock_p3, self.lock_tr, self.lock_ce, self.lock_dm, self.lock_gf}
        for val, cb, lck in zip(self.values, self.checkboxes, self.locks):
            try:
                cb.setChecked(config[val])
            except TypeError:
                cb.setEnabled(False)
                if lck in self.locks_left_check:
                    lck.move(70, lck.y())
                else:
                    lck.move(210, lck.y())

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

        self.delay_slider.setValue(config['INPUT DELAY'])
        self.tray_button.setChecked(config['TRAY'])

        self.filtering()
        self.erm_slider.setValue(config['PREVIOUS'])

        self.is_init = False

    def export_config(self):
        """
        Export config.
        """

        if self.IS_TEST:
            with open('./test_config.json', 'r') as f:
                config = json.load(f)
        else:
            with open('./data/config.json', 'r') as f:
                config = json.load(f)

        for i, j in zip(self.checkboxes, self.values):
            if i.isEnabled():
                config[j] = i.isChecked()
            else:
                config[j] = None

        config['MIN'] = self.lvl_min.value()
        config['MAX'] = self.lvl_max.value()
        config['BEGINNER'] = self.cb_bgn.isChecked()
        config['MASTER'] = self.cb_mst.isChecked()

        config['FREESTYLE'] = self.cb_freestyle.isChecked()

        config['INPUT DELAY'] = self.delay_slider.value()
        config['PREVIOUS'] = self.erm_slider.value()
        config['TRAY'] = self.tray_button.isChecked()

        if self.IS_TEST:
            with open('./test_config.json', 'w') as f:
                json.dump(config, f, indent=4)
        else:
            with open('./data/config.json', 'w') as f:
                json.dump(config, f, indent=4)


    def closeEvent(self, __):
        self.export_config()

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()




class DataUi(QDialog):
    """
    MODIFY DATA Window
    """

    def __init__(self, parent):

        super().__init__(parent)
        data_ui = './ui/modify_data_ui.ui'
        uic.loadUi(data_ui, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.modify_button.clicked.connect(lambda: self.modify_data(parent))
        self.cancel_button.clicked.connect(lambda: self.cancel(parent))
        self.yd_values = ['P3', 'TR', 'CE', 'BS', 'VE',
                          'ES', 'T1', 'T2', 'T3', 'GC',
                          'DM', 'CY', 'GF', 'CHU']
        self.yd_checkboxes = [self.yd_cb_p3, self.yd_cb_tr, self.yd_cb_ce, self.yd_cb_bs, self.yd_cb_ve,
                              self.yd_cb_es, self.yd_cb_t1, self.yd_cb_t2, self.yd_cb_t3, self.yd_cb_gc,
                              self.yd_cb_dm, self.yd_cb_cy, self.yd_cb_gf, self.yd_cb_chu]

    def show_data_ui(self, parent):
        """
        Shows 'MODIFY DATA' window.
        """

        parent.lock_all.move(0, 0)

        modify_data_check = set(parent.yourdata['Series'].values)

        for i, j in zip(self.yd_values, self.yd_checkboxes):
            j.setChecked(i in modify_data_check)

        self.show()

    def modify_data(self, parent):
        """
        Modifies data.
        """

        fil_yd_sr = set(val for val, cb in zip(self.yd_values, self.yd_checkboxes) if cb.isChecked())
        fil_yd_sr.update(['RP', 'P1', 'P2', 'GG'])
        dmrs.edit_data(fil_yd_sr, parent.IS_TEST)
        parent.yourdata = dmrs.read_data(parent.IS_TEST)

        enabled_check = set(parent.yourdata['Series'].values)
        for val, cb, lck in zip(parent.values[9:], parent.checkboxes[9:], parent.locks[9:]):
            try:
                if val in enabled_check:
                    cb.setEnabled(True)
                    if lck in parent.locks_left_check:
                        lck.move(-20, lck.y())
                    else:
                        lck.move(300, lck.y())

                else:
                    cb.setEnabled(False)
                    if lck in parent.locks_left_check:
                        lck.move(70, lck.y())
                    else:
                        lck.move(210, lck.y())
            except AttributeError:
                pass

        parent.lock_all.move(0, -540)
        parent.filtering()
        parent.erm_initialize()
        self.close()

    def cancel(self, parent):
        """
        Cancels modifying and closes window.
        """

        parent.lock_all.move(0, -540)
        self.close()




class HistoryUi(QDialog):
    """
    History Window
    """

    def __init__(self, parent):

        super().__init__(parent)
        history_ui = './ui/history_ui.ui'
        uic.loadUi(history_ui, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.clear_button.clicked.connect(self.history_list.clear)
        self.close_button.clicked.connect(lambda: parent.history_button.setChecked(False))
        self.aot_button.toggled.connect(self.always_on_top)

        def move_window(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.drag_pos)
                self.drag_pos = event.globalPos()
                event.accept()
        self.title_bar.mouseMoveEvent = move_window

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()

    def always_on_top(self):
        """
        Sets window staying on top or not.
        """

        if self.aot_button.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SelectorUi()
    ex.show()
    sys.exit(app.exec_())
