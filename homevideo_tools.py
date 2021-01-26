#!/usr/bin/env python
""" tools to modify homevideos such as:
        create and imprint timestamp subtitles
        combine several videos with a crossfade transition 
"""

import sys, os
import pathlib
from pathlib import Path
import datetime
from datetime import timedelta
import subprocess
import tool_settings

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

def format_datecode(mtime, t, with_seconds, use_24hour_format):
    new_time = mtime + timedelta(seconds=t)
    hour = "H" if use_24hour_format else "I"
    m = "" if use_24hour_format else "%p"
    if with_seconds:
        return new_time.strftime("%{}:%M:%S {}\n%b %d %Y".format(hour, m))
    else:
        return new_time.strftime("%{}:%M {}\n%b %d %Y".format(hour, m))

def create_subtitles(file, tsettings):
    #print(file)
    fs = pathlib.Path(file)
    mtime = datetime.datetime.fromtimestamp(fs.stat().st_mtime)
    dur = get_duration(file)
    #print(dur)

    with open(str(file) + ".srt", 'w') as f:
        for i in range(0, dur):
            f.write("{}\n{} --> {}\n{}\n\n".format(
                i+1,
                format_timecode(i),
                format_timecode(i + 1),
                format_datecode(mtime, i, tsettings.include_seconds, tsettings.use_24hour_format)
            ))

def write_subtitle_to_video(file, out_folder, tsettings):
    subname = "{}.srt".format(str(file))
    if not (os.path.exists(file) or \
            os.path.exists(subname)):
        print("video or subtitle does not exist")
        return

    subargs = "{}:force_style='Alignment={},FontName={},FontSize={},PrimaryColour=&H{},OutlineColour=&H{}'".format(
        subname.replace(":", "\\\\:"),
        tsettings.alignment,
        tsettings.font,
        tsettings.font_size,
        tsettings.primary_color,
        tsettings.outline_color
    )

    out_file = os.path.join(out_folder, os.path.basename(file))

    args = [FFMPEG,
            "-hide_banner",
            "-loglevel", "error",
            "-i", file,
            "-vf", "subtitles=" + subargs + "[sub];[sub]yadif=1",
            "-crf", "18",
            "-c:v", "libx264",
            "-y",
            out_file]
    subprocess.call(args)

    if tsettings.delete_after_imprint:
        os.remove(subname)

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

def main(tsettings):
    if tsettings.in_test:
        f = 'samples/M2U00059.MPG'
        f1 = 'samples/M2U00059.MPG'
        f2 = 'samples/M2U00006.MPG'
        create_subtitles(f, tsettings)
        write_subtitle_to_video(f, 'out', tsettings)
        #crossfade_two(f1, f2)
    # else:
    #     for f in Path(sys.argv[1]).glob("*.MPG"):
    #         create_subtitles(f, tsettings)
    #         write_subtitle_to_video(f, tsettings)

if __name__ == "__main__":
    tsettings = tool_settings.ToolSettings()
    main(tsettings)