#gtts(google text to speech) is to convert text to audio
from gtts import gTTS
import spacy
import pyaudio
import speech_recognition as sr
import pyglet
import time, os

recognition = sr.Recognizer()
def init_the_mic(mic):
    print("Please wait, while microphone is callibrating. It will take 4 seconds.")
    print("You can speak after you hear the beep.")
    with mic as source:
        recognition.adjust_for_ambient_noise(source, duration=4)

def sp_to_txt(mic):
    init_the_mic(mic)
    speech_customer = ''
    with mic as source:
        audio_customer=recognition.listen(source)
    try:
        speech_customer = recognition.recognize_google(audio_customer)
        return speech_customer
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand what you said!")
    except sr.RequestError as e:
        print("Could not request results from Google SRS; {0}".format(e))

def txt_to_sp(text, lang) :
	file = gTTS(text=text, lang=lang)
	fileN = 'txt_to_sp.mp3'
	file.save(fileN)

	say = pyglet.media.load(fileN, streaming=False)
	say.play()

	time.sleep(say.duration)
	os.remove(fileN)