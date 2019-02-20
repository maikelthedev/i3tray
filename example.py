from PyQt5.QtWidgets import QApplication, QWidget, QMenu, qApp
import sys
import pyautogui


def shit():
    print('I shit you not')


def menu_is_hidden():
    print('Menu has hidden')


def get_mouse_position():
    return pyautogui.position()


def main():
    app = QApplication([])
    widget = QWidget()
    menu = QMenu(widget)
    menu.addAction('I shit you not')
    closeAction = menu.addAction('Close')
    closeAction.triggered.connect(qApp.quit)
    menu.aboutToHide.connect(qApp.quit)
    # How to show it where the mouse pointer is?
    menu.setTitle('meeeeeh')
    location = get_mouse_position()
    menu.move(location.x, location.y)
    menu.addSection('hello')
    menu.addAction('I shit you not')
    menu.addAction('I shit you not')
    menu.addSeparator()
    menu.addAction('I shit you not')
    menu.addAction('I shit you not')
    menu.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
