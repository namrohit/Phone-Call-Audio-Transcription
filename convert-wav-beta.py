filepath = "/home/rohit/wishfin-python/audio/"     #Input audio file path
output_filepath = "/home/rohit/wishfin-python/transcripts/" #Final transcript path
bucketname = "rohit-bucket" #Name of the bucket created in the step before

# Import libraries
from pydub import AudioSegment
import io
import os
#from google.cloud import speech
# from google.cloud.speech import enums
# from google.cloud.speech import types
from google.cloud import speech_v1p1beta1 as speech

import wave
from google.cloud import storage
import pandas as pd
import csv

# def mp3_to_wav(audio_file_name):
#     if audio_file_name.split('.')[1] == 'mp3':
#         sound = AudioSegment.from_mp3(audio_file_name)
#         audio_file_name = audio_file_name.split('.')[0] + '.wav'
#         sound.export(audio_file_name, format="wav")


# def stereo_to_mono(audio_file_name):
#     if audio_file_name.split('.')[1] == 'flac':
#         sound = AudioSegment.from_wav(audio_file_name)
#         sound = sound.set_channels(1)
#         sound.export(audio_file_name, format="flac")

# def frame_rate_channel(audio_file_name):
#     if audio_file_name.split('.')[1] == 'wav':
#         with wave.open(audio_file_name, "rb") as wave_file:
#             frame_rate = wave_file.getframerate()
#             channels = wave_file.getnchannels()
#             return frame_rate,channels


# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     if audio_file_name.split('.')[1] == 'flac':
#         storage_client = storage.Client()
#         bucket = storage_client.get_bucket(bucket_name)
#         blob = bucket.blob(destination_blob_name)

#         blob.upload_from_filename(source_file_name)


def google_transcribe(audio_file_name):

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



    metadata=speech.types.RecognitionMetadata()
    metadata.interaction_type=(
        speech.enums.RecognitionMetadata.InteractionType.PHONE_CALL
    )
    metadata.microphone_distance=(
        speech.enums.RecognitionMetadata.MicrophoneDistance.NEARFIELD
    )
    metadata.recording_device_type = (
        speech.enums.RecognitionMetadata.RecordingDeviceType.PHONE_LINE
    )


    client = speech.SpeechClient()
    first_lang='en-IN'
    second_lang='hi'
    audio = speech.types.RecognitionAudio(uri=gcs_uri)

    config = speech.types.RecognitionConfig(
    encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=8000,
    language_code=first_lang,
    alternative_language_codes=[second_lang],
    metadata=metadata,
    max_alternatives=10,
    # enable_word_confidence=True,
    speech_contexts=[speech.types.SpeechContext(
            phrases=['life insurance'],
            
            )
            ]
    )

    # Detects speech in the audio file
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=10000)

    confidence=0

    


    num=0
    # for i, result in enumerate(response.results):
    #     alternative = result.alternatives[1]
    #     print('-' * 20)
    #     print('First alternative of result {}: {}'.format(i, alternative))
    #     print(u'Transcript: {}'.format(alternative.transcript))
    for result in response.results:
        con=0
        tran=''
        for alternative in result.alternatives:
            if( alternative.confidence>con):
                con=alternative.confidence
                tran=alternative.transcript
            
        # print("=====================================")
        # for word in result.words:
        #     print('word is === '+word.word)
        #     print('start time = '+word.start_time)
        #     print('end time = '+word.end_time)

        # print("=====================================")

        transcript += tran
        confidence=con
        transcript+="======="+str(con)
    
    return transcript,confidence 


def write_transcripts(transcript_filename,transcript):
    f= open(output_filepath + transcript_filename,"w+")
    f.write(transcript)
    f.close()

if __name__ == "__main__":
    data=[]
    for audio_file_name in os.listdir(filepath):
        #mp3_to_wav(audio_file_name)
        if audio_file_name.split('.')[1] == 'wav':
            transcript , confidence = google_transcribe(audio_file_name)
            #transcript_filename = audio_file_name.split('.')[0] + '.txt'
            #write_transcripts(transcript_filename,transcript)
            data.append([audio_file_name,transcript,confidence])
    with open("output.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerows(data)        
    f.close()
