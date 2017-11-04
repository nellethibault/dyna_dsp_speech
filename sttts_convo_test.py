import time
import random
import speech_recognition as sr
import pyttsx3

tts = pyttsx3.init()

tts.setProperty('rate', 120)  #120 words per minute
tts.setProperty('volume', 0.9) 
voices = tts.getProperty('voices')
# tts.setProperty('voice', voices[1].id)

with sr.Microphone() as source:
    sr.Recognizer().adjust_for_ambient_noise(source) # Do this only once - multiple times if necessary

tts.setProperty('voice', random.choice(voices).id)
tts.say('you just turned me on')
tts.say('say something, i repeat what you say')
tts.runAndWait()
time.sleep(1.0)

def reply(string):
    string = string.lower()
    if (('hello' in string) or ('hey' in string) or ('hi' in string)):
        tts.say('hello there')
        tts.runAndWait()
    elif (('how are you' in string) or 
          ('how\'re you' in string)):
        tts.say('i am good!, thank you for asking, how are you?')
        tts.runAndWait()
    elif (('who are you' in string) or 
          ('who\'re you' in string)):
        tts.say('i am your musical friend, dyna-e-q, from paarsehval') # DO NOT CHANGE PAARSEHVAL - NOT A TYPO !!!
        tts.runAndWait()
    elif ('good' in string):
        if ('morning' in string):
            tts.say('happy morning to you too')
            tts.runAndWait()
        elif ('afternoon' in string):
            tts.say('good afternoon to you too')
            tts.runAndWait()
        elif ('evening' in string):
            tts.say('good evening to you too')
            tts.runAndWait()
        elif ('night' in string):
            tts.say('nighty night, tighty tight')
            tts.runAndWait()
        elif ('not' in string):
            tts.say('sorry to hear that, i will try to make you feel good')
            tts.runAndWait()
        else:
            tts.say('glad to hear that')
            tts.runAndWait()
    elif (('fine' in string) or ('great' in string) or 
          ('awesome' in string) or ('fantastic' in string) or 
          ('wonderful' in string) or ('excellent' in string)):
        tts.say('glad to hear that')
        tts.runAndWait()
    elif ('bad' in string):
        if ('not' in string):
            tts.say('glad to hear that')
            tts.runAndWait()
        else:
            tts.say('sorry to hear that, i will try to make you feel good')
            tts.runAndWait()
    elif (('sad' in string) or ('terrible' in string) or 
          ('sick' in string) or ('pathetic' in string) or 
          ('miserable' in string) or ('worse' in string) or 
          ('worst' in string)):
        tts.say('sorry to hear that, i will try to make you feel good')
        tts.runAndWait()
    elif (('increase' in string) or 
           ('raise' in string) or 
           ('higher' in string) and 
           ('volume' in string)):
        tts.say('raising the volume')
        tts.runAndWait()
    elif (('decrease' in string) or 
           ('reduce' in string) or 
           ('lower' in string) and 
           ('volume' in string)):
        tts.say('reducing the volume')
        tts.runAndWait()
    elif (('thank you' in string) or 
          ('thanks' in string)):
        tts.say('you are welcome')
        tts.runAndWait()        
    elif ('i love you' in string):
        tts.say('i love you too, with all i\'ve got')
        tts.runAndWait()
    else:
        tts.say(string)
        tts.runAndWait()
    return None

def callback():
    with sr.Microphone() as source:
        # sr.Recognizer().adjust_for_ambient_noise(source)
        audio = sr.Recognizer().listen(source)
    try:
        spoken = sr.Recognizer().recognize_google(audio)
        print(spoken)
        # print("Google Speech Recognition thinks you said " + spoken)
        tts.setProperty('voice', random.choice(voices).id)
        reply(spoken)
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