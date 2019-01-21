
import argparse
import datetime
import re
import subprocess 
from time import sleep
import os
import sys
from os import listdir
from os.path import isfile, join ,splitext , basename

# 视频尾部的垃圾广告时长 需要用户自己手动设置
g_adv_length = 0.0
  
def cut_VideoAds(file_name,new_name,start_at,how_Long,debug_infor='./d.txt'): 
    process = subprocess.Popen(
        ["ffmpeg", "-ss", start_at, "-t", how_Long, "-i", file_name, "-vcodec", "copy", "-acodec", "copy", new_name], 
        stderr = subprocess.PIPE,
        close_fds = True
    ) 
    output = ""
    iterations = 0
    # ensure the output contains "Duration"
    while(not "start" in output and iterations < 100):
        buffer_read = str(process.stderr.read())
        iterations += 1
        if(buffer_read != "None"):
            output += buffer_read
        #print(iterations)
        sleep(.01)

    with open(debug_infor,"a+") as fn:
        fn.write(output[1:])
        fn.close()
        
    return output

def get_VideoDurationsByName(file_name):
    regex = r"Duration:.+(\d\d:\d\d:\d\d\.\d\d)"
    process = subprocess.Popen(
        ["ffmpeg", "-i", file_name], 
        stderr = subprocess.PIPE,
        close_fds = True
    ) 
    output = ""
    iterations = 0
    # ensure the output contains "Duration"
    while(not "start" in output and iterations < 100):
        buffer_read = str(process.stderr.read())
        iterations += 1
        if(buffer_read != "None"):
            output += buffer_read
        #print(iterations)
        sleep(.01)

    target = output[1:]
    match = re.search(regex, target)
    if match:
        duration = match.group(1)              
    else:
        duration = "00:00:00"
        
    return duration

def get_videofiles(rootdir):
    vfs = []
    for fpathe,dirs,fs in os.walk(rootdir):
      for f in fs:
        if os.path.splitext(f)[1]=='.mp4':
            vfs.append (os.path.join(fpathe,f))
    return vfs

def get_durationfromstring(target):
    durations = []
    fle = len("Duration: 00:06:37.20") 
    fi = 0
    fnext =target.find("Duration",fi)
    while ( fnext  > 0 ):
        if(fnext>0):
            durations.append(target[fnext:fnext+fle])
            fi =  fnext+fle + 1
            fnext =target.find("Duration",fi)
            
def calculate_total(durations):
    total = datetime.timedelta()
    for duration in durations:
        time = datetime.datetime.strptime(duration, "%H:%M:%S.%f")
        time_delta = datetime.timedelta(
            hours = time.hour,
            minutes = time.minute,
            seconds = time.second,
            microseconds = time.microsecond
        )
        total += time_delta
    return total

def get_seconds(duration):
    tar = duration.split(":")
    hours = float(tar[0])
    mins = float(tar[1])
    seconds = float(tar[2])
    return float(hours*3600 + mins * 60 + seconds )
 
def format_TimeStyles(total_seconds):
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tstyle = "{:.0f}:{:.0f}:{:.2f}".format( hours, minutes, seconds)
    print(tstyle)
    return tstyle
                            
def main():
    global g_adv_length
    save_result = "./d.txt"
    regex = r"Duration:.+(\d\d:\d\d:\d\d\.\d\d)"
    g_adv_length =  float(input("In vidoe at tails ,the adverisement duration times Long(ep. 5 seconds input 5 and Enter):"))
    curdir = input("Need to cut video directory : ")
    if  os.path.exists(save_result):
        os.unlink(save_result)
    videofiles = get_videofiles(curdir)
    for file_name in videofiles:
        basename = os.path.basename(file_name)
        videosize = os.path.getsize(file_name)
        ext_name = os.path.splitext(file_name)[1]
        file_path = os.path.dirname(file_name)
        new_name = "%s/%s_%s"%(file_path,basename.split(".")[0],ext_name)
        duration = get_VideoDurationsByName(file_name)        
        start_at = "00:00:00"
        total_seconds = get_seconds(duration)
        how_Long = format_TimeStyles( total_seconds - g_adv_length)
##        print("duration=%s\nhow_Long=%s"%(duration,how_Long))
##        print("file_name=%s file_path=%s\nbasename=%s\nnew_name=%s"%(file_name,file_path,basename,new_name))
        output = cut_VideoAds(file_name,new_name,start_at,how_Long,save_result)


if __name__ == "__main__":
    main()







 
