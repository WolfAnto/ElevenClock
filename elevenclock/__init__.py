from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import winreg, locale



import time, sys, threading, datetime, webbrowser
from pynput.keyboard import Controller, Key

lastTheme = 0
seconddoubleclick = False

def readRegedit(aKey, sKey, default, storage=winreg.HKEY_CURRENT_USER):
    registry = winreg.ConnectRegistry(None, storage)
    reg_keypath = aKey
    try:
        reg_key = winreg.OpenKey(registry, reg_keypath)
    except FileNotFoundError as e:
        print(e)
        return default

    for i in range(1024):
        try:
            value_name, value, _ = winreg.EnumValue(reg_key, i)
            if value_name == sKey:
                return value
        except OSError as e:
            print(e)
            return default


#get system locale and formats and setting them up

locale.setlocale(locale.LC_ALL, readRegedit(r"Control Panel\International", "LocaleName", "en_US"))
dateTimeFormat = "%H:%M\n%d/%m/%Y"

dateMode = readRegedit(r"Control Panel\International", "sShortDate", "dd/MM/yyyy")
dateMode = dateMode.replace("dd", "%d").replace("d", "%d").replace("MMM", "%b").replace("MM", "%m").replace("M", "%m").replace("yyyy", "%Y").replace("yy", "%y")

timeMode = readRegedit(r"Control Panel\International", "sShortTime", "H:mm")
timeMode = timeMode.replace("HH", "%H").replace("H", "%H").replace("mm", "%M").replace("m", "%M")

dateTimeFormat = dateTimeFormat.replace("%d/%m/%Y", dateMode).replace("%H:%M", timeMode)




class Clock(QMainWindow):
    refresh = Signal()
    def __init__(self, w, h, dpix, dpiy):
        super().__init__()
        self.refresh.connect(self.refreshandShow)
        self.keyboard = Controller()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.Tool)
        self.move(w-(86*dpix), h-(48*dpiy))
        self.resize(72*dpix, 48*dpiy)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.01);margin: 5px; border-radius: 5px;")
        self.label = Label(datetime.datetime.now().strftime(dateTimeFormat))
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if(readRegedit(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme",  1) == 0):
            lastTheme = 0
            self.label.setStyleSheet("padding: 1px; color: white; font-family: \"Segoe UI Variable\"; font-weight: bold;")
        else:
            lastTheme = 1
            self.label.setStyleSheet("padding: 1px; color: black; font-family: \"Segoe UI Variable\"; font-weight: bold;")
        self.label.clicked.connect(lambda: self.showCalendar())
        self.setCentralWidget(self.label)
        threading.Thread(target=self.fivesecsloop, daemon=True).start()
        self.show()
        self.raise_()
        self.setFocus()
        
    def fivesecsloop(self):
        while True:
            time.sleep(1)
            self.refresh.emit()
        
    def showCalendar(self):
        self.keyboard.press(Key.cmd)
        self.keyboard.press('n')
        self.keyboard.release('n')
        self.keyboard.release(Key.cmd)
        
    def refreshandShow(self):
        global lastTheme
        self.show()
        self.raise_()
        theme = readRegedit(r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", 1)
        if(theme != lastTheme):
            if(theme == 0):
                lastTheme = 0
                self.label.setStyleSheet("padding: 1px; color: white; font-family: \"Segoe UI Variable\"; font-weight: bold;")
            else:
                lastTheme = 1
                self.label.setStyleSheet("padding: 1px; color: black; font-family: \"Segoe UI Variable\"; font-weight: bold;")
            
        self.label.setText(datetime.datetime.now().strftime(dateTimeFormat))
        
    
    def closeEvent(self, event: QCloseEvent) -> None:
        sys.exit()
        return super().closeEvent(event)
        
class Label(QLabel):
    clicked = Signal()
    def __init__(self, text):
        super().__init__(text)
        
    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()
        return super().mouseReleaseEvent(ev)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:

        def toggleSeconddoubleclick():
            global seconddoubleclick
            time.sleep(1)
            seconddoubleclick = False
            
        global seconddoubleclick
        if(seconddoubleclick):
            webbrowser.open("http://www.somepythonthings.tk/redirect/?elevenclock")
        else:
            seconddoubleclick = True
            threading.Thread(target=toggleSeconddoubleclick).start()
        return super().mouseDoubleClickEvent(event)
        

QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)

app = QApplication()
wins = []
firstWinSkipped = False
for screen in app.screens():
    if(firstWinSkipped):
        wins.append(Clock(screen.geometry().x()+screen.geometry().width(), screen.geometry().y()+screen.geometry().height(), screen.logicalDotsPerInchX()/96, screen.logicalDotsPerInchY()/96))
    else: # Skip the primary display, as it has already the clock
        firstWinSkipped = True
app.exec_()
sys.exit(0)