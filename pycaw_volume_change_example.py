
"""
Get and set access to master volume example.
"""
from __future__ import print_function

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

def mute():
    volume.SetMute(1, None)
    return None

def unmute():
    volume.SetMute(0, None)
    return None

def get_range():
    return volume.GetVolumeRange()

def same_vol():
    volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel(), None)
    return None

def decr_vol():
    if volume.GetMasterVolumeLevel() > (get_range()[0] + 46.15): # strictly >
        volume.SetMasterVolumeLevel((volume.GetMasterVolumeLevel() - 0.5), None)
    else:
        volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel(), None)
    return None

def incr_vol():
    if volume.GetMasterVolumeLevel() < (get_range()[1] - 2.50): # strictly <
        volume.SetMasterVolumeLevel((volume.GetMasterVolumeLevel() + 0.5), None)
    else:
        volume.SetMasterVolumeLevel(volume.GetMasterVolumeLevel(), None)
    return None



print("volume.GetMute(): %s" % volume.GetMute())
print("volume.GetMasterVolumeLevel(): %s" % volume.GetMasterVolumeLevel())
print("volume.GetVolumeRange(): (%s, %s, %s)" % volume.GetVolumeRange())
print("volume.SetMasterVolumeLevel()")
volume.SetMasterVolumeLevel(-30.0, None)
print("volume.GetMasterVolumeLevel(): %s" % volume.GetMasterVolumeLevel())
