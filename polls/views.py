from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_str
from sys import byteorder
from array import array
from struct import pack
import speech_recognition as sr
from translate import Translator
from gtts import gTTS
import os
from sys import byteorder
from array import array
from struct import pack
from translate import Translator
import speech_recognition as sr
# Import the required module for text
# to speech conversion
from gtts import gTTS
from .forms import UploadFileForm
import pyaudio
import wave
from mimetypes import guess_type

THRESHOLD = 300
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

import pyaudio
import wave
from django.http import JsonResponse
# Create your views here.
def  index(request):
    return render(request,"index.html",{})

def  language(request):
            language=request.POST['language']
            english=request.POST['english']
            # text = open('media/demo_eng_text111.txt', 'w')
            # text.write(language)

            #import shutil
            #shutil.rmtree('C:\\Users\\a\\Desktop\\django_project\\myproject\\media\\')

            def is_silent(snd_data):
                "Returns 'True' if below the 'silent' threshold"
                return max(snd_data) < THRESHOLD


            def normalize(snd_data):
                "Average the volume out"
                MAXIMUM = 16384
                times = float(MAXIMUM) / max(abs(i) for i in snd_data)

                r = array('h')
                for i in snd_data:
                    r.append(int(i * times))
                return r


            def trim(snd_data):
                "Trim the blank spots at the start and end"
                def _trim(snd_data):
                    snd_started = False
                    r = array('h')

                    for i in snd_data:
                        if not snd_started and abs(i) > THRESHOLD:
                            snd_started = True
                            r.append(i)

                        elif snd_started:
                            r.append(i)
                    return r

                # Trim to the left
                snd_data = _trim(snd_data)

                # Trim to the right
                snd_data.reverse()
                snd_data = _trim(snd_data)
                snd_data.reverse()
                return snd_data


            def add_silence(snd_data, seconds):
                "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
                r = array('h', [0 for i in range(int(seconds * RATE))])
                r.extend(snd_data)
                r.extend([0 for i in range(int(seconds * RATE))])
                return r


            def record():
                """
                Record a word or words from the microphone and
                return the data as an array of signed shorts.

                Normalizes the audio, trims silence from the
                start and end, and pads with 0.5 seconds of
                blank sound to make sure VLC et al can play
                it without getting chopped off.
                """
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT, channels=1, rate=RATE,
                                input=True, output=True,
                                frames_per_buffer=CHUNK_SIZE)

                num_silent = 0
                snd_started = False

                r = array('h')

                while 1:
                    # little endian, signed short
                    snd_data = array('h', stream.read(CHUNK_SIZE))
                    if byteorder == 'big':
                        snd_data.byteswap()
                    r.extend(snd_data)

                    silent = is_silent(snd_data)

                    if silent and snd_started:
                        num_silent += 1
                    elif not silent and not snd_started:
                        snd_started = True

                    if snd_started and num_silent > 30:
                        break

                sample_width = p.get_sample_size(FORMAT)
                stream.stop_stream()
                stream.close()
                p.terminate()

                r = normalize(r)
                r = trim(r)
                r = add_silence(r, 0.5)
                return sample_width, r


            def record_to_file(path):
                "Records from the microphone and outputs the resulting data to 'path'"
                sample_width, data = record()
                data = pack('<' + ('h' * len(data)), *data)

                wf = wave.open(path, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(sample_width)
                wf.setframerate(RATE)
                wf.writeframes(data)
                wf.close()

            if english == "true":
                print("please speak a word into the microphone")
                record_to_file('media\\aud_1.wav')
                print("done - result written to demo.wav")

                r = sr.Recognizer()

                audio_eng = sr.AudioFile('media\\aud_1.wav')
                with audio_eng as source:
                    print("start")
                    audio = r.record(source)
                print("start print")
                # print(r.recognize_google(audio))
                result = r.recognize_google(audio)
                text = open('media\\text_1.txt', 'w', encoding="utf-8")
                # text.write(r.recognize_google(audio))
                text.write(r.recognize_google(audio))
                text.close()
                #result = "done"
                # TEXT TO TEXT
                if language == "German":
                    translator = Translator(to_lang="German", from_lang="English")
                if language == "Swedish":
                    translator = Translator(to_lang="Swedish", from_lang="English")
                if language == "Telugu":
                    translator = Translator(to_lang="Telugu", from_lang="English")
                if language == "Spanish":
                    translator = Translator(to_lang="Spanish", from_lang="English")
                if language == "French":
                    translator = Translator(to_lang="French", from_lang="English")
                text = open("media\\text_1.txt", "r", encoding="utf-8")
                text_w = open("media\\text_2.txt", "w", encoding="utf-8")
                for line in text:
                    translation = translator.translate(line)
                    print(translation)
                    text_w.write(translation + "\n")
                result_fren = translation
                text.close()
                text_w.close()

                # TEXT TO AUDIO CONVERTION
                text_file = open("media\\text_2.txt", "r", encoding="utf-8")

                # Passing the text and language to the engine,
                # here we have marked slow=False. Which tells
                # the module that the converted audio should
                # have a high speed
                if language=="German":
                    myobj = gTTS(text=text_file.read(), lang='de', slow=False)
                if language=="Swedish":
                    myobj = gTTS(text=text_file.read(), lang='sv', slow=False)
                if language == "Telugu":
                    myobj = gTTS(text=text_file.read(), lang='te', slow=False)
                if language == "Spanish":
                    myobj = gTTS(text=text_file.read(), lang='es', slow=False)
                if language == "French":
                    myobj = gTTS(text=text_file.read(), lang='fr', slow=False)

                # Saving the converted audio in a mp3 file named
                # welcome
                myobj.save("media\\aud_2.wav")
                text_file.close()

                # Playing the converted file
                #os.system("C:\\Users\\a\\Desktop\\django_project\\myproject\\media\\demo_non.mp3")

            elif english == "false":
                print("please speak a word into the microphone")
                record_to_file('media\\aud_2.wav')
                print("done - result written to demo.wav")

                r = sr.Recognizer()

                audio_eng = sr.AudioFile('media\\aud_2.wav')
                with audio_eng as source:
                    print("start")
                    audio = r.record(source)
                print("start print")
                text = open('media\\text_2.txt', 'w', encoding="utf-8")
                # print(r.recognize_google(audio))
                if language == "German":
                    result = r.recognize_google(audio, language="de-DE")
                    text.write(r.recognize_google(audio, language="de-DE"))
                if language == "Telugu":
                    result = r.recognize_google(audio, language="te-IN")
                    text.write(r.recognize_google(audio, language="te-IN"))
                if language == "Swedish":
                    result = r.recognize_google(audio, language="sv-SE")
                    text.write(r.recognize_google(audio, language="sv-SE"))
                if language == "French":
                    result = r.recognize_google(audio, language="fr-FR")
                    text.write(r.recognize_google(audio, language="fr-FR"))
                if language == "Spanish":
                    result = r.recognize_google(audio, language="es-ES")
                    text.write(r.recognize_google(audio, language="es-ES"))
                text.close()
                #result = "done"
                # TEXT TO TEXT
                if language == "German":
                    translator = Translator(to_lang="English", from_lang="German")
                if language == "Swedish":
                    translator = Translator(to_lang="English", from_lang="Swedish")
                if language == "Telugu":
                    translator = Translator(to_lang="English", from_lang="Telugu")
                if language == "Spanish":
                    translator = Translator(to_lang="English", from_lang="Spanish")
                if language == "French":
                    translator = Translator(to_lang="English", from_lang="French")
                text = open("media\\text_2.txt", "r", encoding="utf-8")
                text_w = open("media\\text_1.txt", "w", encoding="utf-8")
                for line in text:
                    translation = translator.translate(line)
                    print(translation)
                    text_w.write(translation + "\n")
                result_fren = translation
                text.close()
                text_w.close()

                # TEXT TO AUDIO CONVERTION
                text_file = open("media\\text_1.txt", "r", encoding="utf-8")

                # Passing the text and language to the engine,
                # here we have marked slow=False. Which tells
                # the module that the converted audio should
                # have a high speed
                myobj = gTTS(text=text_file.read(), lang='en', slow=False)

                # Saving the converted audio in a mp3 file named
                # welcome
                myobj.save("media\\aud_1.wav")
                text_file.close()

                # Playing the converted file
                #os.system("C:\\Users\\a\\Desktop\\django_project\\myproject\\media\\demo_eng.mp3")


            return HttpResponse(result + "\n" +":"+ result_fren+'\n') # if everything is OK
            # nothing went well
            return HttpRepsonse('FAIL!!!!!')

def upload(request):

      filename=request.FILES['filevalue'].name
      language=request.POST['languagevalue']

      handle_uploaded_file(request.FILES['filevalue'])
      sourse_text = open('media\\name.txt','r')
      dest_text = open('media\\dest_name.txt','w', encoding="utf-8")
      if language == "German":
          translator = Translator(to_lang="German", from_lang="English")
      if language == "Spanish":
          translator = Translator(to_lang="Spanish", from_lang="English")
      if language == "Telugu":
        translator = Translator(to_lang="Telugu", from_lang="English")
      if language == "French":
          translator = Translator(to_lang="French", from_lang="English")
      if language == "Swedish":
          translator = Translator(to_lang="Swedish", from_lang="English")
      for line in sourse_text:
          translation = translator.translate(line)
          dest_text.write(translation + "\n")
      sourse_text.close()
      dest_text.close()
      return HttpResponseRedirect('/polls/')



def handle_uploaded_file(f):
    with open('media\\name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
def download(request):
    file_path = 'media\\dest_name.txt'
    path_to_file='C:\\Users\\a\\Desktop\\download'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh, content_type=guess_type(file_path)[0])
            response['X-Sendfile'] = smart_str(path_to_file)
            response['Content-Disposition'] = "attachment; filename='fname.ext'"
            return response
    raise Http404
