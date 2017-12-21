import numpy as np
import scipy.io.wavfile as spwf
import pyaudio as pa
import time
import wave

# Instantiations
audio = pa.PyAudio()
#devices = AudioUtilities.GetSpeakers()
#interface = devices.Activate(
#        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#volume = cast(interface, POINTER(IAudioEndpointVolume))

def pinknoise(n_samples):
    # This Function Generates as Sequence of Pink (Flicker) Noise Samples
    # n_samples - no. of samples to be returned in a row vector
    
    # Defining Length of Vector and Ensuring that 'm' is Even
    if (np.remainder(n_samples, 2) == 0):
        m = n_samples + 1
    else:
        m = n_samples
    
    # Generate White Noise
    x = np.random.randn(1, m)
    
    # FFT
    X = np.fft.fft(x)
    
    # Prepare a Vector with Frequency Indices
    n_unique_pts = int(m) # No. of Unique FFT Points
    n = np.array([i for i in range(1, n_unique_pts)]) # Vector with Frequency Indices
    
    # Manipulating the Left Half of the Sprectrum so that 
    # Power Spectrum Density is Proportional to the Frequency 
    # by a Factor of 1/f, i.e, Amplitudes Proportional to 1/sqrt(f)
    X = np.array(X.ravel()[0 : (n_unique_pts - 1)])
    X = X / np.sqrt(n)
    
    # Preparing the Right Half of the Spectrum - A Conjugate Copy of Left Half
    # Except the DC Component and Nyquist Components - They are Unique
    # And Reconstruct the Whole Spectrum
    X = np.hstack([X, np.conj(X[1 : -2])])
    
    # IFFT
    out_pink = np.fft.ifft(X).real
    
    # Ensuring out_pink is same length as n_samples
    out_pink = out_pink[0 : len(n)]
    
    # Ensuring Unity Standard Deviation and Zero Mean Values
    out_pink = out_pink - np.mean(out_pink)
    out_pink = out_pink / np.std(out_pink)
    
    # Return out_pink - a row vector of pink (flicker) noise samples
    out_pink = out_pink.astype(np.float32)
    return out_pink

fs = 48000
T = 10
N = np.round(fs * T)

t = time.time()
xpink = pinknoise(N)
t = time.time() - t
print('Time Taken to Generate Pink Noise for T = %.2f Secs is %.3f Secs.' % (T, t))

# For Two Channels
pink_noise = np.vstack([xpink, xpink]).T
#spwf.write('pypinknoise.wav', fs, pink_noise)
wf = wave.open('pypinknoise.wav', 'wb')
wf.setnchannels(2)
wf.setsampwidth(audio.get_sample_size(pa.paFloat32))
wf.setframerate(fs)
wf.writeframes(b''.join(pink_noise))
wf.close()

# End of File