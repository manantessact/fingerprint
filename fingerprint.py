import json
import shutil
import sys
from pydub.silence import split_on_silence
import time 
import os
import errno
from pydub import AudioSegment
import subprocess as sp                                                                                                
from dejavu import Dejavu                                                                                              
from dejavu.recognize import FileRecognizer                                                                            
                                                                                                                       
config = {                                                                                                             
     "database": {                                                                                                     
         "host": "127.0.0.1",                                                                                          
         "user": "root",                                                                                               
         "passwd": 'root',                                                                                             
         "db": "dejavu",                                                                                               
     }                                                                                                                 
}                                                                                                                      
                                                                                                                       
djv = Dejavu(config)       

fing = ['07 Tu Jo Mila',
 'Aa 1_M00003',
 'Aa 2_M00047',
 'Allah-Waariyan-(RaagSong',
 'Allah Waariyan- Verse 1_M00044',
 'Angry 1_M00028',
 'Emotional 1_M00013',
 'Emotional 2_M00017',
 'Emotional 3_M00019',
 'Emotional 4_M00020',
 'Emotional 5_M00043',
 'KKB_Theme_M00001',
 'Relax _Fun 10_M00018',
 'Relax _Fun 11_M00021',
 'Relax _Fun 12_M00022',
 'Relax _Fun 13_M00023',
 'Relax _Fun 14_M00024',
 'Relax _Fun 15_M00025',
 'Relax _Fun 16_M00029',
 'Relax_Fun 17_M00033',
 'Relax_Fun 18_M00036',
 'Relax_Fun 19_M00037',
 'Relax_Fun 1_M00002',
 'Relax_Fun 20_M00039',
 'Relax _Fun 2_M00004',
 'Relax _Fun 3_M00005',
 'Relax _Fun 4_M00006',
 'Relax _Fun 5_M00007',
 'Relax _Fun 6_M00008',
 'Relax _Fun 7_M00010',
 'Relax _Fun 8_M00015',
 'Relax _Fun 9_M00016',
 'Tension 10_M00038',
 'Tension 11_M00040',
 'Tension 12_M00041',
 'Tension 13_M00042',
 'Tension 14_M00045',
 'Tension 15_M00046',
 'Tension 1_M00009',
 'Tension 2_M00011',
 'Tension 3_M00012',
 'Tension 4_M00014',
 'Tension 6_M00031',
 'Tension 7_M00032',
 'Tension 8_M00034',
 'Tension 9_M00035',
 'Tu Jo Mila- Intro_M00026',
 'Tu Jo Mila- Second line and hook line_M00030',
 'Tu Jo Mila- Verse 1_M00027']


def check_or_create_file(file_path):                                                                                   
    if not os.path.exists(os.path.dirname(file_path)):                                                                 
        try:                                                                                                           
            os.makedirs(os.path.dirname(file_path))                                                                    
        except OSError as exc:  # Guard against race condition                                                         
            if exc.errno != errno.EEXIST:                                                                              
                raise                                                                                                  
                                                                                                                       
def break_audio(input_file, tmp_folder, overlap):
    FFPROBE_BIN = "ffprobe"                                                                                            
    FFMPEG_BIN = "ffmpeg"                                                                                              
    command = [FFPROBE_BIN,                                                                                            
               '-v', 'quiet',                                                                                          
               '-print_format', 'json',                                                                                
               '-show_format',                                                                                         
               '-show_streams',                                                                                        
               input_file]                                                                                             
    output = sp.check_output(command)                                                                                  
    output = output.decode('utf-8')                                                                                    
    metadata_output = json.loads(output)                                                                               
    duration = metadata_output['streams'][0]['duration']                                                               
    sample_rate = metadata_output['streams'][0]['sample_rate']                                                         
    print("duration : " + duration + " seconds")                                                                       
    print("sample_rate : " + sample_rate)                                                                              
    overlap_dur = int(float(duration)) - (overlap - 1)
    check_or_create_file(tmp_folder)                                                                                   
    for i in range(overlap_dur):                                                                                       
        os.system("ffmpeg -v quiet -ss {} -i '{}' -t {} {}/{}.mp3 -y &".format(i, input_file, overlap, tmp_folder, i))      
    print("overlaping done")                                                                                           
                                                                                                                       
def batch_fingerprint(tmp_folder, step):
    lis = os.listdir(tmp_folder).__len__()
    pmap = []
    times = []
    for i in range(lis):
        song = djv.recognize(FileRecognizer, os.path.join(tmp_folder, "{}.mp3".format(i)))
        if song:
            print(song)
            pmap.append(((i, i + step, song['confidence'], song['song_name'])))
    chunk = []
    c = 10
    for each in fing:
        kk = []
        for beach in pmap:
            if each == beach[3] and beach[2] >= 10:
                kk.append(beach)
        if kk:
            if kk.__len__() != 1:
                l = [x[0] for x in kk]
                res, last = [[]], None
                for x in l:
                    if last is None or abs(last - x) <= 2:
                        res[-1].append(x)
                    else:
                        res.append([x])
                    last = x
                for rr in res:
                    if rr.__len__() != 1:
                        times.append({"start_time": rr[0], "end_time": rr[-1] + step, "song_name": each})
    times = sorted(times, key = lambda i: i['start_time'])
    for i in range(len(times) - 1):
        if times[i + 1]['start_time'] - times[i]['end_time'] > 5:
            times.append({"start_time": times[i]['end_time'] + 1 , "end_time":times[i + 1]['start_time'] - 1, "song_name": "Unidentified"})

    return times

step = 3
song_name = sys.argv[1]
folder_name = sys.argv[2]
break_audio(song_name, folder_name, step)
jsonwa = batch_fingerprint(folder_name, step)
with open("{}.json".format(song_name.split(".mp3")[0]), 'w') as fout:
    json.dump(jsonwa, fout)


