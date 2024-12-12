from pydub import AudioSegment
import os

# turn mp4 to mp3
def turn_mp4_to_mp3(mp4_path, mp3_path):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
    
    audio = AudioSegment.from_file(mp4_path, format="mp4")
    audio.export(mp3_path, format="mp3")

turn_mp4_to_mp3("/Users/jinghanz/Documents/Code/Awesome-Orator/sample_video_13.mp4", "files/audio/1.mp3")