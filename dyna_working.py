from __future__ import print_function
import numpy as np
import pyaudio as pa
import struct
#import wave
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Instantiations
calib_play = pa.PyAudio()
calib_recd = pa.PyAudio()
audio = pa.PyAudio()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#sweep = wave.open('pinknoise.wav', 'rb')

# Global Variables
sampling_frequency = 48000 # Hz
samples_chunk = 4800
samples_width = 2
channel_count = 2
dB_threshold = 70
dB_error_correct = 85 # Change this to level of dBSPL
dB_channels = np.array(np.ones(4, dtype=np.float32))
dB_chs_mean = np.mean(dB_channels)

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

# Designed for Two Channels only
def read_2ch_in_data(in_data):
    chnls = 2
    in_data_ch1, in_data_ch2 = [], []
    for i in range(0, int(len(in_data)), int(4*chnls)):
        in_data_ch1.append(struct.unpack('f', in_data[i:i+4])[0])
        in_data_ch2.append(struct.unpack('f', in_data[i+4:i+8])[0])
    in_data_ch1 = np.array(in_data_ch1)
    in_data_ch2 = np.array(in_data_ch2)
    return [in_data_ch1, in_data_ch2]

# Designed for Two Channels only
def write_2ch_out_data(proc_data):
    out_data = b''
    out_data_ch1 = proc_data[0].tolist()
    out_data_ch2 = proc_data[1].tolist()
    for i in range(0, int(len(out_data_ch1))):
        out_data = out_data + struct.pack('ff', out_data_ch1[i], out_data_ch2[i])
    return out_data

def calc_dBSPL(input_signal):
    # Input Signal is NumPy Array
    dB_SPL = (10.0 * np.log10(np.mean(input_signal ** 2.0))) + dB_error_correct;
    if np.isnan(dB_SPL):
        dB_SPL = dB_threshold
    #print(dB_SPL)
    return dB_SPL

def calc_RMS(input_signal):
    # Input Signal is NumPy Array
    rms = np.sqrt(np.mean(input_signal ** 2.0))
    return rms

def callback_1(in_data, frame_count, time_info, status):
    #out_data = in_data
    # Signal Processing Goes Here
    in_data_ch1, in_data_ch2 = read_2ch_in_data(in_data)
    global dB_channels, dB_chs_mean
    dB_chs_mean = np.mean(dB_channels)
    dB_channels[0] = calc_dBSPL(in_data_ch1)
    dB_channels[1] = calc_dBSPL(in_data_ch1)
    if int(np.mean(dB_channels)) <= dB_threshold:
        if (int(np.mean(dB_channels)) > int(dB_chs_mean)): # >
            incr_vol()
        elif (int(np.mean(dB_channels)) < int(dB_chs_mean)): # <
            decr_vol()
        else:
            same_vol
    else:
        same_vol()
    #out_data = write_2ch_out_data([in_data_ch1, in_data_ch1])
    #out_data = [in_data_ch1 * gain_overall, in_data_ch1 * gain_overall]
    #out_data = write_2ch_out_data(out_data)
    return (in_data, pa.paContinue)

def callback_2(in_data, frame_count, time_info, status):
    #out_data = in_data
    # Signal Processing Goes Here
    in_data_ch1, in_data_ch2 = read_2ch_in_data(in_data)
    global dB_channels, dB_chs_mean
    dB_chs_mean = np.mean(dB_channels)
    dB_channels[2] = calc_dBSPL(in_data_ch1)
    dB_channels[3] = calc_dBSPL(in_data_ch1)
    if int(np.mean(dB_channels)) <= dB_threshold:
        if (int(np.mean(dB_channels)) > int(dB_chs_mean)): # >
            incr_vol()
        elif (int(np.mean(dB_channels)) < int(dB_chs_mean)): # <
            decr_vol()
        else:
            same_vol
    else:
        decr_vol()
    #out_data = write_2ch_out_data([in_data_ch1, in_data_ch1])
    #out_data = [in_data_ch1 * gain_overall, in_data_ch1 * gain_overall]
    #out_data = write_2ch_out_data(out_data)
    return (in_data, pa.paContinue)

def process():
    print ('Running Main Loop ...')
    # Mic 1
    stream_1 = audio.open(format = pa.paFloat32, channels = channel_count, 
                          rate = sampling_frequency, input = True, 
                          output = False, # Change output = True to hear the Mics 
                          input_device_index = get_Mics()[0], 
                          output_device_index = get_Spkrs()[0], 
                          frames_per_buffer = samples_chunk, 
                          stream_callback = callback_1)
    # Mic 2
    stream_2 = audio.open(format = pa.paFloat32, channels = channel_count, 
                          rate = sampling_frequency, input = True, 
                          output = False, # Change output = True to hear the Mics 
                          input_device_index = get_Mics()[1], 
                          output_device_index = get_Spkrs()[0], 
                          frames_per_buffer = samples_chunk, 
                          stream_callback = callback_2)
    
    stream_1.start_stream()
    stream_2.start_stream()
    
    while (stream_1.is_active() and stream_2.is_active()):
        time.sleep(0.1)

    stream_1.stop_stream()
    stream_2.stop_stream()
    stream_1.close()
    stream_2.close()
    audio.terminate()
    
    print ('Main Loop Terminated !')
    
    return None

process()

# End of File