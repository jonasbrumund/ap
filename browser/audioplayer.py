# audio_player.py
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
        while self.playing:
            with self.default_speaker.player(samplerate=self.samplerate) as player:
                player.play(self.audio_data)
            if not self.loop:
                break

    def play(self):
        if self.audio_data is None:
            return
        self.playing = True
        self.play_thread = threading.Thread(target=self._play_audio, daemon=True)
        self.play_thread.start()

    def stop(self):
        self.playing = False

    def set_loop(self, loop):
        self.loop = loop
