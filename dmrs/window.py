import os
import shutil
from PyQt5 import uic
from PyQt5.QtWidgets import QCheckBox, QDialog, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem, QVBoxLayout
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
        self.parent_ = parent
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.apply_button.clicked.connect(self.apply)
        self.cancel_button.clicked.connect(self.close)

        self.current_ver, self.lastest_ver = self.parent_.db_curr_ver, self.parent_.db_last_ver
        self.dlc_packs = [
            ('VE', self.yd_cb_ve), ('ES', self.yd_cb_es), ('TR', self.yd_cb_tr), ('GC', self.yd_cb_gc),
            ('CE', self.yd_cb_ce), ('BS', self.yd_cb_bs), ('DM', self.yd_cb_dm), ('CY', self.yd_cb_cy),
            ('T1', self.yd_cb_t1), ('T2', self.yd_cb_t2), ('T3', self.yd_cb_t3),  
            ('GF', self.yd_cb_gf), ('CHU', self.yd_cb_chu), ('P3', self.yd_cb_p3)
            ]

    @data.filtering
    def apply(self):
        """
        Modifies data.
        """

        if self.current_ver < self.lastest_ver:
            data.update_database()
            data.update_version(self.parent_.rs_curr_ver, self.lastest_ver)
            _, _, self.current_ver, self.lastest_ver = data.update_check()

        fil_yd_sr = set(val for val, cb in self.dlc_packs if cb.isChecked())
        fil_yd_sr.update(['RP', 'P1', 'P2', 'GG'])
        data.edit_data(fil_yd_sr, self.parent_.IS_TEST)
        self.parent_.yourdata = data.read_data(self.parent_.IS_TEST)
        self.parent_.enabled_check = set(self.parent_.yourdata['Series'].values)

        data.lock_series(self.parent_.categories, self.parent_.enabled_check)

        self.close()

    def showEvent(self, _):
        self.parent_.lock_all.move(0, 0)

        for val, cb in self.dlc_packs:
            cb.setChecked(val in self.parent_.enabled_check)
        
        self.current_label.setText(f'Current: {self.current_ver}')
        self.lastest_label.setText(f'Lastest: {self.lastest_ver}')
        if self.current_ver < self.lastest_ver:
            self.lastest_label.setStyleSheet('color: #ffbe00;\nfont: 15px')
        else:
            self.lastest_label.setStyleSheet('color: #dddddd;\nfont: 15px')

    def closeEvent(self, _):
        self.parent_.lock_all.move(0, -540)
    
    def reject(self):
        self.parent_.lock_all.move(0, -540)
        super().reject()




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
        self.parent_ = parent
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.apply_button.clicked.connect(self.apply)
        self.cancel_button.clicked.connect(self.close)
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
        
    @data.filtering
    def apply(self):
        """

        """
       
        self.parent_.favorite = {widget.text() for widget in self.widgets if widget.isChecked()}
        self.parent_.is_favor_black = self.favor_black.isChecked()
        print(self.parent_.favorite)
        self.close()

    def showEvent(self, _):
        self.parent_.lock_all.move(0, 0)
        
        for widget in self.widgets:
            widget.setChecked(widget.text() in self.parent_.favorite)
        self.favor_black.setChecked(self.parent_.is_favor_black)
        self.update_display(self.favor_search.text())

    def closeEvent(self, _):
        self.parent_.lock_all.move(0, -540)
    
    def reject(self):
        self.parent_.lock_all.move(0, -540)
        super().reject()




# def _update_preset(func):
    
#     def wrapper(self: PresetUi, add: str = '', del: Tuple[str, int] = ()):
#         if add:
#             self.preset_list.append(add)
#             self.preset_box.addItem(add)
#         if del:
#             self.preset_list.remove(del[0])
#             self.preset_box.takeItem(del[1])


class PresetUi(QDialog):
    """
    Preset Window
    """

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(PRESET_UI, self)
        self.parent_ = parent
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.close_button.clicked.connect(self.close)

        self.preset_list = self.read_preset()
        self.file = lambda name: f'./data/presets/{name}.json'

        for preset in self.preset_list:
            self.preset_box.addItem(preset)

        self.preset_add.clicked.connect(self.add_preset)
        self.preset_remove.clicked.connect(self.remove_preset)
        self.preset_apply.clicked.connect(self.apply_preset)
        self.preset_rename.clicked.connect(self.rename_preset)
        self.preset_create.clicked.connect(self.create_preset)

    def read_preset(self):
        list_ = os.listdir(data.PRESET_PATH)
        list_json = [file.removesuffix('.json') for file in list_ if file.endswith('.json')]

        return list_json


    def add_preset(self):
        file = QFileDialog.getOpenFileName(self, 'Add Preset', '/home', 'Json Files(*.json)')
        try:
            if not data.check_config(file[0]):
                QMessageBox.critical(self, 'Failed', 'This JSON Document is not for me.')
                return
        except FileNotFoundError:
            return
        json_ = file[0].removesuffix('.json')
        index = json_.rfind('/')
        name = json_[index+1:]
        name = self.generate_clone(name)
        file_copy = self.file(name)
        
        self.preset_list.append(name)
        self.preset_box.addItem(name)
        shutil.copy(file[0], file_copy)

    def remove_preset(self):
        msg = QMessageBox.warning(self, 'Remove Preset', 'Are you sure to remove it?', QMessageBox.Yes | QMessageBox.No)
        if msg == QMessageBox.No:
            return
        row = self.preset_box.currentRow()
        item = self.preset_box.currentItem()
        name = item.text()

        self.preset_box.takeItem(row)
        self.preset_list.remove(name)

        file = self.file(name)
        if os.path.isfile(file):
            os.remove(file)
    
    def apply_preset(self):
        item = self.preset_box.currentItem()
        name = item.text()
        data.import_config(self.parent_, self.file(name))
    
    def rename_preset(self):
        item = self.preset_box.currentItem()
        bname = item.text()
        text = self.preset_name.text()
        aname = self.generate_clone(text)
        before = self.file(bname)
        after = self.file(aname)

        item.setText(aname)
        self.preset_list.remove(bname)
        self.preset_list.append(aname)
        try:
            os.rename(before, after)
        except FileExistsError:
            pass
    
    def create_preset(self):
        text = self.preset_name.text()
        name = self.generate_clone(text)

        data.export_config(self.parent_, self.file(name))
        self.preset_list.append(name)
        self.preset_box.addItem(name)

    def generate_clone(self, name):
        if name in self.preset_list:
            num = 1
            clone = name
            while clone in self.preset_list:
                clone = f'{name}_{num}'
                num += 1
            name = clone
        return name

    def showEvent(self, _):
        self.parent_.lock_all.move(0, 0)

    def closeEvent(self, _):
        self.parent_.lock_all.move(0, -540)

    def reject(self):
        self.parent_.lock_all.move(0, -540)
        super().reject()