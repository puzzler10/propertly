
### File only runs for audio decoding. Not if you change input yourself.
import io, glob, sys, base64
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import types
from IPython.core.debugger import set_trace
import pickle
sys.path.append("./app/")  # path contains python_file.py
from helper import *
from references import SPEECH_CONTEXT_PHRASES, path_audio


### Authentication
# WILL NEED TO CHANGE THIS
credentials_file = 'natural-language-search-4bd529dbad13.json'
# Instantiates a client
client = speech.SpeechClient.from_service_account_file(credentials_file)

### Load audio file manually
#prototype_audio_files = glob.glob(path_audio + 'prototype*')
#prototype_audio_files.sort()
#file_name = prototype_audio_files[0]
## Loads the audio into memory
#with io.open(file_name, 'rb') as audio_file:
#    content = audio_file.read()
#    content_b64 = base64.b64encode(content) # To turn into base64
#    content_b64_decode = base64.decodebytes(content_b64)
#    audio = types.RecognitionAudio(content=content_b64_decode)


pickle_in = open("contents.pickle","rb")
contents = pickle.load(pickle_in)
content_type, content_string = contents.split(',')
decoded = base64.b64decode(content_string)
audio = types.RecognitionAudio(content=decoded)



def encode_audio(audio):
  audio_content = audio.read()
  return base64.b64encode(audio_content)


#### Specify config
## Specify metadata
metadata = speech.types.RecognitionMetadata()
metadata.interaction_type = speech.enums.RecognitionMetadata.InteractionType.VOICE_SEARCH
metadata.industry_naics_code_of_audio = 531210
metadata.microphone_distance = speech.enums.RecognitionMetadata.MicrophoneDistance.NEARFIELD
metadata.original_media_type = speech.enums.RecognitionMetadata.OriginalMediaType.AUDIO
# Note: change this if doing smartphone audio recording
metadata.recording_device_type = speech.enums.RecognitionMetadata.RecordingDeviceType.PC
metadata.original_mime_type = "audio/flac"
metadata.audio_topic = "Voice search for real estate properties"
## Phrase hints
speech_context = types.SpeechContext(phrases=SPEECH_CONTEXT_PHRASES)
## Final config
config = types.RecognitionConfig(
    encoding= "FLAC",
    language_code='en-au',
    max_alternatives=1,
    model="command_and_search",
    enable_word_confidence=True,
    metadata=metadata,
    speech_contexts=[speech_context],
    enable_automatic_punctuation = True)

### Send off audio and config to get translated
response = client.recognize(config, audio)
for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))
sen = result.alternatives[0].transcript

print(sen)

pickle_out = open("sen.pickle","wb")
pickle.dump(sen, pickle_out)
pickle_out.close()













