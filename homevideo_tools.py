import sys, os
import pathlib
import datetime
from datetime import timedelta
import subprocess
from pathlib import Path

FFMPEG = "tools/ffmpeg.exe"
FFPROBE = "tools/ffprobe.exe"

def get_duration(fname):
    args = [FFPROBE,
            "-loglevel", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            fname]
    duration = int(float(subprocess.check_output(args)))
    return duration

def format_timecode(s):
    t = datetime.datetime(1,1,1) + timedelta(seconds=s)
    return t.strftime("%H:%M:%S.000")

def format_datecode(mtime, t, with_seconds=False):
    new_time = mtime + timedelta(seconds=t)
    if with_seconds:
        return new_time.strftime("%I:%M:%S %p\n%b %d %Y")
    else:
        return new_time.strftime("%I:%M %p\n%b %d %Y")

def create_subtitles(file):
    print(file)
    fs = pathlib.Path(file)
    mtime = datetime.datetime.fromtimestamp(fs.stat().st_mtime)
    dur = get_duration(file)
    print(dur)
    
    with open(str(file) + ".srt", 'w') as f:
        for i in range(0, dur):
            f.write("{}\n{} --> {}\n{}\n\n".format(
                i+1,
                format_timecode(i),
                format_timecode(i + 1),
                format_datecode(mtime,i)
            ))

def write_subtitle_to_video(file):
    subname = str(file) + ".srt"
    if not (os.path.exists(file) or \
            os.path.exists(subname)):
        print("video or subtitle does not exist")
        return

    """ Alignment values 
        1 = bottom left, 2 = bottom center, 3 = bottom right 
        color values
        ABGR where alpha FF is full transparent
    """
    subargs = subname + ":force_style='Alignment=1," + \
                                      "FontSize=12," + \
                                      "PrimaryColour=&H55FFFFFF," + \
                                      "OutlineColour=&H55000000'"

    args = [FFMPEG,
            "-hide_banner",
            "-loglevel", "error",
            "-i", file,
            "-vf", "subtitles=" + subargs + "[sub];[sub]yadif=1",
            "-crf", "18",
            "-c:v", "libx264",
            "-y",
            "out/output_size.mp4"]
    subprocess.call(args)

def crossfade_two(f1, f2):
    if not (os.path.exists(f1) or \
            os.path.exists(f2)):
        print("video does not exist")
        return

    d1 = get_duration(f1)
    #cfilter = "xfade=offset=" + str(d1 - 1) + ":duration=1[v];[v]yadif=1;" + \
    cfilter = "xfade=offset=" + str(d1 - 1) + ":duration=1;" + \
              "acrossfade=d=1:c1=tri:c2=tri"

    args = [FFMPEG,
            "-hide_banner",
            "-loglevel", "error",
            "-i", f1,
            "-i", f2,
            "-filter_complex", cfilter,
            "-c:v", "libx264",
            "-crf", "18",
            "-y",
            "out/fadeout.mp4"]
    subprocess.call(args)
            

if len(sys.argv) > 1:
    for f in Path(sys.argv[1]).glob("*.MPG"):
        create_subtitles(f)
        write_subtitle_to_video(f)
else:
    f = 'samples/M2U00059.MPG'
    f1 = 'samples/M2U00059.MPG'
    f2 = 'samples/M2U00006.MPG'
    create_subtitles(f)
    write_subtitle_to_video(f)
    #crossfade_two(f1, f2)
    
