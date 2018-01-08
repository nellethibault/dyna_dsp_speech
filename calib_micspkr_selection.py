from __future__ import print_function

'''
Combined Calibration and Mic-Speaker Selction Process:
'''

'''
Process:
    Choose one Speaker - one speaker is one channel always
    For every speaker:
    Now locate the nearest Microphone to that speaker:
        with a start volume of 60% sysvol
        Play a Pink noise sample in the speaker:
            While sound is on:
                Record a sample length in all microphones - 5 sec @ 48khz
                and store the avarage of all the mics in an array
                The maximum value of volume of mics in the list is the closest mic
                The closest mic index is the mic's device index.
                for the next 10 sec @ 48khz:
                    for the closest mic
                    with a start volume of 30% sysvol to 70%
                    get mic reading levels with random step size change in sysvol
                    save the relevant mic inputs as x and sysvol as y as an x,y pair
                    
            Now pair up speaker channel to microphone as tuple

        Obtain the regression line equation for best fit line:
            using sklearn? kernel ridge regression
            tune hyperparameters using gridsearchCV
        
        return the regression line equation for every model(?)
        
        NOTE:
            One pair of speaker is one device
            So, one speaker is one of the pair (if mono)
            Combine two channels in a mic to make single mic input (average channels)
            Now we have one input one outut pair.

'''

import numpy as np
import pyaudio as pa
import wave
import time
import struct
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import matplotlib.pyplot as plt

dbs = []
rmss = []

audio = pa.PyAudio()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# This method is used if there is more than one Microphone.
def get_Mics():
    mics_index = []
    for i in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(i)
        if (devices['name'][0:10] == 'Microphone'):
            mics_index.append(devices['index'])
    return mics_index

# This method is used if there is more than one Microphone. Also includes Wireless Devices.
def get_All_Mics():
    all_mics_index = []
    for i in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(i)
        if (devices['maxOutputChannels'] == 0):
            if (('Microphone' in devices['name']) or ('Head' in devices['name'])):
                all_mics_index.append(devices['index'])
    return all_mics_index

# This method is used if and only if there are more than one pair of Speakers. 
def get_Spkrs():
    spkrs_index = []
    for i in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(i)
        if (devices['name'][0:8] == 'Speakers'):
            spkrs_index.append(devices['index'])
    return spkrs_index

# This method is used if and only if there are more than one pair of Speakers. Also includes Wireless Devices.
def get_All_Spkrs():
    all_spkrs_index = []
    for i in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(i)
        if (devices['maxInputChannels'] == 0):
            if (('Speaker' in devices['name']) or ('Head' in devices['name'])):
                all_spkrs_index.append(devices['index'])
    return all_spkrs_index

def mute():
    volume.SetMute(1, None)
    return None

def unmute():
    volume.SetMute(0, None)
    return None

def get_range():
    return volume.GetVolumeRange()

def same_vol():
    volume.SetMasterVolumeLevelScalar(volume.GetMasterVolumeLevelScalar(), None)
    return None

def decr_vol():
    # Default Minimum is 20% -> If Parseval Higher (+0.05 or 5%) Elif Parseval Lower (-0.05 or 5%) ELse No Change (0.0 or 0%)
    if volume.GetMasterVolumeLevelScalar() > (0.20): # strictly > 20%
        volume.SetMasterVolumeLevelScalar((volume.GetMasterVolumeLevelScalar() - 0.01), None)
    else:
        volume.SetMasterVolumeLevelScalar(volume.GetMasterVolumeLevelScalar(), None)
    return None

def incr_vol():
    # Default Maximum Never Changes - Constant at 98% or 0.98
    if volume.GetMasterVolumeLevelScalar() < (0.98): # strictly < 98%
        volume.SetMasterVolumeLevelScalar((volume.GetMasterVolumeLevelScalar() + 0.01), None)
    else:
        volume.SetMasterVolumeLevelScalar(volume.GetMasterVolumeLevelScalar(), None)
    return None

def calc_dBSPL(input_signal):
    # Input Signal is NumPy Array
    dB_SPL = (10.0 * np.log10(np.mean(input_signal ** 2.0))) + 100;
    #print(dB_SPL)
    return dB_SPL

def calc_RMS(input_signal):
    # Input Signal is NumPy Array
    rms = np.sqrt(np.mean(input_signal ** 2.0))
    return rms

def read_2ch_in_data(in_data):
    chnls = 2
    in_data_ch1, in_data_ch2 = [], []
    for i in range(0, int(len(in_data)), int(4*chnls)):
        in_data_ch1.append(struct.unpack('f', in_data[i+0:i+4])[0])
        in_data_ch2.append(struct.unpack('f', in_data[i+4:i+8])[0])
    in_data_ch1 = np.array(in_data_ch1)
    in_data_ch2 = np.array(in_data_ch2)
    return [in_data_ch1, in_data_ch2]

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    in_data_ch1, in_data_ch2 = read_2ch_in_data(in_data)
    global dbs, rmss
    db = np.round((calc_dBSPL(in_data_ch1)+calc_dBSPL(in_data_ch2))/2, 1)
    rms = np.round((calc_RMS(in_data_ch1)+calc_RMS(in_data_ch2))/2, 3)
    dbs.append(db)
    rmss.append(rms)
    print ('dbspl : ' + str(db) + ' rms : ' + str(rms) + '\n')
    return (data, pa.paContinue)

def process(wf, mic, spkr):
    stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        output=True,
                        input_device_index = mic,
                        output_device_index = spkr,
                        stream_callback=callback)
    
    stream.start_stream()
    
    while stream.is_active():
        time.sleep(0.1)
    
    stream.stop_stream()
    stream.close()
    wf.close()
    return None

mics = get_All_Mics()
spkrs = get_All_Spkrs()

for s in spkrs:
    for m in mics:
        dbs, rmss = [], [] # clear global variables
        wf = wave.open('pypinknoise.wav', 'r')
        print('~' * 25)
        process(wf, m, s)
        plt.figure()
        plt.plot(dbs, 'r')
        # plt.figure()
        # plt.plot(rmss, 'b')
        # here take the  second half ofthe dbs - average them
        # make a [spkr, micavgdbval] pair as list of lists
        # max micavgdbval for that spkr is the closest mic of that spkr
        time.sleep(1.0)

audio.terminate()