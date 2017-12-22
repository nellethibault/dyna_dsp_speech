import pyaudio
import wave
import scipy.io.wavfile as spwf

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 2

wf = wave.open('pypinknoise.wav', 'r')

p = pyaudio.PyAudio()

# play
stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# record
stream2 = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

data = wf.readframes(wf.getnframes())
stream1.write(data)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream2.read(CHUNK)
    frames.append(data)

print("* done recording")


stream1.stop_stream()
stream1.close()


stream2.stop_stream()
stream2.close()




frames = b''.join(frames)
wf = wave.open('pinkrecord.wav', 'wb')
wf.setnchannels(2)
wf.setsampwidth(p.get_sample_size(pyaudio.paFloat32))
wf.setframerate(RATE)
wf.writeframes(frames)
wf.close()


p.terminate()