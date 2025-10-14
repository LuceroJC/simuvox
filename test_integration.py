from simuvox_api import SimuVoxEngine, VoiceParameters
import time
import numpy as np
from scipy.io import wavfile

print("Testing SimuVox API with your original code...\n")

engine = SimuVoxEngine()

# Test 1: Normal voice
print("Test 1: Normal male voice")
params = VoiceParameters(gender="Male", duration=1.5)
start = time.time()
result = engine.synthesize(params)
print(f"  Time: {time.time() - start:.2f}s")
print(f"  F0: {result.f0:.1f} Hz")
print(f"  Jitter: {result.jitter_percent:.2f}%")
print(f"  Success: {result.success}\n")

# Test 2: Disordered voice
print("Test 2: Female voice with jitter")
params = VoiceParameters(
    gender="Female",
    jitter=5.0,
    mass=0.12
    damping=0.015
    stiffness=185.0
    glottal_length=1.0 
    glottal_depth=0.25
)
start = time.time()
result = engine.synthesize(params)
print(f"  Time: {time.time() - start:.2f}s")
print(f"  F0: {result.f0:.1f} Hz")
print(f"  Jitter: {result.jitter_percent:.2f}%\n")

# Test 3: Save audio
print("Test 3: Saving audio file")
audio_normalized = result.audio / np.max(np.abs(result.audio))
audio_int16 = (audio_normalized * 32767).astype(np.int16)
wavfile.write('api_test.wav', result.sample_rate, audio_int16)
print("  ✓ Saved api_test.wav\n")

print("✅ All tests passed!")