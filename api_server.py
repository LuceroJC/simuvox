"""
FastAPI server for SimuVox - Web API for PhonaLab

Run with: uvicorn api_server:app --reload
Access at: http://localhost:8000
API docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np
import base64
import io
import wave
from typing import List, Optional
import spec001 as spg
from simuvox_api import SimuVoxEngine, VoiceParameters

app = FastAPI(
    title="SimuVox API",
    description="Physics-based voice synthesis for clinical applications",
    version="0.1.0"
)

# CORS configuration for PhonaLab frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global engine instance (stateless, thread-safe)
engine = SimuVoxEngine()


class SynthesisRequest(BaseModel):
    """Request schema for voice synthesis"""
    # Source parameters
    lung_pressure: float = Field(default=500.0, ge=0, le=2000, description="Lung pressure (Pa)")
    mass: float = Field(default=0.2, ge=0.01, le=1.0, description="Vocal fold mass (g)")
    damping: float = Field(default=0.025, ge=0.001, le=0.1, description="Damping coefficient (N·s/m)")
    stiffness: float = Field(default=90.0, ge=10, le=300, description="Stiffness (N/m)")
    tau: float = Field(default=0.8, ge=0.1, le=2.0, description="Mucosal wave delay (ms)")
    abduction: float = Field(default=0.08, ge=0, le=0.5, description="Initial separation (cm)")
    glottal_length: float = Field(default=1.4, ge=0.5, le=2.0, description="Glottal length (cm)")
    glottal_depth: float = Field(default=0.3, ge=0.1, le=0.5, description="Glottal depth (cm)")
    
    # Simulation parameters
    duration: float = Field(default=1.5, ge=0.5, le=5.0, description="Duration (s)")
    onset_time: float = Field(default=0.3, ge=0.1, le=1.0, description="Onset time (s)")
    offset_time: float = Field(default=0.15, ge=0.05, le=1.0, description="Offset time (s)")
    pitch_decrease: bool = Field(default=False, description="10% pitch decrease")
    
    # Gender
    gender: str = Field(default="Male", description="'Male' or 'Female'")
    
    # Disorder parameters (0-10 scale)
    asymmetry: float = Field(default=1.0, ge=0.1, le=10.0, description="Asymmetry ratio")
    wow: float = Field(default=1.0, ge=0, le=10, description="Wow (slow frequency modulation)")
    tremor: float = Field(default=1.0, ge=0, le=10, description="Tremor")
    jitter: float = Field(default=1.0, ge=0, le=10, description="Jitter (muscle flutter)")
    aspiration: float = Field(default=1.0, ge=0, le=10, description="Aspiration noise")
    
    # Vocal tract
    vocal_tract: str = Field(default="aa", description="Vowel configuration")
    
    # Advanced
    viscous_loss: bool = Field(default=False, description="Include viscous/thermal losses")
    wall_vibration: bool = Field(default=False, description="Include wall vibration")
    
    # Output options
    downsample_factor: int = Field(default=10, ge=1, le=100, description="Downsample waveforms for plotting")


class AcousticMeasures(BaseModel):
    """Acoustic analysis results"""
    f0: float = Field(description="Fundamental frequency (Hz)")
    jitter_percent: float = Field(description="Jitter (%)")
    open_quotient: float = Field(description="Open quotient (0-1)")
    snr_db: float = Field(description="Signal-to-noise ratio (dB)")
    spectral_balance: float = Field(description="Spectral balance (Hz)")
    spectral_ratio: float = Field(description="Spectral ratio (dB)")

class WaveformData(BaseModel):
    """Time series data for plotting"""
    time: List[float] = Field(description="Time vector (s)")
    glottal_area: List[float] = Field(description="Glottal area (cm²)")
    glottal_flow: List[float] = Field(description="Glottal flow (cm³/s)")
    vocal_fold_left: List[float] = Field(description="Left vocal fold displacement (cm)")
    vocal_fold_right: List[float] = Field(description="Right vocal fold displacement (cm)")
    acoustic_pressure: List[float] = Field(description="Acoustic pressure (Pa)")
    # Add spectrogram data:
    spectrogram: Optional[List[List[float]]] = Field(None, description="Spectrogram matrix")
    spectrogram_freq_max: Optional[float] = Field(None, description="Max frequency for spectrogram (kHz)")

class SynthesisResponse(BaseModel):
    """Response schema with all results"""
    success: bool
    error_message: Optional[str] = None
    
    # Acoustic measures
    measures: Optional[AcousticMeasures] = None
    
    # Audio (base64-encoded WAV file)
    audio_base64: Optional[str] = Field(None, description="Base64-encoded WAV audio")
    sample_rate: Optional[int] = Field(None, description="Sample rate (Hz)")
    duration_actual: Optional[float] = Field(None, description="Actual audio duration (s)")
    
    # Waveforms for visualization
    waveforms: Optional[WaveformData] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SimuVox API - Physics-based voice synthesis",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simuvox-api"}


@app.post("/api/synthesize", response_model=SynthesisResponse)
async def synthesize_voice(request: SynthesisRequest):
    """
    Synthesize voice with given parameters.
    
    Returns audio as base64-encoded WAV file and all acoustic measures.
    """
    try:
        # Validate gender
        if request.gender not in ["Male", "Female"]:
            raise HTTPException(
                status_code=400, 
                detail="Gender must be 'Male' or 'Female'"
            )
        
        # Convert request to VoiceParameters
        params = VoiceParameters(
            lung_pressure=request.lung_pressure,
            mass=request.mass,
            damping=request.damping,
            stiffness=request.stiffness,
            tau=request.tau,
            abduction=request.abduction,
            glottal_length=request.glottal_length,
            glottal_depth=request.glottal_depth,
            duration=request.duration,
            onset_time=request.onset_time,
            offset_time=request.offset_time,
            pitch_decrease=request.pitch_decrease,
            gender=request.gender,
            asymmetry=request.asymmetry,
            wow=request.wow,
            tremor=request.tremor,
            jitter=request.jitter,
            aspiration=request.aspiration,
            vocal_tract=request.vocal_tract,
            viscous_loss=request.viscous_loss,
            wall_vibration=request.wall_vibration
        )
        
        # Run synthesis
        result = engine.synthesize(params)
        
        if not result.success:
            return SynthesisResponse(
                success=False,
                error_message=result.error_message
            )
        
        # Convert audio to WAV format in memory
        audio_bytes = io.BytesIO()
        with wave.open(audio_bytes, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(result.sample_rate)
            # Normalize and convert to int16
            audio_normalized = result.audio / np.max(np.abs(result.audio))
            audio_int16 = (audio_normalized * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        # Encode as base64
        audio_base64 = base64.b64encode(audio_bytes.getvalue()).decode()
                
        # Downsample time series for efficient transmission
        ds = request.downsample_factor
        time_ds = result.time[::ds]

        # Extract vocal fold displacements
        vf_left = -result.vocal_fold_displacement[::ds, 0]
        vf_right = result.vocal_fold_displacement[::ds, 1]

        # Compute spectrogram - NO downsampling
        ims, fm1 = spg.get_ims(result.audio, window_length=0.050, overlap=0.92)
        vv = np.max(ims)
        ims_full = ims.clip(min=vv-50.)

        # Normalize to 0-50 range for better color mapping
        ims_normalized = ims_full - (vv - 50.)

        print(f"Spectrogram shape BEFORE transpose: {ims_normalized.shape}")
        print(f"Max frequency: {fm1} Hz")
        print(f"Duration: {len(result.audio) / result.sample_rate} s")
        print(f"Spectrogram value range: {ims_normalized.min():.1f} to {ims_normalized.max():.1f}")

        # Transpose so that rows=frequency, cols=time
        ims_transposed = ims_normalized.T

        print(f"Spectrogram shape AFTER transpose: {ims_transposed.shape}")

        return SynthesisResponse(
            success=True,
            measures=AcousticMeasures(
                f0=result.f0,
                jitter_percent=result.jitter_percent,
                open_quotient=result.open_quotient,
                snr_db=result.snr_db,
                spectral_balance=result.spectral_balance,
                spectral_ratio=result.spectral_ratio
            ),
            audio_base64=audio_base64,
            sample_rate=result.sample_rate,
            duration_actual=len(result.audio) / result.sample_rate,
             waveforms=WaveformData(
                time=time_ds.tolist(),
                glottal_area=result.glottal_area[::ds].tolist(),
                glottal_flow=(result.glottal_flow[::ds] / 1000).tolist(),
                vocal_fold_left=vf_left.tolist(),
                vocal_fold_right=vf_right.tolist(),
                acoustic_pressure=(result.audio[::ds] / 10).tolist(), 
                spectrogram=ims_transposed.tolist(),
                spectrogram_freq_max=fm1/1000.0
            )
        )
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error in synthesis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/presets/{gender}")
async def get_presets(gender: str):
    """
    Get default parameter presets for male or female voice.
    """
    if gender.lower() == "male":
        return {
            "gender": "Male",
            "mass": 0.2,
            "damping": 0.025,
            "stiffness": 90.0,
            "glottal_length": 1.4,
            "glottal_depth": 0.3
        }
    elif gender.lower() == "female":
        return {
            "gender": "Female",
            "mass": 0.12,
            "damping": 0.015,
            "stiffness": 185.0,
            "glottal_length": 1.0,
            "glottal_depth": 0.25
        }
    else:
        raise HTTPException(status_code=400, detail="Gender must be 'male' or 'female'")


@app.get("/api/vowels")
async def list_vowels():
    """List available vocal tract configurations (vowels)"""
    try:
        import config_lam as cfl
        return {
            "vowels": cfl.Param.VOWELCODE,
            "default": "aa"
        }
    except Exception as e:
        # Fallback if config_lam not available
        return {
            "vowels": ["aa", "ae", "ah", "ao", "eh", "er", "ih", "iy", "uh", "uw", "iw", "ew", "oe"],
            "default": "aa"
        }


@app.get("/api/vowel/{vowel_code}")
async def get_vowel_data(vowel_code: str, gender: str = "Male"):
    """
    Get vocal tract area function and formants for a specific vowel
    
    Parameters:
    - vowel_code: Vowel identifier (aa, ae, etc.)
    - gender: "Male" or "Female" (default: Male)
    
    Returns:
    - area_function: {distance: [array], area: [array]}
    - formants: {f1, f2, f3} in Hz
    """
    
    # Pre-computed formants (Hz) - no need for complex computation
    VOWEL_CODES = ["iy", "ey", "eh", "ah", "aa", "ao", "oh", "uw", "iw", "ew", "oe"]
    
    FORMANTS_MALE = {
        "iy": [201, 2311, 3061],
        "ey": [378, 2037, 2561],
        "eh": [515, 1679, 2478],
        "ah": [569, 1553, 2439],
        "aa": [637, 1259, 2354],
        "ao": [327, 514, 964],
        "oh": [468, 883, 2276],
        "uw": [225, 933, 2385],
        "iw": [289, 1653, 2402],
        "ew": [384, 1561, 2399],
        "oe": [463, 1669, 2473]
    }
    
    FORMANTS_FEMALE = {
        "iy": [240, 2562, 3351],
        "ey": [417, 2251, 2832],
        "eh": [547, 1810, 2676],
        "ah": [623, 1720, 2706],
        "aa": [697, 1393, 2602],
        "ao": [549, 1061, 2549],
        "oh": [506, 974, 2505],
        "uw": [241, 1035, 2621],
        "iw": [308, 1788, 2592],
        "ew": [416, 1734, 2662],
        "oe": [508, 1848, 2741]
    }
    
    # Validate vowel
    if vowel_code not in VOWEL_CODES:
        raise HTTPException(status_code=404, detail=f"Vowel '{vowel_code}' not found")
    
    # Get formants based on gender
    formants_dict = FORMANTS_MALE if gender == "Male" else FORMANTS_FEMALE
    formants = formants_dict[vowel_code]
    
    # Generate a simple schematic area function for visualization
    # (This is approximate - the actual vocal tract computation is complex)
    # For visualization purposes, we'll create a generic tract shape
    distance = np.linspace(0, 17, 29)  # Typical vocal tract ~17cm
    
    # Generic area function (varies by vowel - this is simplified)
    # Different vowels have different constriction patterns
    if vowel_code in ["iy", "iw"]:  # High front vowels - palatal constriction
        area = 3.0 + 2.0 * np.sin(distance / 17 * np.pi) - 1.5 * np.exp(-((distance - 7) ** 2) / 10)
    elif vowel_code in ["uw"]:  # High back vowel - velar/pharyngeal
        area = 2.5 + 1.5 * np.sin(distance / 17 * np.pi) + 1.0 * np.exp(-((distance - 12) ** 2) / 15)
    elif vowel_code in ["aa", "ah"]:  # Low vowels - open tract
        area = 4.0 + 2.5 * np.sin(distance / 17 * np.pi * 0.8)
    elif vowel_code in ["ao", "oh"]:  # Mid-back rounded
        area = 3.2 + 1.8 * np.sin(distance / 17 * np.pi) + 0.8 * np.exp(-((distance - 13) ** 2) / 12)
    else:  # Mid vowels - moderate opening
        area = 3.5 + 2.0 * np.sin(distance / 17 * np.pi)
    
    # Ensure positive areas
    area = np.maximum(area, 0.5)
    
    return {
        "vowel": vowel_code,
        "area_function": {
            "distance": distance.tolist(),
            "area": area.tolist()
        },
        "formants": {
            "f1": formants[0],
            "f2": formants[1],
            "f3": formants[2]
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting SimuVox API server...")
    print("API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)