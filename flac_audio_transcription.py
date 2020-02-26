filepath = "/home/rohit/wishfin-python/audio/"     #Input audio file path
output_filepath = "/home/rohit/wishfin-python/transcripts/" #Final transcript path
bucketname = "rohit_bucket" #Name of the bucket created in the step before

# Import libraries
from pydub import AudioSegment
import io
import os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import wave
from google.cloud import storage
import pandas as pd
import csv


# def stereo_to_mono(audio_file_name):                         // for conversion of stereo to mono channel
#     if audio_file_name.split('.')[1] == 'flac':
#         sound = AudioSegment.from_wav(audio_file_name)
#         sound = sound.set_channels(1)
#         sound.export(audio_file_name, format="flac")

# def frame_rate_channel(audio_file_name):                    // for getting frame rate and channel
#     if audio_file_name.split('.')[1] == 'wav':
#         with wave.open(audio_file_name, "rb") as wave_file:
#             frame_rate = wave_file.getframerate()
#             channels = wave_file.getnchannels()
#             return frame_rate,channels


# def upload_blob(bucket_name, source_file_name, destination_blob_name):           //uploading the audio file on cloud server
#     if audio_file_name.split('.')[1] == 'flac':
#         storage_client = storage.Client()
#         bucket = storage_client.get_bucket(bucket_name)
#         blob = bucket.blob(destination_blob_name)

#         blob.upload_from_filename(source_file_name)


def google_transcribe(audio_file_name):             // transcribing the audio with the help of API

    file_name = filepath + audio_file_name

    # The name of the audio file to transcribe

    #frame_rate, channels = frame_rate_channel(file_name)

    #stereo_to_mono(file_name)

    bucket_name = bucketname
    source_file_name = filepath + audio_file_name
    destination_blob_name = audio_file_name

    # upload_blob(bucket_name, source_file_name, destination_blob_name)

    gcs_uri = 'gs://' + bucketname + '/' + audio_file_name
    transcript = ''

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.AMR,
    sample_rate_hertz=8000,
    language_code='hi-IN')

    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    confidence=0
    num=0
    for result in response.results:
        num=num+1
        transcript += result.alternatives[0].transcript
        confidence=confidence+result.alternatives[0].confidence
    confidence=confidence/num
    return transcript,confidence 


def write_transcripts(transcript_filename,transcript):               // saving transcription into a file
    f= open(output_filepath + transcript_filename,"w+")          
    f.write(transcript)
    f.close()

if __name__ == "__main__":
    data=[]
    for audio_file_name in os.listdir(filepath):
        #mp3_to_wav(audio_file_name)
        if audio_file_name.split('.')[1] == 'flac':
            transcript , confidence = google_transcribe(audio_file_name)
            #transcript_filename = audio_file_name.split('.')[0] + '.txt'
            #write_transcripts(transcript_filename,transcript)
            data.append([audio_file_name,transcript,confidence])
    with open("output.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerows(data)        
    f.close()
