import xbmc
from .util import json_rpc, seconds_to_kodi_time


def play(path, seconds):
    try:
        json_rpc("Player.Open", {"item": {"file": path}, "options": {"resume": seconds_to_kodi_time(seconds)}})
    except Exception:
        player = xbmc.Player()
        player.play(path)
        monitor = xbmc.Monitor()
        waited = 0.0
        while waited < 20.0 and not player.isPlayingVideo():
            if monitor.waitForAbort(0.25):
                return
            waited += 0.25
        if not player.isPlayingVideo():
            raise RuntimeError("Kodi video player did not start.")
        player.seekTime(float(seconds))
