import soundfile as sf
import soundcard as sc
import os

def play_audio(file_path):
    """Play audio file using soundfile."""
    default_device = sc.default_speaker()
    try:
        data, samplerate = sf.read(file_path)
        default_device.play(data, samplerate)
    except Exception as e:
        print(f"Error playing {file_path}: {e}")


if __name__ == "__main__":
    # # Example usage
    # cwd = os.getcwd()
    # sample_folder = os.path.join(cwd, 'Samples')
    # sample_file = os.path.join(sample_folder, 'example.wav')  # Replace with your actual file

    sample_file = '/Users/jonasbrumund/AP/Samples/musicradar_copy1/00s_Synths/Arps/90bpm/00s_Arp[90]-D.wav'

    if os.path.exists(sample_file):
        print(f"Playing audio file: {sample_file}")
        play_audio(sample_file)
    else:
        print(f"Audio file does not exist: {sample_file}")