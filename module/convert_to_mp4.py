import os
import subprocess

# libx264 = CPU encode, h264_nvenc = NVIDIA GPU encode
DEFAULT_VIDEO_CODEC = 'h264_nvenc'


def convert_to_mp4(input_path, output_file, video_codec=DEFAULT_VIDEO_CODEC):
    """Convert ``input_path`` to MP4 with ffmpeg. Returns True on success.

    ffmpeg writes to a temporary ``.part.mp4`` file that is renamed only when the
    conversion finishes, so ``output_file`` never holds a half-converted video.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    part_file = os.path.splitext(output_file)[0] + '.part.mp4'
    command = [
        'ffmpeg',
        '-hide_banner',
        '-y',  # only overwrites our own leftover .part file, never waits for a prompt
        '-i', input_path,
        '-c:v', video_codec,
        '-c:a', 'aac',
        part_file,
    ]
    try:
        subprocess.run(command, check=True, stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Install ffmpeg and make sure it is on PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path}: {e}")
        if os.path.exists(part_file):
            os.remove(part_file)
        return False

    os.replace(part_file, output_file)
    return True
