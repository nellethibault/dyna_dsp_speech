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

mic_index = []
for i in range(audio.get_device_count()):
    devices = audio.get_device_info_by_index(i)
    if (devices['name'][0:10] == 'Microphone'):
        mic_index.append(devices['index'])

spkr_index = []
for i in range(audio.get_device_count()):
    devices = audio.get_device_info_by_index(i)
    if (devices['name'][0:8] == 'Speakers'):
        spkr_index.append(devices['index'])
    
stream_1 = audio.open(format = sampling_format, channels = channel_count, 
                      rate = sampling_frequency, input = True, 
                      output = True, # Change output = True to hear the Mics 
                      input_device_index = mic_index[0], 
                      output_device_index = spkr_index[0], 
                      frames_per_buffer = samples_chunk)

stream_2 = audio.open(format = sampling_format, channels = channel_count, 
                      rate = sampling_frequency, input = True, 
                      output = True, # Change output = True to hear the Mics 
                      input_device_index = mic_index[1], 
                      output_device_index = spkr_index[0], 
                      frames_per_buffer = samples_chunk)

while True:
    for i in range(0, int(sampling_frequency / samples_chunk * sampling_time)):
        data_1 = stream_1.read(samples_chunk)
        data_1 = np.fromstring(data_1, dtype=np.float32)
        rms_1 = np.sqrt(np.mean(data_1 ** 2.0))
        dB_1 = (10.0 * np.log10(np.mean(data_1 ** 2.0))) + dB_error_correct
        data_2 = stream_2.read(samples_chunk)
        data_2 = np.fromstring(data_2, dtype=np.float32)
        rms_2 = np.sqrt(np.mean(data_2 ** 2.0))
        dB_2 = (10.0 * np.log10(np.mean(data_2 ** 2.0))) + dB_error_correct
    
        rms_avg = (rms_1 + rms_2) / 2
        prev_rms_avg = rms_avg
        dB_avg = (dB_1 + dB_2) / 2
        prev_dB_avg = dB_avg
    
        if (dB_avg <= dB_threshold):
            if dB_avg > prev_dB_avg:
                volume.SetMasterVolumeLevel(round(volume.GetMasterVolumeLevel(), 1) + 0.5, None)
            elif dB_avg < prev_dB_avg:
                volume.SetMasterVolumeLevel(round(volume.GetMasterVolumeLevel(), 1) - 0.5, None)
            else:
                volume.SetMasterVolumeLevel(round(volume.GetMasterVolumeLevel(), 1), None)
        else:
            volume.SetMasterVolumeLevel(round(volume.GetMasterVolumeLevel(), 1) - 0.5, None)
    time.sleep(0.1)

stream_1.stop_stream()
stream_2.stop_stream()
audio.terminate()

# End of File