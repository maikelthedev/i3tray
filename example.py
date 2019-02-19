from PyQt5.QtWidgets import QApplication, QWidget, QMenu, qApp
import sys


def shit():
    print('I shit you not')


def main():
    app = QApplication([])
    widget = QWidget()
    menu = QMenu(widget)
    menu.addAction('I shit you not')
    menu.addAction('I shit you not')
    closeAction = menu.addAction('Close')
    closeAction.triggered.connect(qApp.quit)
    menu.show()
    menu.leaveEvent(shit)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
