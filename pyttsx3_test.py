import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 120)  #120 words per minute
engine.setProperty('volume', 0.9) 
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.say("Hello this is me talking.")
engine.say('Sally sells seashells by the seashore.')
engine.say('The quick brown fox jumped over the lazy dog.')
engine.say("Nananananananananananananana Batman.")
engine.say("This Is Fawking Amazing!") # Ignore This Please
engine.runAndWait()
#
## Works Awesome

#import pyttsx3
#
#def onStart(name):
#    print ('starting', name)
#
#def onWord(name, location, length):
#    print ('word', name, location, length)
#
#def onEnd(name, completed):
#    print ('finishing', name, completed)
#
#engine = pyttsx3.init()
#
#engine.connect('started-utterance', onStart)
#engine.connect('started-word', onWord)
#engine.connect('finished-utterance', onEnd)
#
#engine.say('The quick brown fox jumped over the lazy dog.')
#
#voices = engine.getProperty('voices')
#for voice in voices:
#    engine.setProperty('voice', voice.id)
#    print (voice.id)
#    engine.say('The quick brown fox jumped over the lazy dog.')
#
#engine.setProperty('voice', engine.getProperty('voices')[1])
#engine.say('Hello this is me talking!')
#
#engine.runAndWait()