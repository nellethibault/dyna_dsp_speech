import time
import random
import speech_recognition as sr
import pyttsx3

rcg = sr.Recognizer()
mic = sr.Microphone()
spk = pyttsx3.init()

spk.setProperty('rate', 120)  #120 words per minute
spk.setProperty('volume', 0.9) 
voices = spk.getProperty('voices')
# spk.setProperty('voice', voices[1].id)

with mic as source:
    rcg.adjust_for_ambient_noise(source) # Do this only once - multiple times if necessary

spk.setProperty('voice', random.choice(voices).id)
spk.say('say something, i repeat what you say')
spk.runAndWait()
time.sleep(1.0)

def callback():
    with sr.Microphone() as source:
        sr.Recognizer().adjust_for_ambient_noise(source)
        audio = sr.Recognizer().listen(source)
    try:
        spoken = sr.Recognizer().recognize_google(audio)
        # print("Google Speech Recognition thinks you said " + spoken)
        spk.setProperty('voice', random.choice(voices).id)
        spk.say(spoken)
        print(spoken)
        spk.runAndWait()
        # return spoken
    except sr.UnknownValueError:
        # print("Google Speech Recognition could not understand audio")
        pass
        # spk.setProperty('voice', random.choice(voices).id)
        # spk.say('sorry, please repeat')
        # spk.runAndWait()
    except sr.RequestError as e:
        # print("Could not request results from Google Speech Recognition service; {0}".format(e))
        spk.setProperty('voice', random.choice(voices).id)
        spk.say('please connect to internet')
        spk.runAndWait()

#stop_listening = rcg.listen_in_background(mic, callback)
#stop_listening()  # calling this function requests that the background listener stop listening

while True:
    callback()
    time.sleep(0.0)


# End of File