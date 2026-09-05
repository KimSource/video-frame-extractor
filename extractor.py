import os
import re


def parse_specific_frames(value):
    value = value.strip()
    if not value:
        raise ValueError('Specific frames are required.')

    frames = re.split(r'[\s,]+', value)
    if any(not frame.isdigit() for frame in frames):
        raise ValueError('Specific frames must be non-negative integers.')

    return frames


def validate_inputs(
    input_file,
    output_directory,
    method,
    frame_interval,
    specific_frames,
    ffmpeg_file,
):
    errors = []

    if not input_file.strip():
        errors.append('Input file is required.')
    elif not os.path.isfile(input_file):
        errors.append('Input file does not exist.')

    if not output_directory.strip():
        errors.append('Output directory is required.')
    elif not os.path.isdir(output_directory):
        errors.append('Output directory does not exist.')

    if method == 0:
        if not frame_interval.strip().isdigit() or int(frame_interval) < 1:
            errors.append('The frame interval must be a positive integer.')
    else:
        try:
            parse_specific_frames(specific_frames)
        except ValueError as error:
            errors.append(str(error))

    if not ffmpeg_file:
        errors.append('Unable to find FFmpeg.')

    return errors


def build_select_filter(method, frame_interval, specific_frames):
    if method == 0:
        select = r'not(mod(n\,{n}))'.format(n=frame_interval.strip())
    elif method == 1:
        frames = parse_specific_frames(specific_frames)
        select = '+'.join(f'eq(n,{frame})' for frame in frames)
    else:
        frames = parse_specific_frames(specific_frames)
        select = '+'.join(f'eq(pts,{frame})' for frame in frames)

    return f'select={select}'


def build_command_args(
    ffmpeg_file,
    input_file,
    output_directory,
    output_file_type,
    jpg_quality,
    webp_quality,
    lossless,
    method,
    frame_interval,
    specific_frames,
):
    options = []
    if output_file_type == '.jpg':
        options.extend(['-qscale:v', str(int(jpg_quality))])
    elif output_file_type == '.webp':
        options.extend([
            '-qscale:v',
            str(int(webp_quality)),
            '-lossless',
            '1' if lossless else '0',
        ])

    return [
        ffmpeg_file,
        '-i',
        input_file,
        '-vf',
        build_select_filter(method, frame_interval, specific_frames),
        '-fps_mode',
        'passthrough',
        '-frame_pts',
        '1',
        *options,
        output_directory.rstrip('/\\') + '/%d' + output_file_type,
    ]
