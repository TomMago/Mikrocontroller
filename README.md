# Mikrocontroller Projekt der KSS

Das Mikrocontroller Projekt befasst sich mit der Programmierung eines Ardunios.

## Einführung

Ein kurze Installationsanleitung, vorerst für Linux.

### Vorraussetzungen

Python: https://www.python.org/downloads/ oder über Paketmanager
Numpy und Matplotlib: über pip oder Paketmanager - https://scipy.org/install.html


### Installation

Lade zunächst die Projektdateien von GitHub runter.

Installiere nun wxPython: http://www.wxpython.org/
```
pip install wxPython
```

Installiere außerdem pySerial: http://pyserial.sourceforge.net/
```
pip install pyserial
```
Installiere den Arduino IDE entweder von https://www.arduino.cc/en/Main/Software oder:
```
apt-get install arduino
```

Füge nun die Librarys aus dem Ordner lib/ im IDE über Sketch/Import Library hinzu.

