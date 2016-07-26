from __future__ import print_function # python2-python3 compatibility
from imp import load_source
from os.path import join, dirname
from sys import platform, argv
from math import sqrt, sin, cos, radians
try: import Tkinter as tk
except: import tkinter as tk

ICON_PATH = join(dirname(argv[0]), 'walabot-icon.png')
IMAGE_PATH = join(dirname(argv[0]), 'piano-keys.gif')
CONNECT_WALABOT_PATH = join(dirname(argv[0]), 'connect-walabot.gif')
APP_X, APP_Y = 100, 100 # (x, y) of left corner of the window (in pixels)
R_MIN, R_MAX, R_RES = 10, 30, 5 # walabot SetArenaR values
THETA_MIN, THETA_MAX, THETA_RES = -30, 30, 5 # walabot SetArenaTheta values
PHI_MIN, PHI_MAX, PHI_RES = -30, 30, 5 # walabot SetArenaPhi values
TSHLD = 5 # walabot SetThreshold value
PIANO_RATIO = 1
X_MAX = R_MAX * sin(radians(THETA_MAX))
Y_MAX = R_MAX * cos(radians(THETA_MAX)) * sin(radians(PHI_MAX))
Z_MAX = R_MAX * cos(radians(THETA_MAX)) * cos(radians(PHI_MAX))
PIANO_AXES_ARENA = tuple(PIANO_RATIO * n for n in [X_MAX, Y_MAX, Z_MAX])

class MainGUI(tk.Label):
    def __init__(self, master):
        self.img = tk.PhotoImage(file=IMAGE_PATH)
        tk.Label.__init__(self, master, image=self.img)
        self.wlbt = Walabot(self)
        self.alertIfWalabotIsNotConnected(self)
        self.wlbt.setParametersAndStart()
        self.after_idle(self.detectTargetAndReply)
    def alertIfWalabotIsNotConnected(self, master):
        connectWalabotImage = tk.PhotoImage(file=CONNECT_WALABOT_PATH)
        connectWalabotLabel = tk.Label(master, image=connectWalabotImage)
        while not self.wlbt.isConnected():
            connectWalabotLabel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update_idletasks()
    def detectTargetAndReply(self):
        self.after_idle(self.detectTargetAndReply)
        coordinates = self.wlbt.getClosestTargetCoordinates()
        if not coordinates: return # no targets were found
        xValue, yValue, zValue = coordinates[0], coordinates[1], coordinates[2]
        if self.inPianoArena(1, yValue) and self.inPianoArena(2, zValue):
            if self.inPianoArena(0, xValue):
                self.pressAndPlayKey(yValue)
            else:
                self.highlightKey(yValue)
        else:
            self.resetPianoImage()
    def inPianoArena(self, axis, n):
        if abs(n) <= PIANO_AXES_ARENA[axis]:
            return True
        return False
    def pressAndPlayKey(self, yValue):
        # TODO: change image to pressed key, play sound
        print('Press:', int(yValue))
    def highlightKey(self, yValue):
        # TODO: change image to highlight
        print('Highlight:', int(yValue))
    def resetPianoImage(self):
        print('Reset')

class Walabot:
    def __init__(self, master):
        self.master = master
        if platform == 'win32': # for windows
            path = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK',
                'python')
        else: # for linux, raspberry pi, etc.
            path = join('/usr', 'share', 'walabot', 'python')
        self.wlbt = load_source('WalabotAPI', join(path, 'WalabotAPI.py'))
        self.wlbt.Init()
        self.wlbt.SetSettingsFolder()
        self.distance = lambda t: sqrt(t.xPosCm**2 + t.yPosCm**2 + t.zPosCm**2)
    def isConnected(self):
        try:
            self.wlbt.ConnectAny()
        except self.wlbt.WalabotError as err:
            if err.code == 19: # 'WALABOT_INSTRUMENT_NOT_FOUND'
                return False
        return True
    def setParametersAndStart(self):
        self.wlbt.SetProfile(self.wlbt.PROF_SENSOR)
        self.wlbt.SetArenaR(R_MIN, R_MAX, R_RES)
        self.wlbt.SetArenaTheta(THETA_MIN, THETA_MAX, THETA_RES)
        self.wlbt.SetArenaPhi(PHI_MIN, PHI_MAX, PHI_RES)
        self.wlbt.SetThreshold(TSHLD)
        self.wlbt.SetDynamicImageFilter(self.wlbt.FILTER_TYPE_MTI)
        self.wlbt.Start()
    def getClosestTargetCoordinates(self):
        self.wlbt.Trigger()
        targets = self.wlbt.GetSensorTargets()
        if targets:
            target = max(targets, key=self.distance)
            return target.xPosCm, target.yPosCm, target.zPosCm

def configureWindow(root):
    """ Set configurations for the GUI window, such as icon, title, etc.
    """
    root.title('Walabot - Piano Gestures')
    iconPath = join(dirname(argv[0]), 'walabot-icon.png')
    iconFile = tk.PhotoImage(file=iconPath)
    root.tk.call('wm', 'iconphoto', root._w, iconFile) # set app icon
    root.geometry('+{}+{}'.format(APP_X, APP_Y))
    root.resizable(width=False, height=False)

def startApp():
    """ Main function.
    """ # TODO: add func documentation.
    root = tk.Tk()
    configureWindow(root)
    MainGUI(root).pack()
    root.mainloop()

if __name__ == '__main__':
    startApp()
