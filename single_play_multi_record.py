import pyaudio
import wave
import time
import struct
import numpy as np
import matplotlib.pyplot as plt

dbs = []
rmss = []

p = pyaudio.PyAudio()

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
    db = np.round((calc_dBSPL(in_data_ch1)+calc_dBSPL(in_data_ch2))/2,1)
    rms = np.round((calc_RMS(in_data_ch1)+calc_RMS(in_data_ch2))/2,3)
    dbs.append(db)
    rmss.append(rms)
    print ('dbspl : ' + str(db) + ' rms : ' + str(rms) + '\n')
    return (data, pyaudio.paContinue)

def process(wf):
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    output=True,
                    stream_callback=callback)
    
    stream.start_stream()
    
    while stream.is_active():
        time.sleep(0.1)
    
    stream.stop_stream()
    stream.close()
    wf.close()
    return None


for i in range(1, 25):
    dbs, rmss = [], [] # clear global variables
    wf = wave.open('pypinknoise.wav', 'r')
    print('~' * 25 + str(i) + '~' * 25)
    process(wf)
    plt.figure()
    plt.plot(dbs, 'r')
    # plt.figure()
    # plt.plot(rmss, 'b')
    time.sleep(1.0)

p.terminate()