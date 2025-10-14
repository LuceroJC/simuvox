from simuvox_api import SimuVoxEngine, VoiceParameters
import time

engine = SimuVoxEngine()
params = VoiceParameters(gender="Male")

start = time.time()
result = engine.synthesize(params)
elapsed = time.time() - start

print(f"Time: {elapsed:.2f}s")
print(f"F0: {result.f0:.1f} Hz")
print(f"Jitter: {result.jitter_percent:.2f}%")

# Save audio
from scipy.io import wavfile
import numpy as np
audio_normalized = result.audio / np.max(np.abs(result.audio))
audio_int16 = (audio_normalized * 32767).astype(np.int16)
wavfile.write('test.wav', result.sample_rate, audio_int16)
print("✓ Saved test.wav")