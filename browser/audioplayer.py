import soundfile as sf
import soundcard as sc
import threading
import numpy as np


class AudioPlayer:
    def __init__(self):
        self.default_speaker = sc.default_speaker()
        self.play_thread = None
        self.playing = False
        self.loop = False
        self.audio_data = None
        self.samplerate = None

    def load_audio(self, file_path, start=0.0, end=None):
        data, samplerate = sf.read(file_path, dtype='float32')
        if end:
            end_idx = int(end * samplerate)
        else:
            end_idx = len(data)
        start_idx = int(start * samplerate)
        self.audio_data = data[start_idx:end_idx]
        self.samplerate = samplerate

    def _play_audio(self):
        chunk_size = 1024  # frames per chunk

        while self.playing:
            with self.default_speaker.player(
                    samplerate=self.samplerate) as player:

                frames = self.audio_data
                idx = 0
                while idx < len(frames) and self.playing:
                    end_idx = min(idx + chunk_size, len(frames))
                    chunk = frames[idx:end_idx]

                    # Ensure chunk shape: (frames, channels)
                    if chunk.ndim == 1:
                        chunk = np.expand_dims(chunk, axis=-1)

                    player.play(chunk)
                    idx += chunk_size

                if not self.loop:
                    break

        self.playing = False  # Playback done

    def play(self):
        if self.audio_data is None:
            return

        self.stop()  # Stop previous playback

        self.playing = True
        self.play_thread = threading.Thread(
            target=self._play_audio, daemon=True)
        self.play_thread.start()

    def stop(self):
        self.playing = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join()
        self.play_thread = None

    def set_loop(self, loop):
        self.loop = loop
