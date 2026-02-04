"""Audio utilities: loading, mixing, playback, effects, and the wav context manager."""

import os
from contextlib import contextmanager

import numpy as np
import pygame
from scipy.io import wavfile

from ia2.math import interpolate
from ia2.types import Sequence
from ia2.wave_table import fade_in_out


@contextmanager
def wav(filename="output.wav", sample_rate=44100, length=1, tempo=120, fps=60):
    """Context manager for creating WAV audio file output."""
    data = np.zeros((int(sample_rate * (length + 3))), dtype=np.float32)
    seq = Sequence(data, tempo, sample_rate, fps)
    try:
        yield seq
    finally:
        data /= np.max(np.abs(data), axis=0)
        data = fade_in_out(data)
        wavfile.write(filename, sample_rate, data)


def load_sample(file_name, rate=44100):
    """Load an audio sample from a WAV file."""
    sample_rate, data = wavfile.read(file_name)
    return data


def load_wav_file(filename):
    """Load a WAV file and return float32 mono audio and sample rate.

    Supports int16, int32, uint8, float32, float64.
    Automatically converts stereo to mono.
    Returns (audio_float32_mono, sample_rate) or (None, None) on error.
    """
    try:
        sample_rate, audio = wavfile.read(filename)

        print(f"Loaded: {filename}")
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Data type: {audio.dtype}")
        print(f"  Shape: {audio.shape}")

        if audio.dtype == np.int16:
            audio_float = audio.astype(np.float32) / 32768.0
        elif audio.dtype == np.int32:
            audio_float = audio.astype(np.float32) / 2147483648.0
        elif audio.dtype == np.uint8:
            audio_float = (audio.astype(np.float32) - 128) / 128.0
        elif audio.dtype in (np.float32, np.float64):
            audio_float = audio.astype(np.float32)
            audio_float = np.clip(audio_float, -1.0, 1.0)
        else:
            raise ValueError(f"Unsupported audio data type: {audio.dtype}")

        if len(audio_float.shape) == 2:
            num_channels = audio_float.shape[1]
            print(f"  Channels: {num_channels}")
            audio_mono = np.mean(audio_float, axis=1).astype(np.float32)
        else:
            print(f"  Channels: 1")
            audio_mono = audio_float

        duration = len(audio_mono) / sample_rate
        print(f"  Duration: {duration:.3f} seconds")
        print(f"  Total samples: {len(audio_mono)}")

        return audio_mono, sample_rate

    except Exception as e:
        print(f"Error loading WAV file: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def play_sample(data):
    """Play an audio sample using pygame.

    Automatically handles format conversion to int16 stereo.
    """
    data = np.asarray(data)
    needs_conversion = False

    if data.dtype not in [np.int16]:
        needs_conversion = True
    if len(data.shape) == 1:
        needs_conversion = True
    elif len(data.shape) == 2 and data.shape[1] != 2:
        needs_conversion = True

    if needs_conversion:
        if data.dtype in [np.float32, np.float64]:
            audio_float = data.astype(np.float32)
            audio_float = np.clip(audio_float, -1.0, 1.0)
        elif data.dtype == np.int16:
            audio_float = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            audio_float = data.astype(np.float32) / 2147483648.0
        elif data.dtype == np.uint8:
            audio_float = (data.astype(np.float32) - 128) / 128.0
        else:
            audio_float = data.astype(np.float32)
            max_val = np.max(np.abs(audio_float))
            if max_val > 1.0:
                audio_float = audio_float / max_val

        if len(audio_float.shape) == 2:
            audio_mono = np.mean(audio_float, axis=1).astype(np.float32)
        else:
            audio_mono = audio_float

        audio_int16 = (np.clip(audio_mono, -1.0, 1.0) * 32767).astype(np.int16)
        data = np.column_stack([audio_int16, audio_int16])

    sound = pygame.sndarray.make_sound(data)
    sound.play()


def copy_sample(seq, sample, num_samples, duration):
    """Copy and trim a sample for mixing."""
    num_samples = min(num_samples, int(seq.rate * duration))
    sample_copy = sample[0:num_samples].copy()
    return sample_copy


def write_lead_in(seq, time, sample_copy, num_samples, weight):
    """Write a lead-in ramp to reduce clicks from abrupt amplitude changes."""
    lead_in = min(2000, num_samples // 2)
    weight_i = interpolate(0, weight, lead_in)

    for k in range(lead_in):
        start = int(time * seq.rate)
        seq.wav_file[k + start] = sample_copy[k] * weight_i[k] + seq.wav_file[
            k + start
        ] * (1 - weight_i[k])

    return lead_in


def write_sample(seq, time, sample_copy, num_samples, weight, lead_in):
    """Write a sample into the sequence buffer after the lead-in."""
    start = int(time * seq.rate)
    seq.wav_file[lead_in + start : num_samples + start] = sample_copy[
        lead_in:num_samples
    ] * weight + seq.wav_file[lead_in + start : num_samples + start] * (1 - weight)


def mix_sample(seq, sample, time, weight=0.5, duration=1):
    """Mix an audio sample into a sequence at a specific time."""
    num_samples = sample.shape[0]
    num_samples = min(num_samples, int(seq.rate * duration))
    sample_copy = sample[0:num_samples].copy()
    sample_copy = fade_in_out(sample_copy, fade_length=2000)

    lead_in = min(2000, num_samples // 2)
    weight_i = interpolate(0, weight, lead_in)

    for k in range(lead_in):
        start = int(time * seq.rate)
        seq.wav_file[k + start] = sample_copy[k] * weight_i[k] + seq.wav_file[
            k + start
        ] * (1 - weight_i[k])

    for k in range(lead_in, num_samples):
        start = int(time * seq.rate)
        seq.wav_file[k + start] = sample_copy[k] * weight + seq.wav_file[k + start] * (
            1 - weight
        )


def mix_sample2(seq, sample, weight=0.5, duration=1):
    """Mix an audio sample at the current frame position."""
    num_samples = sample.shape[0]
    time = seq.current_frame / seq.fps

    sample_copy = copy_sample(seq, sample, num_samples, duration)
    sample_copy = fade_in_out(sample_copy, fade_length=2000)

    lead_in = write_lead_in(seq, time, sample_copy, num_samples, weight)
    write_sample(seq, time, sample_copy, num_samples, weight, lead_in)


def on_sixteenths(seq, frame, sample, sixteenths, weight=0.5, duration=1.0):
    """Play a sample on specific sixteenth note beats.

    sixteenths is a list of positions (0-15) within a whole note.
    """
    beat = 60 / seq.tempo
    whole = beat * 4 * seq.fps
    sixteenth = beat / 4 * seq.fps
    intra_note = frame % whole
    d, r = divmod(intra_note, sixteenth)
    if r < 1.0 and d in sixteenths:
        mix_sample2(seq, sample, weight=weight, duration=duration)


def reverb(seq, delay=0.05, decay=0.5):
    """Apply a simple reverb effect to the audio sequence."""
    delay = int(seq.rate * delay)
    decay = 0.2
    for i in range(seq.wav_file.shape[0] - delay):
        seq.wav_file[i + delay] = seq.wav_file[i + delay] + seq.wav_file[i] * decay


def combine(video_output, wav_output, combined_output):
    """Combine video and audio files using ffmpeg."""
    command = (
        f"ffmpeg -y -i {video_output} "
        f" -i {wav_output} "
        " -c:v copy "
        "-c:a aac "
        "-shortest "
        f" {combined_output}"
    )
    os.system(command)
