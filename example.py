from PyQt5.QtWidgets import QApplication, QWidget, QMenu, qApp
from PyQt5.QtGui import QIcon
import sys
import pyautogui


def shit():
    print('I shit you not')


def menu_is_hidden():
    print('Menu has hidden')


def get_mouse_position():
    return pyautogui.position()


def main():
    app = QApplication(sys.argv)
    widget = QWidget()
    if 'show' in sys.argv:
        show_menu(QMenu(widget))
    if 'tray' in sys.argv:
        print('tray version')
        quit()
    if len(sys.argv) == 1:
        quit()
    sys.exit(app.exec_())


def show_menu(menu):
    menu.addAction('I shit you not')
    closeAction = menu.addAction('Close')
    closeAction.triggered.connect(qApp.quit)
    menu.aboutToHide.connect(qApp.quit)
    menu.addAction('I shit you not')
    menu.addAction('I shit you not')
    menu.addSeparator()
    menu.addAction('I shit you not')
    menu.addAction('I shit you not')
    icon = QIcon('icon.ico')
    menu.addAction(icon, 'Hoho')
    location = get_mouse_position()
    menu.move(location.x, location.y)
    menu.show()


if __name__ == '__main__':
    main()
