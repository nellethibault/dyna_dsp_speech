import pyaudio
import wave
import scipy.io.wavfile as spwf

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 1

wf = wave.open('pypinknoise.wav', 'r')

p = pyaudio.PyAudio()

# play
stream1 = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)

while data != '':
    stream1.write(data)
    data = wf.readframes(CHUNK)

stream1.stop_stream()
stream1.close()

# record
stream2 = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream2.read(CHUNK)
    frames.append(data)

print("* done recording")

frames = b''.join(frames)
spwf.write('pinkrecord.wav', RATE, frames)

stream2.stop_stream()
stream2.close()

p.terminate()
