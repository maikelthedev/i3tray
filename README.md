# i3tray system tray to change layouts

I am really liking literate programming so I wrote this python script using my own Literate Programming implementation in Fish shell [here](https://github.com/maikeldotuk/literatefish) which I wrote yesterday night.

First be aware I'm importing libraries than I use because I haven't yet cleaned up what I don't really need. This whole thing is still **in the experimental**. That doesn't stop you from forking it.

Using [LiterateFish](https://github.com/maikeldotuk/literatefish) you can both execute and upgrade this file as it contains instructions in both Python and Bash and my little crappy function distinguishes them.

### To install this

```bash
git clone git@github.com:maikeldotuk/i3tray.git
cd i3tray
pip install -r requirements.txt
```
### To run it:

```none
litrun README.md python
```

### To update it

From the parent folder where installed it just type this and press Return
```none
litrun README.md bash
```
That will run the bash code (and only that code) inside the section 'to install it'

### AUR package.

I will publish a package in the Arch AUR as soon as this stop being experimental for everybody to freely share the joy of having a bit more of mouse functionality in i3. Bear with me while I finish it. Most of what needs to be done is in the comments below.

This is the Python code
```python
import sys
import os
import subprocess
import pprint
import json
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, qApp
from PyQt5 import QtCore
from functools import partial
```
This is just laziness, I'm assuming the first loaded layout is the netflix one because I don't have the time right now to bother.

What this should do is?
* Detect the layout currently in use.
	For this it will need to have a way to figure it, by taking the respones from i3 get_tree or similar. I'm still figuring this out.
* Assing it to the program when it's first run.

```python
current_layout = 'netflix.layout'
```

This gets all the layouts assuming they are in such folder. Obviously this will need to be configured better. Pending is:
1. Detect the config folder dependingo the linux distro?
2. Create the config folder if it doesn't exist.
3. Tell the user if there are no layouts found, in which case this whole thing is useless.

```python
def get_layouts():
    layouts = []
    for file in os.listdir():
        if (file.split('.')[1] == 'layout'):
            layouts.append(file)
    return layouts
```
We need to detect the current windows in the currently focused workspace so we can later move them in place. I need to figure a way to do this within Python, not depending of a subprocess.
```python
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
```
Xdotool does the job so far, so I didn't think on reimplementing it. Again, as before it will make sense if I find a way to do it all without leaving Python nor depending on external tools but...it is there any reason to do it all from within Python?

This does two things, I should break it in two functions instead. The two things are:
1. Take all the windows out of the view so they can be placed inside the placeholders
2. Show all the windows again but this time inside their placeholders. i3 behaviour by default would be to place them as if they were new windows.

```python
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
```

Right, so this is the one that does the magic. Considering we have the layouts as, for example "grid4windows.layout" in a folder with name FOLDER, use that as the filename. But do it in this order:
1. Get the current windows of the current desktop IDs, before doing any changes.
2. Append the layout.
3. Move the windows you got from 1 (which means, this doesn't include the newly created placeholders) back into view, hence inside the placeholders.

```python
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
```
Basically read the layout file names, strip them from their ".layout" name and add them as items of the menu in the SysTrayIcon.
```python
def add_layouts_to_tray(layouts, menu):
    for layout in layouts:
        layout_name = layout.split('.')[0]
        action = menu.addAction(layout_name)
        action.triggered.connect(partial(change_layout, layout))
```
What I'm trying to accomplish here is to cycle through the layouts as the user left-clicks on the system tray icon. One very important consideration here I have not implemented yet is to give meaningful icons to each layout, same as in AwesomeVM (I might just copy their icons).
```python
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

```
Got to change the name of this function. Also, I don't need self.
```python
def on_systray_activated(self):
    buttons = qApp.mouseButtons()
    if buttons & QtCore.Qt.RightButton:
        print('right-button')
    if buttons & QtCore.Qt.LeftButton:
        print('left-button')
        cycle_through_layouts()

```
This simply creates the systemtray icon, this class needs to be heavily cleaned up. Also, do I need a class at all for this?
```python
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
```
This allows this app to run just called from the command line, but I would implement [@cli](https://pypi.org/project/pyCLI/) at some point to be able to run it properly and with arguments.
```python
def main():
    app = QApplication(sys.argv)
    w = QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("icon.ico"), w)
    trayIcon.show()
#    trayIcon.showMessage('Hello', "Hello again")
    trayIcon.activated.connect(on_systray_activated)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
```
