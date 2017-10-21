#!/usr/bin/env python3
# Requires PyAudio and PySpeech.
 
import speech_recognition as sr
import time
import os
from gtts import gTTS
 
def speak(audioString):
    print(audioString)
    tts = gTTS(text=audioString, lang='en')
    tts.save("audio.mp3")
    os.system("mpg321 audio.mp3")
 
def recordAudio():
    # Record Audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
 
    # Speech recognition using Google Speech Recognition
    data = ""
    try:
        # Uses the default API key
        # To use another API key: `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        data = r.recognize_google(audio)
        print("You said: " + data)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
 
    return data
 
def jarvis(data):
    if "parseval higher" in data:
        speak("Increasing Volume")
        print("Increasing Volume")
        return 1
    elif "parseval lower" in data:
        speak("Decreaing Volume")
        print("Decreaing Volume")
        return -1
    else:
        return 0
    
# initialization
time.sleep(2)
speak("Hi, what can I do for you?")
while 1:
    data = recordAudio()
    action = jarvis(data)
    print(action)