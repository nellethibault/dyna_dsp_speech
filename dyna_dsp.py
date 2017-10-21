import numpy as np
import scipy.signal as sps
import pyaudio as pa
import struct
import wave
import time
from __future__ import print_function
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Global Variables
sampling_frequency = 48000 # Hz
samples_chunk = 4800
samples_width = 2
channel_count = 2
#gain_at_AC = np.power(10.0, (-3.0 / 20.0))
gain_overall = np.power(10, (-0.1 / 20.0))
gain_decrease = np.power(10.0, (-0.5 / 20.0))
gain_increase = np.power(10.0, (0.5 / 20.0))
dB_threshold = 75
dB_error_correct = 60.0 # Change this to level of dBSPL
dB_channels = np.array(np.ones(4, dtype=np.float32))
dB_chs_mean = np.mean(dB_channels)
sweep_file_rms = 0.0
sweep_in_rms = 0.0

# Defaults :
# Sampling Rate = 16000 Hz
# Nyquist Frequency = Fs/2 = (16kHz/2) = 8000 Hz
# Nyquist rad/sec = Fs/2 = 1 normalized
# Normalized freq X = (4*pi*X)/Fs rad/sec

# Instantiations
calib_play = pa.PyAudio()
calib_recd = pa.PyAudio()
audio = pa.PyAudio()
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
sweep = wave.open('sine_sweep_linear.wav', 'rb')

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

## Designed for Two Channels only
#def read_2ch_in_data(in_data):
#    chnls = 2
#    in_data_ch1, in_data_ch2 = [], []
#    in_data = np.fromstring(in_data, dtype=np.float32)
#    for i in range(0, int((len(in_data)/chnls)+chnls), chnls):
#        in_data_ch1.append(in_data[i])
#        in_data_ch2.append(in_data[i+1])
#    in_data_ch1 = np.array(in_data_ch1)
#    in_data_ch2 = np.array(in_data_ch2)
#    return [in_data_ch1, in_data_ch2]

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

## Two Channels Merged
#def read_in_data(in_data):
#    in_data = np.fromstring(in_data, dtype=np.float32)
#    return in_data

# Two Channels Merged - Incorrect Refer 2ch Method
def read_in_data(in_data):
    data_in = []
    for i in range(0, int(len(in_data)+1), 4):
        data_in.append(struct.unpack('f', in_data[i:i+4])[0])
    data_in = np.array(data_in)
    return data_in

## Designed for Two Channels only
#def write_2ch_out_data(proc_data):
#    out_data = []
#    out_data_ch1 = proc_data[0]
#    out_data_ch2 = proc_data[1]
#    for i in range(0, len(out_data_ch1)):
#        out_data.append(out_data_ch1[i])
#        out_data.append(out_data_ch2[i])
#    out_data = np.array(out_data)
#    out_data = out_data.astype(np.float32).tostring()
#    return out_data

# Designed for Two Channels only
def write_2ch_out_data(proc_data):
    out_data = b''
    out_data_ch1 = proc_data[0].tolist()
    out_data_ch2 = proc_data[1].tolist()
    for i in range(0, int(len(out_data_ch1))):
        out_data = out_data + struct.pack('ff', out_data_ch1[i], out_data_ch2[i])
    return out_data

## Two Channels Merged
#def write_out_data(proc_data):
#    out_data = proc_data.astype(np.float32).tostring()
#    return out_data

# Two Channels Merged
def write_out_data(proc_data):
    out_data = b''
    proc_data = proc_data.tolist()
    for i in range(0, int(len(proc_data))):
        out_data = out_data + struct.pack('f', proc_data[i])
    return out_data

def calc_dBSPL(input_signal):
    # Input Signal is NumPy Array
    dB_SPL = (10.0 * np.log10(np.mean(input_signal ** 2.0))) + dB_error_correct;
    if np.isnan(dB_SPL):
        dB_SPL = dB_threshold
    return dB_SPL

def calc_RMS(input_signal):
    # Input Signal is NumPy Array
    rms = np.sqrt(np.mean(input_signal ** 2.0))
    return rms

#def filter_HighPass(input_signal):
#    filter_order = 16 # number
#    stopband_frequency = (4 * np.pi * 75.0) / sampling_frequency # rad/sec
#    passband_ripple = 1.0 # dB
#    stopband_ripple = 60.0 # dB
#    b, a = sps.iirfilter(N=filter_order, Wn=stopband_frequency, 
#                         rp=passband_ripple, rs=stopband_ripple, 
#                         btype='highpass', analog=False, 
#                         ftype='ellip', output='ba')
#    filt_input = sps.lfilter(b, a, input_signal)
#    return filt_input
#
#def filter_BandPass(input_signal):
#    filter_order = 16 # number
#    passband_frequency = (4 * np.pi * 75.0) / sampling_frequency # rad/sec
#    stopband_frequency = (4 * np.pi * 275.0) / sampling_frequency # rad/sec
#    passband_ripple = 1.0 # dB
#    stopband_ripple = 60.0 # dB
#    b, a = sps.iirfilter(N=filter_order, 
#                         Wn=[passband_frequency, stopband_frequency], 
#                         rp=passband_ripple, rs=stopband_ripple, 
#                         btype='bandpass', analog=False, 
#                         ftype='ellip', output='ba')
#    filt_input = sps.lfilter(b, a, input_signal)
#    return filt_input
#
#def filter_LowPass(input_signal):
#    filter_order = 16 # number
#    passband_frequency = (4 * np.pi * 275.0) / sampling_frequency # rad/sec
#    passband_ripple = 1.0 # dB
#    stopband_ripple = 60.0 # dB
#    b, a = sps.iirfilter(N=filter_order, Wn=passband_frequency, 
#                         rp=passband_ripple, rs=stopband_ripple, 
#                         btype='lowpass', analog=False, 
#                         ftype='ellip', output='ba')
#    filt_input = sps.lfilter(b, a, input_signal)
#    return filt_input

def callback_1(in_data, frame_count, time_info, status):
    # out_data = in_data
    # Signal Processing Goes Here
    in_data_ch1, in_data_ch2 = read_2ch_in_data(in_data)
    global dB_channels, dB_chs_mean
    dB_chs_mean = np.mean(dB_channels)
    dB_channels[0] = calc_dBSPL(in_data_ch1)
    dB_channels[1] = calc_dBSPL(in_data_ch1)
    if (int(np.mean(dB_channels)) > int(dB_chs_mean)): # >
        in_data_ch1 = in_data_ch1 * gain_increase
        in_data_ch2 = in_data_ch2 * gain_increase
    elif (int(np.mean(dB_channels)) < int(dB_chs_mean)): # <
        in_data_ch1 = in_data_ch1 * gain_decrease
        in_data_ch2 = in_data_ch2 * gain_decrease
    elif (int(np.mean(dB_channels)) == int(dB_chs_mean)):
        in_data_ch1 = in_data_ch1 * gain_overall
        in_data_ch2 = in_data_ch2 * gain_overall
    out_data = write_2ch_out_data([in_data_ch1, in_data_ch1])
    #out_data = [in_data_ch1 * gain_overall, in_data_ch1 * gain_overall]
    #out_data = write_2ch_out_data(out_data)
    return (out_data, pa.paContinue)

def callback_2(in_data, frame_count, time_info, status):
    # out_data = in_data
    # Signal Processing Goes Here
    in_data_ch1, in_data_ch2 = read_2ch_in_data(in_data)
    global dB_channels, dB_chs_mean
    dB_chs_mean = np.mean(dB_channels)
    dB_channels[2] = calc_dBSPL(in_data_ch1)
    dB_channels[3] = calc_dBSPL(in_data_ch1)
    if (int(np.mean(dB_channels)) > int(dB_chs_mean)): # >
        in_data_ch1 = in_data_ch1 * gain_increase
        in_data_ch2 = in_data_ch2 * gain_increase
    elif (int(np.mean(dB_channels)) < int(dB_chs_mean)): # <
        in_data_ch1 = in_data_ch1 * gain_decrease
        in_data_ch2 = in_data_ch2 * gain_decrease
    elif (int(np.mean(dB_channels)) == int(dB_chs_mean)):
        in_data_ch1 = in_data_ch1 * gain_overall
        in_data_ch2 = in_data_ch2 * gain_overall
    out_data = write_2ch_out_data([in_data_ch1, in_data_ch1])
    #out_data = [in_data_ch1 * gain_overall, in_data_ch1 * gain_overall]
    #out_data = write_2ch_out_data(out_data)
    return (out_data, pa.paContinue)

#def sweep_rms():
#    rms = 0.0
#    sweep_data = sweep.readframes(samples_chunk)
#    while sweep_data != b'':
#        sweep_data = sweep.readframes(samples_chunk)
#        sweep_data = read_in_data(sweep_data)
#        rms = rms + calc_RMS(sweep_data)
#    global sweep_file_rms
#    sweep_file_rms = rms
#    return None

def sweep_rms():
    nframes = sweep.getnframes()
    frames = sweep.readframes(nframes)
    frames = np.fromstring(frames, dtype=np.int16)
    global sweep_file_rms
    sweep_file_rms = np.sqrt(np.sum(frames ** 2)/len(frames))
    return None
    

#def calib_read(in_data, frame_count, time_info, status):
#    # out_data = in_data
#    # Signal Processing Goes Here
#    # Read Incoming Signal but Output Sine Sweep
#    global sweep_in_rms
#    data_in_1, data_in_2 = read_2ch_in_data(in_data)
#    sweep_in_rms = sweep_in_rms + calc_RMS(data_in_1)
#    sweep_in_rms = sweep_in_rms + calc_RMS(data_in_2)
#    #sweep_in_rms = sweep_in_rms/2
#    out_data = sweep.readframes(frame_count)
#    return (out_data, pa.paContinue)
#
#def calib_play(in_data, frame_count, time_info, status):
#    # out_data = in_data
#    # Signal Processing Goes Here
#    # Read Incoming Signal but Output Sine Sweep
#    global sweep_in_rms
#    data_in_1, data_in_2 = read_2ch_in_data(in_data)
#    sweep_in_rms = sweep_in_rms + calc_RMS(data_in_1)
#    sweep_in_rms = sweep_in_rms + calc_RMS(data_in_2)
#    #sweep_in_rms = sweep_in_rms/2
#    out_data = sweep.readframes(frame_count)
#    return (out_data, pa.paContinue)

#def filt_process(input_signal):
#    input_dB = calc_dBSPL(input_signal)
#    # print (input_dB)
#    below_AC_frequency = filter_HighPass(input_signal)
#    at_AC_frequency = filter_BandPass(input_signal) * gain_at_AC
#    above_AC_frequency = filter_LowPass(input_signal)
#    out_data = (below_AC_frequency + at_AC_frequency + above_AC_frequency) * gain_overall
#    if (input_dB > dB_reference):
#        out_data = (out_data * gain_decrease)
#    else:
#        out_data = (out_data * gain_increase)
#    return out_data


def calibrate():
    print ('Calibrating Microphones ...')
    # Play
    stream_1 = calib_play.open(format = pa.get_format_from_width(sweep.getsampwidth()), 
                               channels = channel_count, 
                               rate = sweep.getframerate(), 
                               input = False, output = True, 
                               input_device_index = get_Mics()[0], 
                               output_device_index = get_Spkrs()[0])
    # Record
    stream_2 = calib_recd.open(format = pa.get_format_from_width(sweep.getsampwidth()), 
                               channels = channel_count, 
                               rate = sweep.getframerate(), 
                               input = True, output = False, 
                               input_device_index = get_Mics()[1], 
                               output_device_index = get_Spkrs()[0], 
                               frames_per_buffer = samples_chunk)
    
    frames = []
    in_rms = []
    out_data = sweep.readframes(int(sweep.getframerate()/10))
    for i in range(0, int(sweep.getframerate() / (samples_chunk * 5))):
        stream_1.write(out_data)
        out_data = sweep.readframes(int(sweep.getframerate()/10))
        in_data = stream_2.read(samples_chunk)
        frames.append(in_data)
        rms = np.fromstring(in_data, dtype=np.int16)
        rms = np.sqrt(np.mean(rms ** 2.0))
        in_rms.append(rms)
    global sweep_in_rms
    sweep_in_rms = np.mean(np.array(in_rms)) / 100.0

    stream_1.stop_stream()
    stream_2.stop_stream()
    stream_1.close()
    stream_2.close()
    sweep.close()
    calib_play.terminate()
    calib_recd.terminate()
    
    global sweep_file_rms
    #sweep_file_rms = sweep_file_rms/50.0
    #sweep_in_rms = sweep_in_rms/50.0
    
    print('Sine Sweep RMS from File = ' + str(sweep_file_rms))
    print('Sine Sweep RMS from Mics = ' + str(sweep_in_rms))
    if sweep_file_rms > sweep_in_rms:
        gain_ratio = sweep_in_rms/sweep_file_rms
    else:
        gain_ratio = sweep_file_rms/sweep_in_rms
    
    print ('Gain = ' + str(gain_ratio))
    print ('Microphones Calibrated !')
    time.sleep(5)
    return gain_ratio


def main():
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

sweep_rms()
gain_overall = calibrate()
main()

#take db
#threshold
#run calib once:
#    play arbitrary volume
#    observe vol change at mic
#    ratio = outvol/micin
#correction ratio from calib
#process

# End of File