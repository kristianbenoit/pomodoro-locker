#!/usr/bin/python

from pydbus import SessionBus
from gi.repository import GLib
import logging

# Not needed, remove ?
#from dbus.mainloop.glib import DBusGMainLoop
#DBusGMainLoop(set_as_default=True)

loop = GLib.MainLoop()
bus = SessionBus()
gpomodoro = bus.get('org.gnome.Pomodoro')
screensaver = bus.get('org.gnome.ScreenSaver')

# To see what is going on.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

class PomodoroLocker():
    def __init__(self):
        self.loop = GLib.MainLoop()
        self.bus = SessionBus()
        self.gpomodoro = self.bus.get('org.gnome.Pomodoro')
        self.screensaver = self.bus.get('org.gnome.ScreenSaver')
        logging.debug("Initialized a pomodoro locker: %s", self.__dict__)

    # Could be part of __init__, but useful to have it separate for debugging.
    def startListening(self):
        self.events=[]
        self.events.append(self.gpomodoro.StateChanged.connect(self.onPomodoroStateChange))
        self.events.append(self.screensaver.ActiveChanged.connect(self.onScreensaverActiveChange))
        self.loop.run()
        pauseStart()

    def pauseStart():
        logging.info("We changed to pomodoro while screensaver is on, force it to pause until the screensaver get unlocked.")
        self.gpomodoro.Resume()
        self.restartPausehandler = self.gpomodoro.PropertiesChanged.connect(self.restartPause)
        
    def onPomodoroStateChange(self, *args):
        newState = args[0]
        oldState = args[1]
        logging.info("Got notified of change from %s to %s", oldState['name'], newState['name'])
        logging.debug("Old state was %s", oldState)
        logging.debug("New state is  %s", newState)
        if newState['name'].endswith('-break') and oldState['name'] == 'pomodoro':
            self.screensaver.Lock()
        if newState['name'] == 'pomodoro' and oldState['name'].endswith("-break") and self.screensaver.GetActive():
            pauseStart()

    def restartPause(self, *args, **argv):
        logging.debug("%s changed" % args[0])
        if self.gpomodoro.State == "pomodoro" and self.screensaver.GetActive() and not self.gpomodoro.IsPaused:
            logging.info("Pausing the pomodoro as we are on screensaver")
            logging.debug("Is paused before: %s" % self.gpomodoro.IsPaused)
            self.gpomodoro.Pause()
            logging.debug("Is paused after: %s" % self.gpomodoro.IsPaused)

    def onScreensaverActiveChange(self, *args, **argv):
        active = args[0]
        if not active: 
            logging.info("The screensaver is now inactive, Start a pomodoro")
            self.restartPausehandler.disconnect()
            self.gpomodoro.Resume()
            exit(0)

l = PomodoroLocker()
l.startListening()
