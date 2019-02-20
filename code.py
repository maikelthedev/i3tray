import pyautogui
from PyQt5.QtGui import QIcon
import sys
import os
import subprocess
import json
from PyQt5 import QtCore
from functools import partial
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, qApp


LAYOUTS_FOLDER = os.getenv('HOME') + '/dotfiles/layouts/'
current_layout = 'netflix.layout'
current_icon = LAYOUTS_FOLDER + 'netflix.png'


def get_layouts():
    layouts = []
    for file in os.listdir(LAYOUTS_FOLDER):
        if (file.split('.')[1] == 'layout'):
            layouts.append(file)
    return layouts


def get_windows():
    processes_raw = subprocess.check_output(['wmctrl', '-l']).strip()
    separated = processes_raw.split(b'\n')
    desktop_number = subprocess.check_output(
        ['xdotool', 'get_desktop']).strip()
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
    location_of_layout = LAYOUTS_FOLDER + layout
    with open(location_of_layout) as json_file:
        data = json.load(json_file)
        min_win = len(str(data).split('class')) - 1
    total = len(windows)
    if total < min_win:
        for runagain in range(0, min_win-total):
            subprocess.check_output(['xfce4-terminal'])


def change_layout(layout):
    windows = get_windows()
    file = LAYOUTS_FOLDER + layout
    subprocess.check_output(['i3',
                             'append_layout',
                             file,
                             ]).strip()
    reposition_windows(windows, layout)
    global current_layout
    current_layout = layout


def add_layouts_to_tray(layouts, menu):
    for layout in layouts:
        layout_name = layout.split('.')[0]
        icon_location = LAYOUTS_FOLDER + layout_name + '.png'
        icon = QIcon(icon_location)
        # As this stand each layout MUST have an icon with the same name.png
        action = menu.addAction(icon, layout_name)
        action.triggered.connect(partial(change_layout, layout))


def cycle_through_layouts():
    layouts = get_layouts()
    which_index = layouts.index(current_layout)
    total = len(layouts)
    next_index = which_index+1
    if (which_index+1 > total - 1):
        next_index = 0
    next_layout = layouts[next_index]
    change_layout(next_layout)


def on_systray_activated(tray):
    buttons = qApp.mouseButtons()
    if buttons & QtCore.Qt.RightButton:
        qApp.quit()
    if buttons & QtCore.Qt.LeftButton:
        cycle_through_layouts()
        change_tray_icon(tray)


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QSystemTrayIcon.__init__(self, icon, parent)


def get_mouse_position():
    return pyautogui.position()


def change_tray_icon(tray):
    icon = LAYOUTS_FOLDER + current_layout + '.png'
    icon = icon.replace('.layout', '')
    tray.setIcon(QIcon(icon))


def main():
    app = QApplication(sys.argv)
    widget = QWidget()
    if 'show' in sys.argv:
        show_menu(QMenu(widget))
    if 'tray' in sys.argv:
        trayIcon = SystemTrayIcon(QIcon(current_icon), widget)
        trayIcon.show()
        trayIcon.activated.connect(partial(on_systray_activated, trayIcon))
    if len(sys.argv) == 1:
        quit()
    sys.exit(app.exec_())


def show_menu(menu):
    icon = QIcon(current_icon)
    test = menu.addAction(icon, 'Layouts')
    menu.addSeparator()
    test.setEnabled(False)
    layouts = get_layouts()
    add_layouts_to_tray(layouts, menu)
    menu.addSeparator()
    menu.aboutToHide.connect(qApp.quit)
    location = get_mouse_position()
    menu.move(location.x, location.y)
    menu.show()


if __name__ == '__main__':
    main()
