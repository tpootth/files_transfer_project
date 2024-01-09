def convert_to_mp4(input_path, output_file):
    import subprocess   
    try:
        command = [
            'ffmpeg', 
            '-i', input_path, 
            '-c:v', 'h264_nvenc', # libx264 for cput convert  # h264_nvenc for gpu convert
            '-c:a', 'aac', 
            '-strict', 'experimental', 
            output_file
        ]
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path}: {e}")
        return False