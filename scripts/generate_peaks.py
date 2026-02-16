"""
Generate waveform peak JSON files from MP3s for wavesurfer.js.

Usage:
    python scripts/generate_peaks.py

Reads all .mp3 files from static/audio/ and writes corresponding
.json peak files to static/audio/peaks/. Also prints track durations
for use in data/music.json.

Requirements (dev-only):
    pip install miniaudio
"""

import array
import json
import os

import miniaudio

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "audio")
PEAKS_DIR = os.path.join(AUDIO_DIR, "peaks")
NUM_PEAKS = 200


def generate_peaks(mp3_path, num_peaks=NUM_PEAKS):
    decoded = miniaudio.decode_file(mp3_path, nchannels=1, output_format=miniaudio.SampleFormat.SIGNED16)
    samples = array.array("h", decoded.samples)
    chunk_size = max(1, len(samples) // num_peaks)
    peaks = []
    for i in range(num_peaks):
        start = i * chunk_size
        end = min(start + chunk_size, len(samples))
        chunk = samples[start:end]
        if chunk:
            peak = max(abs(s) for s in chunk) / 32768.0
            peaks.append(round(peak, 4))
        else:
            peaks.append(0)
    return peaks, decoded.duration


def main():
    os.makedirs(PEAKS_DIR, exist_ok=True)

    mp3_files = sorted(f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(".mp3"))
    if not mp3_files:
        print(f"No .mp3 files found in {os.path.abspath(AUDIO_DIR)}")
        return

    print(f"Processing {len(mp3_files)} file(s)...\n")

    for filename in mp3_files:
        mp3_path = os.path.join(AUDIO_DIR, filename)
        peaks, duration_secs = generate_peaks(mp3_path)

        json_name = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(PEAKS_DIR, json_name)
        with open(json_path, "w") as f:
            json.dump({"data": [peaks]}, f)

        mins = int(duration_secs) // 60
        secs = int(duration_secs) % 60
        print(f"  {filename} -> {json_name}  ({mins}:{secs:02d})")

    print("\nDone! Copy the durations above into data/music.json.")


if __name__ == "__main__":
    main()
