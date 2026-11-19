"""
Procedural Sound Effects (SFX) Studio — Tube Trek
Generates broadcast-quality micro-SFX (whoosh, pop, sub-drop) entirely in-memory
using NumPy and standard library wave. Zero external audio downloads required.
"""
import os
import wave
import numpy as np


def generate_whoosh(out_path: str, duration: float = 0.32, sr: int = 44100) -> str:
    """Generate a clean swept bandpass white-noise whoosh for scene cuts."""
    if os.path.exists(out_path):
        return out_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    # Bandpass swept noise
    noise = np.random.uniform(-1.0, 1.0, len(t))
    # Frequency modulation 250Hz -> 1800Hz -> 200Hz
    sweep = np.sin(2 * np.pi * (250 + 1550 * np.sin(np.pi * t / duration)) * t)
    # Smooth Hann volume envelope
    env = (np.sin(np.pi * t / duration) ** 2).astype(np.float32)
    audio = np.clip(noise * sweep * env * 0.42, -1.0, 1.0)

    with wave.open(out_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    return out_path


def generate_pop(out_path: str, duration: float = 0.08, sr: int = 44100) -> str:
    """Generate a crisp kinetic text reveal pop (damped frequency chirp)."""
    if os.path.exists(out_path):
        return out_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    # Exponential frequency chirp 850Hz -> 220Hz
    freq = 850 * np.exp(-t * 28) + 220
    phase = 2 * np.pi * np.cumsum(freq) / sr
    env = np.exp(-t * 55).astype(np.float32)
    audio = np.clip(np.sin(phase) * env * 0.45, -1.0, 1.0)

    with wave.open(out_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    return out_path


def generate_sub_drop(out_path: str, duration: float = 1.2, sr: int = 44100) -> str:
    """Generate a cinematic sub-bass impact drop (75Hz -> 32Hz) for the 0.0s hook."""
    if os.path.exists(out_path):
        return out_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    freq = 75 * np.exp(-t * 1.6) + 32
    phase = 2 * np.pi * np.cumsum(freq) / sr
    env = (np.exp(-t * 2.2) * (1 - np.exp(-t * 40))).astype(np.float32)
    audio = np.clip(np.sin(phase) * env * 0.58, -1.0, 1.0)

    with wave.open(out_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    return out_path


def generate_mechanical_click(out_path: str, duration: float = 0.04, sr: int = 44100) -> str:
    """Generate a subtle tactile mechanical camera/switch click for seamless cuts (replaces loud whooshes)."""
    if os.path.exists(out_path):
        return out_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    freq = 1400 * np.exp(-t * 90) + 350
    phase = 2 * np.pi * np.cumsum(freq) / sr
    env = np.exp(-t * 120).astype(np.float32)
    # Layer with high-pass impulse
    noise = np.random.uniform(-0.3, 0.3, len(t)) * np.exp(-t * 180)
    audio = np.clip((np.sin(phase) * 0.7 + noise) * env * 0.28, -1.0, 1.0)

    with wave.open(out_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    return out_path


def generate_cinematic_braam(out_path: str, duration: float = 1.3, sr: int = 44100) -> str:
    """Generate a low-frequency cinematic brass/sub braam (55Hz->38Hz with saturation) for the opening hook."""
    if os.path.exists(out_path):
        return out_path
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    f0 = 55 * np.exp(-t * 0.8) + 38
    phase = 2 * np.pi * np.cumsum(f0) / sr
    # Fundamental + 2nd/3rd harmonics with mild drive
    tone = np.sin(phase) + 0.45 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    # Distortion saturation
    saturated = np.tanh(tone * 1.8)
    env = (np.exp(-t * 1.8) * (1 - np.exp(-t * 60))).astype(np.float32)
    audio = np.clip(saturated * env * 0.48, -1.0, 1.0)

    with wave.open(out_path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    return out_path


def build_sfx_tracks(job_dir: str, cut_timestamps: list = None,
                     include_hook_drop: bool = True) -> list:
    """
    Build a list of MoviePy AudioClip instances placed at their respective timestamps.
    Original classic setup: hook sub-drop + crisp transition whooshes on cuts.
    """
    from moviepy.editor import AudioFileClip

    sfx_dir = os.path.join(job_dir, "sfx")
    os.makedirs(sfx_dir, exist_ok=True)

    clips = []

    # 1. 0.0s Tension Hook Sub-Drop
    if include_hook_drop:
        sub_path = os.path.join(sfx_dir, "hook_sub_drop.wav")
        generate_sub_drop(sub_path)
        try:
            sub_clip = AudioFileClip(sub_path).volumex(0.35).set_start(0.0)
            clips.append(sub_clip)
        except Exception as e:
            print(f"   ⚠ Could not load sub-drop SFX: {e}")

    # 2. Transition Whoosh at each visual cut
    whoosh_path = os.path.join(sfx_dir, "transition_whoosh.wav")
    generate_whoosh(whoosh_path)
    for ts in (cut_timestamps or []):
        if ts > 0.4:  # Avoid clashing with the initial hook drop
            try:
                start_t = max(0.0, ts - 0.12)
                w_clip = AudioFileClip(whoosh_path).volumex(0.22).set_start(start_t)
                clips.append(w_clip)
            except Exception:
                pass

    return clips
