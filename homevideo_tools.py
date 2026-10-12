#!/usr/bin/env python
""" tools to modify homevideos such as:
        create and imprint timestamp subtitles
        combine several videos with a crossfade transition 
"""

import sys, os
from functools import lru_cache
import platform
import shutil
import pathlib
from pathlib import Path
import datetime
import json
from datetime import timedelta
import subprocess
import tool_settings

TOOLS_DIR = Path(__file__).resolve().parent / "tools"

def _find_media_tool(name):
    if sys.platform == "darwin":
        architecture = platform.machine().lower()
        candidates = [
            TOOLS_DIR / "macos" / architecture / name,
            TOOLS_DIR / "macos" / "universal" / name,
            TOOLS_DIR / name,
            Path("/opt/homebrew/bin") / name,
            Path("/usr/local/bin") / name,
        ]
    elif os.name == "nt":
        candidates = [
            TOOLS_DIR / (name + ".exe"),
            TOOLS_DIR / "windows" / (name + ".exe"),
        ]
    else:
        candidates = []

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return shutil.which(name) or name

FFMPEG = _find_media_tool("ffmpeg")
FFPROBE = _find_media_tool("ffprobe")

@lru_cache(maxsize=1)
def _video_encoder_args():
    if sys.platform == "darwin":
        try:
            encoders = subprocess.check_output(
                [FFMPEG, "-hide_banner", "-encoders"],
                stderr=subprocess.STDOUT,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError):
            encoders = ""

        if any(
            len(fields) > 1 and fields[1] == "h264_videotoolbox"
            for fields in (line.split() for line in encoders.splitlines())
        ):
            return ("-r", "60", "-c:v", "h264_videotoolbox", "-b:v", "8M")

    return ("-r", "60", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast")

def print_durations(fname):
    """ shows durations of audio and video stream for a video"""
    args = [FFPROBE,
            "-loglevel", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            fname]
    dv = float(subprocess.check_output(args))

    args = [FFPROBE,
            "-loglevel", "error",
            "-select_streams", "a:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            fname]
    av = float(subprocess.check_output(args))
    print("video: {}\naudio: {}\n".format(dv, av))

def get_duration(fname):
    args = [FFPROBE,
            "-loglevel", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            fname]
    duration = float(subprocess.check_output(args))
    return duration

def needs_deinterlacing(fname):
    args = [FFPROBE,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=field_order",
            "-of", "json",
            str(fname)]
    try:
        probe_result = subprocess.check_output(
            args,
            stderr=subprocess.STDOUT,
            text=True,
        )
        streams = json.loads(probe_result).get("streams", [])
    except (OSError, subprocess.CalledProcessError):
        return False
    except json.JSONDecodeError:
        return False
    if not streams:
        return False
    field_order = streams[0].get("field_order", "unknown").lower()
    return field_order in {"tt", "bb", "tb", "bt"}

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
    if tsettings.camcorder_yadif_filter:
        mtime = datetime.datetime.fromtimestamp(fs.stat().st_mtime) # for camcorder
    else:
        mtime = datetime.datetime.fromtimestamp(fs.stat().st_ctime) # for phone
    dur = int(get_duration(file))

    with open(str(file) + ".srt", 'w') as f:
        for i in range(0, dur):
            f.write("{}\n{} --> {}\n{}\n\n".format(
                i+1,
                format_timecode(i),
                format_timecode(i + 1),
                format_datecode(mtime, i, tsettings.include_seconds, tsettings.use_24hour_format)
            ))

def _escape_filter_value(value):
    return (str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace("[", "\\[")
            .replace("]", "\\]"))

def write_subtitle_to_video(file, out_folder, tsettings):
    subname = "{}.srt".format(str(file))
    if not (os.path.exists(file) or \
            os.path.exists(subname)):
        print("video or subtitle does not exist")
        return

    force_style = "Alignment={},FontName={},FontSize={},PrimaryColour=&H{},OutlineColour=&H{}".format(
        tsettings.alignment,
        tsettings.font,
        tsettings.font_size,
        tsettings.primary_color,
        tsettings.outline_color
    )
    video_filter = "subtitles=filename='{}':force_style='{}'".format(
        _escape_filter_value(subname),
        _escape_filter_value(force_style)
    )
    if needs_deinterlacing(file):
        video_filter += ",yadif=1"

    op = os.path
    out_file = op.join(out_folder, op.splitext(op.basename(file))[0]) + ".mp4"

    args = [FFMPEG,
            "-hide_banner",
            "-loglevel", "info" if tsettings.show_log else "error",
            "-i", file,
          #   "-vsync", "0",
                        "-vf", video_filter]
    args += list(_video_encoder_args())
    args += ["-pix_fmt", "yuv420p",
            #"-shortest",
            "-y",
            out_file]
    # print(args)
    subprocess.call(args)

    if tsettings.delete_after_imprint:
        os.remove(subname)

def crossfade_multiple(lst_files, out_folder, tsettings, out_filename = "crossfaded.mp4"):
    """ crossfade multiple videos
        example below:

        ffmpeg -i v0.mp4 -i v1.mp4 -i v2.mp4 -i v3.mp4 -i v4.mp4 -filter_complex \
        "[0][1]xfade=transition=fade:duration=0.5:offset=3.500000[V01]; \
        [V01][2]xfade=transition=fade:duration=0.5:offset=6.366667[V02]; \
        [V02][3]xfade=transition=fade:duration=0.5:offset=13.800000[V03]; \
        [V03][4]xfade=transition=fade:duration=0.5:offset=20.433333,format=yuv420p[video]; \
        [0:a]aresample=async=1:first_pts=0,apad,atrim=0:4[AR0]; \
        [1:a]aresample=async=1:first_pts=0,apad,atrim=0:3.366667[AR1]; \
        [2:a]aresample=async=1:first_pts=0,apad,atrim=0:7.933333[AR2]; \
        [3:a]aresample=async=1:first_pts=0,apad,atrim=0:7.133333[AR3]; \
        [4:a]aresample=async=1:first_pts=0,apad,atrim=0:6.566667[AR4]; \
        [AR0][AR1]acrossfade=d=0.5:c1=tri:c2=tri[AF1]; \
        [AF1][AR2]acrossfade=d=0.5:c1=tri:c2=tri[AF2]; \
        [AF2][AR3]acrossfade=d=0.5:c1=tri:c2=tri[AF3]; \
        [AF3][AR4]acrossfade=d=0.5:c1=tri:c2=tri[audio]" \
        -map "[video]" -map "[audio]" -movflags +faststart out.mp4
        ___________________________________________________________________________________
        | input  | input duration | + | previous xfade offset | - | xfade duration | =     |
        | v0.mp4 | 4.00           | + | 0                     | - | 0.5            | 3.5   |
        | v1.mp4 | 3.367          | + | 3.5                   | - | 0.5            | 6.367 |
        | v2.mp4 | 7.93           | + | 6.367                 | - | 0.5            | 13.8  |
        | v3.mp4 | 7.133          | + | 13.8                  | - | 0.5            | 20.43 |
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
    filter_afade = ""
    filter_asample = ""
    prev_vfeed = "[0:v]"
    prev_afeed = "[AR0]"
    prev_offset = 0.0
    xfade_dur = 1.0
    deinterlace = needs_deinterlacing(lst_files[0])

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

            filter_asample += "[{}:a]aresample=async=1:first_pts=0,apad,atrim=0:{}[AR{}];".format(
                i,      # input feed index
                dur,    # duration of feed
                i       # ouput feed index
            )

            curr_afeed = "[AF{}]".format(i + 1)
            filter_afade += "{}[AR{}]acrossfade=d={}:c1=tri:c2=tri{};".format(
                prev_afeed, # input audio feed
                i + 1,      # source audio index
                xfade_dur,  # duraction of fade
                curr_afeed  # output audio feed
            )
            prev_afeed = curr_afeed
        else:
            dur = get_duration(f)

            if deinterlace:
                filter_v += "{}yadif=1[video];".format(prev_vfeed) # not sure about yadif, maybe needed for camcorder
                prev_vfeed = "[video]"

            filter_asample += "[{}:a]aresample=async=1:first_pts=0,apad,atrim=0:{}[AR{}];".format(
                i,      # input feed index
                dur,    # duration of feed
                i       # ouput feed index
            )

    filter_arg = filter_v + filter_asample + filter_afade[:-1]
    map_arg = ["-map", prev_vfeed, "-map", prev_afeed]
    out_file = os.path.join(out_folder, out_filename)

    # build arguments 
    args = [FFMPEG,
            "-hide_banner",
            "-loglevel", "info" if tsettings.show_log else "error"
    ]
    args += input_arg.strip().split(" ")
    args += ["-filter_complex", filter_arg]
    args += map_arg
    args += list(_video_encoder_args())
    args += ["-pix_fmt", "yuv420p", "-y", out_file]
    subprocess.call(args)
    print(filter_arg)


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
        f1 = 'samples/org.MPG'
        # print_metadata(f1)
        # f2 = 'samples/M2U00006.MPG'
        # f1_out = 'out/M2U00059.mp4'
        # f2_out = 'out/M2U00006.mp4'
        # fc = 'out/crossfaded.mp4'
        # create_subtitles(f1, tsettings)
        # write_subtitle_to_video(f1, 'out', tsettings)
        # crossfade_multiple([f3, f3], 'out', tsettings)
        print_durations(f1)
        # print_durations(f1_out)
        # for v in Path("E:\\Videos\\Naomi\\2020\\20201030-31_halloween").glob("*.mp4"):
        #     print_durations(v)
    # else:
    #     for f in Path(sys.argv[1]).glob("*.MPG"):
    #         create_subtitles(f, tsettings)
    #         write_subtitle_to_video(f, tsettings)

if __name__ == "__main__":
    tsettings = tool_settings.ToolSettings()
    main(tsettings)