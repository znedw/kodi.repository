import os
import xbmc
import xbmcaddon
import xbmcvfs

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
debug = __addon__.getSetting("debug")
enabled = __addon__.getSetting("enabled")
speed = __addon__.getSetting("speed")
__cwd__ = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
__profile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__resource__ = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources'))

__settings__ = xbmcaddon.Addon("service.defaultplaybackspeed.matrix")

monitor = xbmc.Monitor()

tempo_down = "TempoDown"
tempo_up = "TempoUp"

# index in select list: (times to run, command)
playBackSpeeds = {"0": (2, tempo_down),
                  "1": (1, tempo_down),
                  "2": (0, ""),  # 1.0x do nothing
                  "3": (1, tempo_up),
                  "4": (2, tempo_up),
                  "5": (3, tempo_up),
                  "6": (4, tempo_up),
                  "7": (5, tempo_up)
                  }


def Debug(msg, force=False):
    if (debug == "true" or force):
        xbmc.log("#####[DefaultPlaybackSpeed]##### " + msg, xbmc.LOGDEBUG)


Debug("Loading '%s' version '%s'" % (__scriptname__, __version__))


class PlaybackSpeedPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        Debug("Initalised")
        Debug("Default playback speed enabled: %s" % enabled)
        Debug("Default playback speed: %s" % speed)
        self.run = True

    def onPlayBackStopped(self):
        Debug("Stopped")
        self.run = True

    def onPlayBackEnded(self):
        Debug("Ended")
        self.run = True

    def onAVStarted(self):
        Debug("onAVStarted")
        enabled = __addon__.getSetting("enabled")
        speed = __addon__.getSetting("speed")
        if (enabled == "true"):
            Debug(
                "Trying to set playback speed for value with index: {0}...".format(speed))
            try:
                times, command = playBackSpeeds[speed]
                to_run = "PlayerControl({0})".format(command)
                # TODO: big assumption that the player is running at 1.0x...
                Debug("I'm going to run {0} {1} times...".format(
                    to_run, times))
                for c in range(times):
                    Debug(
                        "Sending {0}/{1} command {2}".format(c + 1, times, to_run))
                    xbmc.executebuiltin(to_run)
                self.run = False
            except KeyError:
                Debug(
                    "Couldn't find a key for your playback speed {0}...".format(speed))
            except:
                Debug("Something went wrong...")
                pass
        else:
            Debug(
                'Not enabled or not a video file, not setting playback speed, finishing')


class PlaybackSpeedRunner:
    player = PlaybackSpeedPlayer()
    while not monitor.abortRequested():
        monitor.waitForAbort(1)
    del player
