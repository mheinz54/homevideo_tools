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
    fs = pathlib.Path(file)
    mtime = datetime.datetime.fromtimestamp(fs.stat().st_mtime)
    dur = get_duration(file)

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
            "-loglevel", "info" if tsettings.show_log else "error",
            "-i", file,
            "-vf", "subtitles=" + subargs + "[sub];[sub]yadif=1",
            "-crf", "18",
            "-c:v", "libx264",
            "-y",
            out_file]
    subprocess.call(args)

    if tsettings.delete_after_imprint:
        os.remove(subname)

def crossfade_multiple(lst_files, out_folder, tsettings, out_filename = "crossfaded.mp4"):
    """ crossfade multiple videos
        example below:

        ffmpeg -i v0.mp4 -i v1.mp4 -i v2.mp4 -i v3.mp4 -i v4.mp4 -filter_complex \
        "[0][1]xfade=transition=fade:duration=0.5:offset=3.5[V01]; \
        [V01][2]xfade=transition=fade:duration=0.5:offset=12.1[V02]; \
        [V02][3]xfade=transition=fade:duration=0.5:offset=15.1[V03]; \
        [V03][4]xfade=transition=fade:duration=0.5:offset=22.59,format=yuv420p[video]; \
        [0:a][1:a]acrossfade=d=0.5:c1=tri:c2=tri[A01]; \
        [A01][2:a]acrossfade=d=0.5:c1=tri:c2=tri[A02]; \
        [A02][3:a]acrossfade=d=0.5:c1=tri:c2=tri[A03]; \
        [A03][4:a]acrossfade=d=0.5:c1=tri:c2=tri[audio]" \
        -map "[video]" -map "[audio]" -movflags +faststart out.mp4
        ___________________________________________________________________________________
        | input  | input duration | + | previous xfade offset | - | xfade duration | =     |
        | v0.mp4 | 4.00           | + | 0                     | - | 0.5            | 3.5   |
        | v1.mp4 | 9.19           | + | 3.5                   | - | 0.5            | 12.1  |
        | v2.mp4 | 3.41           | + | 12.1                  | - | 0.5            | 15.1  |
        | v3.mp4 | 7.99           | + | 15.1                  | - | 0.5            | 22.59 |
    """
    if not os.path.exists(out_folder):
        raise ValueError(out_folder + " folder does not exist")
    for f in lst_files:
        if not os.path.exists(f):
            raise ValueError(f + " does not exist")
    total = len(lst_files)
    if total <= 1:
        raise ValueError("need more than 1 video to crossfade")

    input_arg = ""
    filter_v = ""
    filter_a = ""
    prev_vfeed = "[0:v]"
    prev_afeed = "[0:a]"
    prev_offset = 0
    xfade_dur = 1.0
    for i, f in enumerate(lst_files):
        input_arg += " -i " + f

        if i < total - 1:
            curr_vfeed = "[V0{}]".format(i + 1)
            dur = get_duration(f)
            offset = dur + prev_offset - xfade_dur
            filter_v += "{}[{}]xfade=transition=fade:duration={}:offset={}{};".format(
                prev_vfeed, # input feed
                i + 1,      # source index
                xfade_dur,  # duraction of fade
                offset,     # offset for video feed
                curr_vfeed  # output feed
            )
            prev_vfeed = curr_vfeed
            prev_offset = offset

            curr_afeed = "[A0{}]".format(i + 1)
            filter_a += "{}[{}:a]acrossfade=d={}:c1=tri:c2=tri{};".format(
                prev_afeed, # input audio feed
                i + 1,      # source audio index
                xfade_dur,  # duraction of fade
                curr_afeed  # output audio feed
            )
            prev_afeed = curr_afeed
        else:
            filter_v += "{}yadif=1[video];".format(prev_vfeed)
            prev_vfeed = "[video]"

    filter_arg = filter_v + filter_a[:-1]
    map_arg = "-map {} -map {}".format(prev_vfeed, prev_afeed)
    out_file = os.path.join(out_folder, out_filename)

    args = [FFMPEG,
            "-hide_banner",
            "-loglevel", "info" if tsettings.show_log else "error"
    ]
    args += input_arg.strip().split(" ")
    args += ["-filter_complex", filter_arg]
    args += map_arg.split(" ")
    args += ["-c:v", "libx264",
            "-crf", "18",
            "-y",
            out_file]
    subprocess.call(args)


# def crossfade_two(f1, f2):
#     if not (os.path.exists(f1) or \
#             os.path.exists(f2)):
#         print("video does not exist")
#         return

#     d1 = get_duration(f1)
#     #cfilter = "xfade=offset=" + str(d1 - 1) + ":duration=1[v];[v]yadif=1;" + \
#     cfilter = "xfade=offset=" + str(d1 - 1) + ":duration=1;" + \
#               "acrossfade=d=1:c1=tri:c2=tri"

#     args = [FFMPEG,
#             "-hide_banner",
#             "-loglevel", "error",
#             "-i", f1,
#             "-i", f2,
#             "-filter_complex", cfilter,
#             "-c:v", "libx264",
#             "-crf", "18",
#             "-y",
#             "out/fadeout.mp4"]
#     subprocess.call(args)

def main(tsettings):
    if tsettings.in_test:
        f = 'samples/M2U00059.MPG'
        f1 = 'samples/M2U00059.MPG'
        f2 = 'samples/M2U00006.MPG'
        #create_subtitles(f, tsettings)
        #write_subtitle_to_video(f, 'out', tsettings)
        crossfade_multiple([f, f1], 'out', tsettings)
    # else:
    #     for f in Path(sys.argv[1]).glob("*.MPG"):
    #         create_subtitles(f, tsettings)
    #         write_subtitle_to_video(f, tsettings)

if __name__ == "__main__":
    tsettings = tool_settings.ToolSettings()
    main(tsettings)