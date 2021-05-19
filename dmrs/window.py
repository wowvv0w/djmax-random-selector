import os
from PyQt5 import uic
from PyQt5.QtWidgets import QCheckBox, QDialog, QSizePolicy, QSpacerItem, QVBoxLayout
from PyQt5.QtCore import Qt
from . import data

SETTING_UI = './ui/setting.ui'
HISTORY_UI = './ui/history.ui'
FAVORITE_UI = './ui/favorite.ui'
PRESET_UI = './ui/preset.ui'

class SettingUi(QDialog):
    """
    SETTING Window
    """

    def __init__(self, parent):

        super().__init__(parent)
        uic.loadUi(SETTING_UI, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.apply_button.clicked.connect(lambda: self.apply(parent))
        self.cancel_button.clicked.connect(lambda: self.cancel(parent))

        self.current_ver, self.lastest_ver = parent.db_curr_ver, parent.db_last_ver
        self.dlc_packs = [
            ('VE', self.yd_cb_ve), ('ES', self.yd_cb_es), ('TR', self.yd_cb_tr), ('GC', self.yd_cb_gc),
            ('CE', self.yd_cb_ce), ('BS', self.yd_cb_bs), ('DM', self.yd_cb_dm), ('CY', self.yd_cb_cy),
            ('T1', self.yd_cb_t1), ('T2', self.yd_cb_t2), ('T3', self.yd_cb_t3),  
            ('GF', self.yd_cb_gf), ('CHU', self.yd_cb_chu), ('P3', self.yd_cb_p3)
            ]

    def show_setting_ui(self, parent):
        """
        Shows 'SETTING' window.
        """

        parent.lock_all.move(0, 0)

        for val, cb in self.dlc_packs:
            cb.setChecked(val in parent.enabled_check)
        
        self.current_label.setText(f'Current: {self.current_ver}')
        self.lastest_label.setText(f'Lastest: {self.lastest_ver}')
        if self.current_ver < self.lastest_ver:
            self.lastest_label.setStyleSheet('color: #ffbe00;\nfont: 15px')
        else:
            self.lastest_label.setStyleSheet('color: #dddddd;\nfont: 15px')

        self.show()

    def apply(self, parent):
        """
        Modifies data.
        """

        if self.current_ver < self.lastest_ver:
            data.update_database()
            data.update_version(parent.rs_curr_ver, self.lastest_ver)
            _, _, self.current_ver, self.lastest_ver = data.update_check()

        fil_yd_sr = set(val for val, cb in self.dlc_packs if cb.isChecked())
        fil_yd_sr.update(['RP', 'P1', 'P2', 'GG'])
        data.edit_data(fil_yd_sr, parent.IS_TEST)
        parent.yourdata = data.read_data(parent.IS_TEST)
        parent.enabled_check = set(parent.yourdata['Series'].values)

        data.lock_series(parent.categories, parent.enabled_check)

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
        uic.loadUi(HISTORY_UI, self)
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




class FavoriteUi(QDialog):
    """
    Favorite Window
    """

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(FAVORITE_UI, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.apply_button.clicked.connect(lambda: self.apply(parent))
        self.cancel_button.clicked.connect(lambda: self.cancel(parent))
        self.favor_search.textChanged.connect(self.update_display)
        self.favor_all.clicked.connect(self.update_abled)
        self.favor_ena.clicked.connect(self.update_abled)
        self.favor_dis.clicked.connect(self.update_abled)

        self.controls_layout = QVBoxLayout()
        all_track_title = data.generate_title_list()
        self.widgets = []

        self.show_enabled = True
        self.show_disabled = True

        for name in all_track_title:
            item = QCheckBox(text=name)
            self.controls_layout.addWidget(item)
            self.widgets.append(item)
        
        spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controls_layout.addItem(spacer)
        self.favor_list.setLayout(self.controls_layout)

    
    def show_favorite_ui(self, parent):
        """
        Shows 'FAVORITE' window.
        """

        parent.lock_all.move(0, 0)
        
        for widget in self.widgets:
            widget.setChecked(widget.text() in parent.favorite)
        self.favor_black.setChecked(parent.is_favor_black)
        self.update_display(self.favor_search.text())

        self.show()

    def update_display(self, text):
        """
        Shows search results.
        """

        for widget in self.widgets:
            check = (widget.isChecked() and self.show_enabled) \
                or (not widget.isChecked() and self.show_disabled)
            if check:
                title = widget.text()
                if text.lower() in title.lower():
                    widget.setVisible(True)
                else:
                    widget.setVisible(False)
            else:
                widget.setVisible(False)
            
            
    def update_abled(self):
        """
        Applies on/off filter.
        """

        if self.favor_all.isChecked():
            self.show_enabled, self.show_disabled = True, True
        else:
            self.show_enabled = self.favor_ena.isChecked()
            self.show_disabled = self.favor_dis.isChecked()
        self.update_display(self.favor_search.text())
        
    
    def apply(self, parent):
        """

        """
       
        parent.favorite = {widget.text() for widget in self.widgets if widget.isChecked()}
        parent.is_favor_black = self.favor_black.isChecked()
        print(parent.favorite)
        parent.lock_all.move(0, -540)
        parent.filtering()
        parent.erm_initialize()
        self.close()

    def cancel(self, parent):
        """
        Cancels editing and closes window.
        """

        parent.lock_all.move(0, -540)
        self.close()




class PresetUi(QDialog):
    """
    Preset Window
    """

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(PRESET_UI, self)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.close_button.clicked.connect(lambda: self.close_preset_ui(parent))

        self.preset_list = self.read_preset()
        self.file = lambda name: f'./data/presets/{name}.json'

        for preset in self.preset_list:
            preset = preset.removesuffix('.json')
            self.preset_box.addItem(preset)

        # self.preset_add.clicked.connect()
        self.preset_remove.clicked.connect(self.remove_preset)
        self.preset_apply.clicked.connect(lambda: self.apply_preset(parent))
        self.preset_create.clicked.connect(lambda: self.create_preset(parent))

    def read_preset(self):
        list_ = os.listdir(data.PRESET_PATH)
        list_json = [file for file in list_ if file.endswith('.json')]

        return list_json

    def show_preset_ui(self, parent):
        """
        Shows 'PRESET' window.
        """

        parent.lock_all.move(0, 0)
        self.show()


    def remove_preset(self):
        row = self.preset_box.currentRow()
        item = self.preset_box.currentItem()
        name = item.text()

        self.preset_box.takeItem(row)
        self.preset_list.remove(name)

        file = self.file(name)
        if os.path.isfile(file):
            os.remove(file)
    
    def apply_preset(self, parent):
        item = self.preset_box.currentItem()
        name = item.text()
        data.import_config(parent, self.file(name))
    
    def create_preset(self, parent):
        name = self.preset_name.text()
        if name in self.preset_list:
            num = 1
            while 1:
                clone = f'{name}_{num}'
                if clone in self.preset_list:
                    num += 1
                    continue
                else:
                    name = clone
                    break
        data.export_config(parent, self.file(name))
        self.preset_list.append(name)
        self.preset_box.addItem(name)


    def close_preset_ui(self, parent):
        """
        closes window.
        """

        parent.lock_all.move(0, -540)
        self.close()