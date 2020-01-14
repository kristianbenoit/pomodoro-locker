#!/usr/bin/python

# This script is to work around a bug in Gnome Pomodoro. 
#
# The bug:
# Gnome Pomodoro start a new pomodoro after waiting for activity (after a
# pause). It start a pomodoro even if the screensaver is active.
#
# What the script do:
# This script force Gnome Pomodoro to stay on pause when it end and the
# screensaver is active. To use it, call it when breaks 'complete' from the
# Custom Actions plugin.
#
# Why I wrote it:
# I wrote this script to force me into a break. I force a break by locking the
# screen with "gnome-screensaver-commmand --lock" when a break 'start' or is
# 'resume'd (using Custom Action plugin)

from pydbus import SessionBus
from gi.repository import GLib

bus = SessionBus()
gpomodoro = bus.get('org.gnome.Pomodoro')
screensaver = bus.get('org.gnome.ScreenSaver')
listeners = []

def onScreensaverActiveChange(*args, **argv):
    gpomodoro.Resume()
    for l in listeners:
        l.disconnect()
    loop.quit()

def onPomodoroPropertyChange(*args, **argv):
    if gpomodoro.State == "pomodoro" and not gpomodoro.IsPaused:
        gpomodoro.Pause()
    
if screensaver.GetActive():
    listeners.append(screensaver.ActiveChanged.connect(onScreensaverActiveChange))
    listeners.append(gpomodoro.PropertiesChanged.connect(onPomodoroPropertyChange))
    loop = GLib.MainLoop()
    loop.run()
