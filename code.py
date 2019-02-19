import sys
import os
import subprocess
import pprint
import json
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, qApp
from PyQt5 import QtCore
from functools import partial


def get_layouts():
    layouts = []
    for file in os.listdir():
        if (file.split('.')[1] == 'layout'):
            layouts.append(file)
    return layouts


def get_windows():
    processes_raw = subprocess.check_output(['wmctrl', '-l']).strip()
    separated = processes_raw.split(b'\n')
    desktop_number = subprocess.check_output(
        ['wmctrl', '-d']).strip().split()[0]
    programs = []
    for program in separated:
        if (program.split()[1] == desktop_number):
            programs.append(program.split()[0])
    return programs


def reposition_windows(windows, layout):
    for window in windows:
        subprocess.check_output(['xdotool', 'windowunmap', window])
        subprocess.check_output(['xdotool', 'windowmap', window])
    min_win = 0
    location_of_layout = os.getenv('HOME') + '/dotfiles/layouts/' + layout
    with open(location_of_layout) as json_file:
        data = json.load(json_file)
        min_win = len(str(data).split('class')) - 1
    total = len(windows)
    if total < min_win:
        for runagain in range(0, min_win-total):
            subprocess.check_output(['xfce4-terminal'])


def change_layout(layout):
    windows = get_windows()
    file = '~/dotfiles/layouts/' + layout
    result = subprocess.check_output(['i3',
                                      'append_layout',
                                      file,
                                      ]).strip()
    reposition_windows(windows, layout)
    global current_layout
    current_layout = layout
    print(result)


def add_layouts_to_tray(layouts, menu):
    for layout in layouts:
        layout_name = layout.split('.')[0]
        action = menu.addAction(layout_name)
        action.triggered.connect(partial(change_layout, layout))


def cycle_through_layouts():
    layouts = get_layouts()
    print(current_layout)
    which_index = layouts.index(current_layout)
    print(which_index)
    total = len(layouts)
    print('total')
    print(total)
    next_index = which_index+1
    print('next_index')
    print(next_index)
    if (which_index+1 > total - 1):
        next_index = 0
    next_layout = layouts[next_index]
    change_layout(next_layout)


def on_systray_activated(self):
    buttons = qApp.mouseButtons()
    if buttons & QtCore.Qt.RightButton:
        print('right-button')
    if buttons & QtCore.Qt.LeftButton:
        print('left-button')
        cycle_through_layouts()


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)
        icon = QtGui.QIcon("icon.ico")
        menu.addSeparator()
        layouts = get_layouts()
        add_layouts_to_tray(layouts, menu)
        menu.addSeparator()
        closeAction = menu.addAction(icon, "&Close")
        closeAction.triggered.connect(qApp.quit)
        self.setContextMenu(menu)
        self.setToolTip("Tooltip")


def main():
    app = QApplication(sys.argv)
    w = QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("icon.ico"), w)
    trayIcon.show()
    trayIcon.activated.connect(on_systray_activated)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
