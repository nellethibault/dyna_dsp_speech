# Imports
from __future__ import print_function
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import pyaudio as pa
import time


# Global Variables
sampling_frequency = 48000 # Hz
sampling_format = pa.paFloat32
samples_chunk = 4800
samples_width = 2
channel_count = 2
sampling_time = 1 # Sec
gain_overall = np.power(10, (-0.1 / 20.0))
gain_decrease = np.power(10.0, (-0.5 / 20.0))
gain_increase = np.power(10.0, (0.5 / 20.0))
dB_threshold = 75
dB_error_correct = 75 # Change this to level of dBSPL
rms_avg = 0.0
prev_rms_avg = rms_avg
dB_avg = 0.0
prev_dB_avg = dB_avg

# Instantiations
audio = pa.PyAudio()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# This method is used if there is more than one Microphone.
def get_Mics():
    mic_index = []
    for i in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(i)
        if (devices['name'][0:10] == 'Microphone'):
            mic_index.append(devices['index'])
    return mic_index

# This method is used if and only if there are more than one pair of Speakers.
def get_Spkrs():
    spkr_index = []
    for i in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(i)
        if (devices['name'][0:8] == 'Speakers'):
            spkr_index.append(devices['index'])
    return spkr_index

def calc_dBSPL(input_signal):
    # Input Signal is NumPy Array
    dB_SPL = (10.0 * np.log10(np.mean(input_signal ** 2.0))) + dB_error_correct;
    #print (int(dB_SPL))
    return int(dB_SPL)

def calc_RMS(input_signal):
    # Input Signal is NumPy Array
    rms = np.sqrt(np.mean(input_signal ** 2.0))
    return rms

# Two Channels Merged
def read_in_data(in_data):
    in_data = np.fromstring(in_data, dtype=np.float32)
    return in_data

def decr_vol():
    #devices = AudioUtilities.GetSpeakers()
    #interface = devices.Activate(
            #IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol = (volume.GetMasterVolumeLevel() - 0.1)
    volume.SetMasterVolumeLevel(vol, None)
    #print ('Volume Decreased !')
    return None

def incr_vol():
    #devices = AudioUtilities.GetSpeakers()
    #interface = devices.Activate(
            #IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol = (volume.GetMasterVolumeLevel() + 0.1)
    volume.SetMasterVolumeLevel(vol, None)
    #print ('Volume Increased !')
    return None

#def same_vol():
#    #devices = AudioUtilities.GetSpeakers()
#    #interface = devices.Activate(
#            #IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#    #volume = cast(interface, POINTER(IAudioEndpointVolume))
#    vol = volume.GetMasterVolumeLevel()
#    volume.SetMasterVolumeLevel(vol, None)
#    #print ('Volume Unchanged !')
#    return None
    
def process():
    stream_1 = audio.open(format = sampling_format, channels = channel_count, 
                          rate = sampling_frequency, input = True, 
                          output = False, # Change output = True to hear the Mics 
                          input_device_index = get_Mics()[0], 
                          #output_device_index = get_Spkrs()[0], 
                          frames_per_buffer = samples_chunk)
    stream_2 = audio.open(format = sampling_format, channels = channel_count, 
                          rate = sampling_frequency, input = True, 
                          output = False, # Change output = True to hear the Mics 
                          input_device_index = get_Mics()[1], 
                          #output_device_index = get_Spkrs()[0], 
                          frames_per_buffer = samples_chunk)
    for i in range(0, int(sampling_frequency / samples_chunk * sampling_time)):
        data_1 = stream_1.read(samples_chunk)
        rms_1 = calc_RMS(read_in_data(data_1))
        dB_1 = calc_dBSPL(read_in_data(data_1))
        data_2 = stream_2.read(samples_chunk)
        rms_2 = calc_RMS(read_in_data(data_2))
        dB_2 = calc_dBSPL(read_in_data(data_2))
        global rms_avg, prev_rms_avg
        global dB_avg, prev_dB_avg
        rms_avg = (rms_1 + rms_2) / 2
        prev_rms_avg = rms_avg
        dB_avg = (dB_1 + dB_2) / 2
        prev_dB_avg = dB_avg
        global dB_threshold
        if (dB_avg <= dB_threshold):
            if dB_avg > prev_dB_avg:
                incr_vol()
            elif dB_avg < prev_dB_avg:
                decr_vol()
            #else:
                #same_vol()
        else:
            decr_vol()
    stream_1.stop_stream()
    stream_2.stop_stream()
    return None

def close():
    audio.terminate()
    return None

def main():
    print ('Running Main Loop ...')
    while True:
        process()
        time.sleep(1.0)
    close()
    return None

main()