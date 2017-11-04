import time
import random
import speech_recognition as sr
import pyttsx3

tts = pyttsx3.init()

tts.setProperty('rate', 120)  #120 words per minute
tts.setProperty('volume', 0.9) 
voices = tts.getProperty('voices')
# tts.setProperty('voice', voices[0].id)

with sr.Microphone() as source:
    sr.Recognizer().adjust_for_ambient_noise(source) # Do this only once - multiple times if necessary

tts.setProperty('voice', random.choice(voices).id)
tts.say('say something, i repeat what you say')
tts.runAndWait()
time.sleep(1.0)

def callback():
    with sr.Microphone() as source:
        sr.Recognizer().adjust_for_ambient_noise(source)
        audio = sr.Recognizer().listen(source)
    try:
        spoken = sr.Recognizer().recognize_google(audio)
        # print("Google Speech Recognition thinks you said " + spoken)
        tts.setProperty('voice', random.choice(voices).id)
        tts.say(spoken)
        print(spoken)
        tts.runAndWait()
        # return spoken
    except sr.UnknownValueError:
        # print("Google Speech Recognition could not understand audio")
        pass
        # tts.setProperty('voice', random.choice(voices).id)
        # tts.say('sorry, please repeat')
        # tts.runAndWait()
    except sr.RequestError as e:
        # print("Could not request results from Google Speech Recognition service; {0}".format(e))
        tts.setProperty('voice', random.choice(voices).id)
        tts.say('please connect to internet')
        tts.runAndWait()

#stop_listening = rcg.listen_in_background(mic, callback)
#stop_listening()  # calling this function requests that the background listener stop listening

while True:
    callback()
    time.sleep(0.0)


# End of File