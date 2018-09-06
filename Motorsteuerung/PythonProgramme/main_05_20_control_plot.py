__author__ = 'alexander_stramma'
################################
# =trennt Unterprogramme und Klassen
#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
# =moegliche Aenderungen (je nach benutztem Betriebssystem und Python-Version) notwendig

##########################################################
# Bibliotheken reinladen
# WX = graphische Benutzeroberflaeche https://wiki.wxpython.org/action/show/FrontPage?action=show&redirect=StartSeite
# numpy = numerische Berechnungen
# matplotlib = Plotten
# serial = serielle Schnittstelle http://matplotlib.org/contents.html

import wx
from wx.lib.splitter import MultiSplitterWindow
import serial
import numpy as np
import matplotlib
#*#*#*#*#*#*#*#*#*#*#*
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import  Polygon
from matplotlib.collections import PatchCollection


##########################################################
# falls unklar ist welche Backends vom Rechner unterstuetzt werden, Befehl unten ausfuehren
# danach in matplotlib.use ausprobieren, welches am besten laeuft
# import matplotlib.rcsetup as rcsetup
# print(rcsetup.all_backends)
##########################################################
# Klasse, die eigentliche Steuerung mit Pfeiltasten beinhaltet sowie X-Bee Kommunikation initialisert
class Controlpanel(wx.Panel):
    # initialisiert serielle Verbindung durch X-Bee

    #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
    # Arduino Programm am Computer oeffnen -> Werkzeuge -> Ports, und entsprechenden Port hier angebben
    arduino_port = "/dev/ttyACM0"
    #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
    # Baudrate muss mit hochgeladenem Arduino-Programm uebereinstimmen, sonst nur Hiroglyphen empfangbar
    arduino_baud = 57600
    global ser
    #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
    # Muss mit X-Bee Konfiguration in xctung uebereinstimmen
    ser = serial.Serial(
        port=arduino_port,
        baudrate=arduino_baud,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0,
    )

    # Erzeugt Cpntrolpanel
    def __init__(self, parent):

        #
        String = 'rf'
        global lastCommand
        lastCommand = list(String)

        # Array fuer Motordaten und Richtung
        global MotorSet
        MotorSet = [0, 0, 0, 0]
        global Direction
        Direction = 1    # 1 vorwaerts, -1 rueckwaerts

        wx.Panel.__init__(self, parent)
        # Bilder (Pfeile) reinladen
        arrowleftblack = wx.Bitmap('arrow-left.bmp', wx.BITMAP_TYPE_BMP,)
        arrowleftgrey = wx.Bitmap('arrow-left-grey.bmp', wx.BITMAP_TYPE_BMP)
        arrowrightblack = wx.Bitmap('arrow-right.bmp', wx.BITMAP_TYPE_BMP)
        arrowrightgrey = wx.Bitmap('arrow-right-grey.bmp', wx.BITMAP_TYPE_BMP)
        arrowupblack = wx.Bitmap('arrow-up.bmp', wx.BITMAP_TYPE_BMP)
        arrowupgrey = wx.Bitmap('arrow-up-grey.bmp', wx.BITMAP_TYPE_BMP)
        arrowdownblack = wx.Bitmap('arrow-down.bmp', wx.BITMAP_TYPE_BMP)
        arrowdowngrey = wx.Bitmap('arrow-down-grey.bmp', wx.BITMAP_TYPE_BMP)
        parkblack = wx.Bitmap('parken_inv.bmp', wx.BITMAP_TYPE_BMP)
        parkgrey = wx.Bitmap('parken.bmp', wx.BITMAP_TYPE_BMP)

        # Buttons (Ort und Bilder) erstellen
        global left
        left = wx.ToggleButton(self, -1, pos=(12, 58),
                               size=(48, 48), style=wx.NO_BORDER)
        left.SetBitmap(arrowleftgrey)
        left.SetBitmapPressed(arrowleftblack)
        global right
        right = wx.ToggleButton(self, -1, pos=(108, 58),
                                size=(48, 48), style=wx.NO_BORDER)
        right.SetBitmap(arrowrightgrey)
        right.SetBitmapPressed(arrowrightblack)
        global up
        up = wx.ToggleButton(self, -1, pos=(60, 10),
                             size=(48, 48), style=wx.NO_BORDER)
        up.SetBitmap(arrowupgrey)
        up.SetBitmapPressed(arrowupblack)
        global down
        down = wx.ToggleButton(self, -1, pos=(60, 58),
                               size=(48, 48), style=wx.NO_BORDER)
        down.SetBitmap(arrowdowngrey)
        down.SetBitmapPressed(arrowdownblack)
        global park
        park = wx.ToggleButton(self, -1, pos=(108, 10),
                               size=(48, 48), style=wx.NO_BORDER)
        park.SetBitmap(parkgrey)
        park.SetBitmapPressed(parkblack)

        # Tastaturknoepfe verknuepfen ueber AcceleratorTable
        aId = wx.NewId()
        wId = wx.NewId()
        dId = wx.NewId()
        sId = wx.NewId()
        pId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.driveleftk, id=aId)
        self.Bind(wx.EVT_MENU, self.driveforwardsk, id=wId)
        self.Bind(wx.EVT_MENU, self.driverightk, id=dId)
        self.Bind(wx.EVT_MENU, self.drivebackwardsk, id=sId)
        self.Bind(wx.EVT_MENU, self.park, id=pId)
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, ord('a'), aId),
                                              (wx.ACCEL_NORMAL, ord('w'), wId),
                                              (wx.ACCEL_NORMAL, ord('d'), dId),
                                              (wx.ACCEL_NORMAL, ord('s'), sId),
                                              (wx.ACCEL_NORMAL, ord('u'), pId)])
        self.SetAcceleratorTable(self.accel_tbl)

        # Mit Funktion verbinden
        self.Bind(wx.EVT_TOGGLEBUTTON, self.driveleft, left)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.driveright, right)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.driveforwards, up)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.drivebackwards, down)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.park, park)


    # Funktionen
    # Funktionen fuer Eingabe ueber Klicken
    def driveleft(self, event):
        global lastCommand
        right.SetValue(0)
        # Abfrage damit nur Aufruf beim Druecken des Knopfes
        if left.GetValue():
            lastCommand[1] = 'a'
        # Abfrage ob Lenkung deaktiviert ist
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'
        # Abfrage ob alle Knoepfe deaktiviert sind
        if (left.GetValue() == 0) & (right.GetValue() == 0):
            lastCommand[1] = 'f'

    def driveright(self, event):
        global lastCommand
        left.SetValue(0)
        if right.GetValue():
            lastCommand[1] = 'd'
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'
        if (left.GetValue() == 0) & (right.GetValue() == 0):
            lastCommand[1] = 'f'

    def driveforwards(self, event):
        global lastCommand
        down.SetValue(0)
        if up.GetValue():
            lastCommand[0] = 'w'
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'

    def drivebackwards(self, event):
        global lastCommand
        up.SetValue(0)
        if down.GetValue():
            lastCommand[0] = 's'
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'

    # Funktionen fuer Eingabe ueber Tastatur
    def driveleftk(self, event):
        global lastCommand
        if left.GetValue() == 0:
            right.SetValue(0)
            left.SetValue(1)
            lastCommand[1] = 'a'
        elif left.GetValue() == 1:
            left.SetValue(0)
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'
        if (left.GetValue() == 0) & (right.GetValue() == 0):
            lastCommand[1] = 'f'

    def driverightk(self, event):
        global lastCommand
        if right.GetValue() == 0:
            right.SetValue(1)
            left.SetValue(0)
            lastCommand[1] = 'd'
        elif right.GetValue() == 1:
            right.SetValue(0)
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'
        if (left.GetValue() == 0) & (right.GetValue() == 0):
            lastCommand[1] = 'f'

    def driveforwardsk(self, event):
        global lastCommand
        if up.GetValue() == 0:
            up.SetValue(1)
            down.SetValue(0)
            lastCommand[0] = 'w'
        elif up.GetValue() == 1:
            up.SetValue(0)
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'
        if (left.GetValue() == 0) & (right.GetValue() == 0):
            lastCommand[1] = 'f'

    def drivebackwardsk(self, event):
        global lastCommand
        if down.GetValue() == 0:
            down.SetValue(1)
            up.SetValue(0)
            lastCommand[0] = 's'
        elif down.GetValue() == 1:
            down.SetValue(0)
        if (down.GetValue() == 0) & (up.GetValue() == 0):
            lastCommand[0] = 'r'
        if (left.GetValue() == 0) & (right.GetValue() == 0):
            lastCommand[1] = 'f'

    # Einpark-Funktion
    # Aendern!
    def park(self, event):
        global lastChar
        if park.GetValue() == 0:
            park.SetValue(1)
            ser.write("u")
            ser.write("r")   # danach reset
            print("Einparken!")
        elif park.GetValue() == 1:
            park.SetValue(0)
        # andere Knoepfe zuruecksetzen
        if left.GetValue() == 1:
            left.SetValue(0)
        if right.GetValue() == 1:
            right.SetValue(0)
        if down.GetValue() == 1:
            down.SetValue(0)
        if up.GetValue() == 1:
            up.SetValue(0)


##################################################
# erzeugt neues Fenster
class MyForm(wx.Frame):

    def __init__(self, parent, id):
        # Fenster initialiseren
        wx.Frame.__init__(self, parent=parent, id=id, title='Remote', size=(200, 200))

        # Fenster aufteilen in mehrere Unterfenster
        splitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        # Unterfenster initialisieren (in jeweiligen Klassen) und anhaengen
        panel1 = Controlpanel(splitter)
        graph1 = MatplotPanel1(splitter)
        graph2 = MatplotPanel2(splitter)
        graph3 = MatplotPanel3(splitter)
        splitter.AppendWindow(panel1)
        splitter.AppendWindow(graph1)
        splitter.AppendWindow(graph2)
        splitter.AppendWindow(graph3)
        # setzt Trennlinie
        splitter.SetSashPosition(1, 600)
        splitter.SetSashPosition(0, 170)
        # verbindet Schliessen-Knopf mit Funktion
        self.Bind(wx.EVT_CLOSE, self.closewindow)

    # Schliessfunktion
    def closewindow(self, event):
        self.Destroy()


##################################################
class MatplotPanel1(wx.Panel):
    # initialisiert Daten
    def init_ani(self):
        self.line.set_ydata(motor)
        return self.line,

    # Empfaengt Daten
    def receive(self):
        global motor
        while True:
            # liest serielle Verbindung und teilt Daten auf in Array
            serline = str(ser.readline())

            ##
            serline = serline.replace("b'", "")
            serline = serline.replace("AU", "")
            serline = serline[:-3]
            ##

            checkstring = "AM"
            if checkstring in serline:
                serline = serline.replace("AM", " ")
                motortemp = [int(val) for val in serline.split()]
                # Pruefen ob Motorintervall
                if (len(motortemp) == 4):
                    motor = motortemp
                    print(motor)
            yield motor

    # initialisiert animation
    def __init__(self, parent):
        # neues Unterpanel
        wx.Panel.__init__(self, parent, -1, size=(50, 50))
        # Array fuer Motorwerte
        global motor
        motor = [20, 20, 20, 20]
        # Anzahl der Werte
        N = 4
        global ind
        ind = np.arange(N)
        global width
        width = 0.35

        # Plot initialisieren
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-0.5, 3.5)
        self.ax.set_xticks(ind)
        self.ax.set_xticklabels(('Motor 1', 'Motor 2', 'Motor 3', 'Motor 4'))
        self.line, = self.ax.plot(motor, marker='o', markersize=20, linewidth=0, color='r',
                                  markeredgecolor='k', markeredgewidth='5')
        self.ax.set_ylim(0, 250)
        # Animation aufrufen: self.fig=fig uebergeben, self.OnPaint=update des Plots, self.receive=update der Daten,
        # self.init_ani=Daten initialisieren, interval=Intervall, nachdem .receive und .OnPaint gerufen wird,
        # Blit=False: Hintergrund wird nicht neu gemalt -> deutlich schneller
        self.ani = animation.FuncAnimation(self.fig, self.OnPaint,
                                           self.receive, init_func=self.init_ani, 
                                           interval=500, blit=True)
        # plt.show()
        # plt.ion()

        #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        # moeglichst block=True, damit Einbindung in Fenster. Falls das nicht klappt: Block=False
        plt.show(block=False)

    # malt Datenpunkte neu
    def OnPaint(self, motor):

        # kopieren des Hintergrunds
        background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        # Daten neusetzen
        self.line.set_ydata(motor)
        self.ax.draw_artist(self.ax.patch)
        self.ax.draw_artist(self.line)
        # Hintergrund wiederherstellen
        self.fig.canvas.restore_region(background)
        self.fig.canvas.blit(self.ax.bbox)
        return self.line,

###################################################


# Erklaerung siehe MatplotPanel1
class MatplotPanel2(wx.Panel):
    def init_ani(self):
        self.line.set_ydata(us)
        return self.line,

    def receive(self):
        global us
        while True:
            serline = str(ser.readline())

            ##
            serline = serline.replace("b'", "")
            serline = serline.replace("AU", "")
            serline = serline[:-3]
            ##

            checkstring = "AU"

            if checkstring in serline:
                print("======DEBUG")
                print(serline)
                ustemp = [int(val) for val in serline.split()]
                if (len(ustemp) == 3):
                    us = ustemp
            yield us

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, size=(50, 50))
        global us
        us = [100, 100, 100]
        # initialiseren der Achsen
        global theta
        theta = [np.pi/4, 3*np.pi/4, 3*np.pi/2]
        self.fig = plt.figure()
        # Polarplot
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.ax.set_xticks(theta)
        self.line, = self.ax.plot(theta, us, marker='o', markersize=10,
                                  linewidth=0)
        self.ani = animation.FuncAnimation(self.fig, self.OnPaint,
                                           self.receive, init_func=self.init_ani,
                                           interval=500, blit=True)
        # *#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        # moeglichst block=True, damit Einbindung in Fenster. Falls das nicht klappt: Block=False
        plt.show(block=False)

    def OnPaint(self, us):

        background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        self.line.set_ydata(us)
        self.ax.draw_artist(self.ax.patch)
        self.ax.draw_artist(self.line)
        self.fig.canvas.restore_region(background)
        self.fig.canvas.blit(self.ax.bbox)
        return self.line,

###################################################


class MatplotPanel3(wx.Panel):
    # Steuerung berechnen

    # initialisiert Daten
    def init_ani(self):
        self.line.set_xdata(0)
        self.line.set_ydata(0)
        return self.line,

    # Empfaengt Daten
    def compute(self):
        # Globale Variablen einlesen
        global MotorSet
        MotorSet = [0, 0, 0, 0]
        global Direction
        global lastCommand
        # Hilfsvariable fuer Richtung (wenn direkt von d->a oder vice versa)
        tempChar = '0'
        while True:
            print(lastCommand)
            if lastCommand[0] == 'w':
                # Richtungswechsel im Nullpunkt
                if (MotorSet[0] == 0) & (MotorSet[1] == 0):
                    Direction = 1
                # Ueberlauf verhindern
                if (MotorSet[0] < 256) & (MotorSet[1] < 256):
                    MotorSet[0] = MotorSet[0]+16
                    MotorSet[1] = MotorSet[1]+16
            elif lastCommand[0] == 's':
                if (MotorSet[0] == 0) & (MotorSet[1] == 0):
                    Direction = -1
                if (MotorSet[0] > -256) & (MotorSet[1] > -256):
                    MotorSet[0] = MotorSet[0]-16
                    MotorSet[1] = MotorSet[1]-16
            elif lastCommand[0] == 'r':
                # Werte verringern
                if (Direction == 1):
                    if MotorSet[0] > 0:
                        MotorSet[0] = MotorSet[0]-16
                    if(MotorSet[1] > 0):
                        MotorSet[1] = MotorSet[1]-16
                elif (Direction == -1):
                    if (MotorSet[0] < 0):
                        MotorSet[0] = MotorSet[0]+16
                    if (MotorSet[1] < 0):
                        MotorSet[1] = MotorSet[1]+16

            if lastCommand[1] == 'a':
                if (Direction == 1):
                    # Lenkung
                    if (MotorSet[0] >= 16) & (MotorSet[0] <= MotorSet[1]):
                        MotorSet[0] = MotorSet[0]-16
                    # falls Sprung von d->a
                    if (MotorSet[0] > MotorSet[1]):
                        lastCommand[1] = 'f'
                        tempChar = 'a'
                if (Direction == -1):
                    if (MotorSet[0] <= -16) & (MotorSet[0] >= MotorSet[1]):
                        MotorSet[0] = MotorSet[0]+16
                    if MotorSet[0] < MotorSet[1]:
                        lastCommand[1] = 'f'
                        tempChar = 'a'
            elif lastCommand[1] == 'd':
                if (Direction == 1):
                    if (MotorSet[1] >= 16) & (MotorSet[1] <= MotorSet[0]):
                        MotorSet[1] = MotorSet[1]-16
                    if (MotorSet[1] > MotorSet[0]):
                        lastCommand[1] = 'f'
                        tempChar = 'd'
                if (Direction == -1):
                    if (MotorSet[1] <= -16) & (MotorSet[1] >= MotorSet[0]):
                        MotorSet[1] = MotorSet[1]+16
                    if MotorSet[1] < MotorSet[0]:
                        lastCommand[1] = 'f'
                        tempChar = 'd'
            elif lastCommand[1] == 'f':
                # Lenkung verringern
                if Direction == 1:
                    if (MotorSet[0] > MotorSet[1]):
                        MotorSet[1] = MotorSet[1]+16
                    elif (MotorSet[0] < MotorSet[1]):
                        MotorSet[0] = MotorSet[0]+16
                if Direction == -1:
                    if (MotorSet[1] > MotorSet[0]):
                        MotorSet[1] = MotorSet[1]-16
                    elif (MotorSet[1] < MotorSet[0]):
                        MotorSet[0] = MotorSet[0]-16
                # nach Sprung von d->a oder andersherum, wenn Nullpunkt
                # durchlaufen, Lenkung fortsetzen
                if tempChar != '0':
                    if MotorSet[1] == MotorSet[0]:
                        lastCommand[1] = tempChar
                        tempChar = '0'
            # Entgegentgesetztlaufende Motoren verhindern
            if Direction == 1:
                if MotorSet[0] < 0:
                    MotorSet[0] = 0
                if MotorSet[1] < 0:
                    MotorSet[1] = 0
            if Direction == -1:
                if MotorSet[0] > 0:
                    MotorSet[0] = 0
                if MotorSet[1] > 0:
                    MotorSet[1] = 0

            # Motoren drehen auf jeweiliger Seite gleich herum
            MotorSet[3] = MotorSet[0]
            MotorSet[2] = MotorSet[1]

            print(Direction)
            print(MotorSet)
            # Daten senden
            str0 = '{:03d}'.format(MotorSet[0])
            str1 = '{:03d}'.format(MotorSet[1])
            str2 = '{:03d}'.format(MotorSet[2])
            str3 = '{:03d}'.format(MotorSet[3])

            string = 'CM M0:'+str0+' M1:'+str1+' M2:'+str2+' M3:'+str3+'\n'
            print(string)
            for s in string:
                ser.write(s)

            # ser.write(bytes(string, 'UTF-8'))

            # Motorenwerte in xy-Koordinaten transformieren
            if Direction == 1:
                MotorSety = max(MotorSet)
                # print(MotorSety)
            else:
                MotorSety = min(MotorSet)
            if Direction == 1:
                MotorSetx = MotorSet[0]-MotorSet[1]
            else:
                MotorSetx = MotorSet[1]-MotorSet[0]
            # print(MotorSetx)
            yield [MotorSetx, MotorSety]

    # initialisiert animation
    def __init__(self, parent):
        # neues Unterpanel
        wx.Panel.__init__(self, parent, -1, size=(50, 50))

        MotorSetx = 0
        MotorSety = 0

        # Plot initialisieren
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        patches = []
        polygon1 = Polygon([[0, 0], [256, 0], [256, 256]], True)
        polygon2 = Polygon([[0, 0], [-256, 0], [-256, 256]], True)
        polygon3 = Polygon([[0, 0], [-256, 0], [-256, -256]], True)
        polygon4 = Polygon([[0, 0], [256, 0], [256, -256]], True)
        patches.append(polygon1)
        patches.append(polygon2)
        patches.append(polygon3)
        patches.append(polygon4)
        p = PatchCollection(patches, alpha=0.4)
        self.ax.add_collection(p)

        plt.axis('equal')
        self.ax.set_xlim(-256, 256)
        self.ax.set_ylim(-256, 256)
        self.ax.set_xticks(np.linspace(-256, 256, 9))
        self.ax.set_yticks(np.linspace(-256, 256, 9))
        plt.xlabel('Lenkung')
        plt.ylabel('Richtung')
        self.ax.grid(True)
        self.line, = self.ax.plot(MotorSetx, MotorSety, marker='s',
                                  markersize=16, linewidth=0, color='firebrick',
                                  markeredgecolor='k', markeredgewidth='2')

        self.ani = animation.FuncAnimation(self.fig, self.OnPaint,
                                           self.compute, init_func=self.init_ani,
                                           interval=500, blit=True)
        #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        # moeglichst block=True, damit Einbindung in Fenster. Falls das nicht klappt: Block=False
        plt.show(block=False)

    # malt Datenpunkte neu
    def OnPaint(self, MotorSetArray):

        # kopieren des Hintergrunds
        background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        # Daten neusetzen
        self.line.set_xdata(MotorSetArray[0])
        self.line.set_ydata(MotorSetArray[1])
        self.ax.draw_artist(self.ax.patch)
        self.ax.draw_artist(self.line)
        # Hintergrund wiederherstellen
        self.fig.canvas.restore_region(background)
        self.fig.canvas.blit(self.ax.bbox)
        return self.line,

##########################################################
# Hauptprogramm


if __name__ == "__main__":
    app = wx.App(False)                       # startet App
    frame = MyForm(parent=None, id=-1)         # startet neues Fenster und zeigt es ->MyForm Class __init__
    frame.Show()
    app.MainLoop()




