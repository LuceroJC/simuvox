# -*- coding: utf-8 -*-
"""
SimuVox API - Clean interface for PhonaLab integration

This module provides a simple, stateless API for voice synthesis
that can be called from web services or other applications.

Example:
    >>> from simuvox_api import SimuVoxEngine, VoiceParameters
    >>> engine = SimuVoxEngine()
    >>> params = VoiceParameters(gender="Female", jitter=2.5)
    >>> result = engine.synthesize(params)
    >>> print(f"F0: {result.f0:.1f} Hz, Jitter: {result.jitter_percent:.2f}%")
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple
import numpy as np
import config as cfg
import synthesis as syn
import spectral_par as sp


@dataclass
class VoiceParameters:
    """
    All voice synthesis parameters.
    
    Units match the GUI display values (not internal units):
    - lung_pressure in Pa (will be multiplied by 10 internally)
    - damping in N·s/m (will be multiplied by 1000 internally)
    - stiffness in N/m (will be multiplied by 1000 internally)
    - tau in ms (will be divided by 1000 internally)
    """
    
    # Source parameters
    lung_pressure: float = 500.0      # Pa (GUI default divided by 10)
    mass: float = 0.2                # g
    damping: float = 0.025           # N·s/m (GUI default divided by 1000)
    stiffness: float = 90.0          # N/m (GUI default divided by 1000)
    tau: float = 0.8                 # ms (GUI default * 1000)
    abduction: float = 0.08          # cm
    glottal_length: float = 1.4      # cm
    glottal_depth: float = 0.3       # cm
    
    # Simulation parameters
    duration: float = 1.5            # s
    onset_time: float = 0.3          # s
    offset_time: float = 0.15        # s
    pitch_decrease: bool = False     # 10% pitch decrease if True
    
    # Gender (automatically adjusts multiple parameters)
    gender: str = "Male"             # "Male" or "Female"
    
    # Disorder parameters (0-10 scale)
    asymmetry: float = 1.0           # Ratio 0.1 to 10 (log scale in GUI)
    wow: float = 0.0                 # 0-10
    tremor: float = 0.0              # 0-10
    jitter: float = 0.0              # 0-10 (muscle jitter/flutter)
    aspiration: float = 0.0          # 0-10 (aspiration noise)
    
    # Vocal tract configuration
    vocal_tract: str = "aa"          # Vowel or vocal tract file name
    
    # Advanced options (usually left at defaults)
    viscous_loss: bool = False
    wall_vibration: bool = False


@dataclass
class SynthesisResult:
    """
    Complete results from voice synthesis.
    
    Includes audio, acoustic measures, and waveform data for visualization.
    """
    
    # Audio output
    audio: np.ndarray                # Pressure signal (raw)
    sample_rate: int                 # Hz (typically 44100)
    
    # Acoustic measures
    f0: float                        # Fundamental frequency (Hz)
    jitter_percent: float            # Jitter (%)
    open_quotient: float             # Open quotient (0-1)
    snr_db: float                    # Signal-to-noise ratio (dB)
    spectral_balance: float          # Spectral balance (Hz)
    spectral_ratio: float            # Spectral ratio (dB)
    
    # Time series for visualization
    time: np.ndarray                 # Time vector (s)
    glottal_area: np.ndarray         # Glottal area (cm²)
    glottal_flow: np.ndarray         # Glottal flow (cm³/s)
    vocal_fold_displacement: np.ndarray  # Shape: (n_samples, 2) for left/right (cm)
    
    # Spectrogram data
    spectrogram: np.ndarray          # Magnitude in dB
    spectrogram_freq_max: float      # Maximum frequency (Hz)
    
    # Success flag
    success: bool = True
    error_message: str = ""


class SimuVoxEngine:
    """
    Pure synthesis engine - no GUI dependencies.
    
    Thread-safe and stateless - can be called from multiple threads
    or in a web API context.
    """
    
    def __init__(self):
        """Initialize the synthesis engine."""
        self._last_config = None
    
    def synthesize(self, params: VoiceParameters) -> SynthesisResult:
        """
        Generate synthetic voice with given parameters.
        
        Args:
            params: Voice synthesis parameters
            
        Returns:
            SynthesisResult with audio and all analysis measures
            
        Example:
            >>> engine = SimuVoxEngine()
            >>> params = VoiceParameters(
            ...     lung_pressure=80,
            ...     gender="Female",
            ...     jitter=2.5,
            ...     duration=2.0
            ... )
            >>> result = engine.synthesize(params)
            >>> print(f"F0: {result.f0:.1f} Hz")
            >>> print(f"Jitter: {result.jitter_percent:.2f}%")
            >>> # Save audio
            >>> from scipy.io import wavfile
            >>> audio_int16 = (result.audio * 32767).astype(np.int16)
            >>> wavfile.write('output.wav', result.sample_rate, audio_int16)
        """
        try:
            # Configure global parameters
            self._configure(params)
            
            # Run synthesis
            synthesis_obj = syn.Synthesis()
            p_end = synthesis_obj.get_voice()
            
            # Get acoustic measures
            f0, jitter = synthesis_obj.get_jitter()
            oq = synthesis_obj.get_openquotient()
            noise = synthesis_obj.get_noise()
            
            # Get glottal waveforms
            xg, ag, ug = synthesis_obj.get_glottal()
            
            # Compute spectral measures
            sb, sr = sp.compute_balance_and_ratio(ug)
            
            # Generate spectrogram
            try:
                from spec001_optimized import get_ims
            except ImportError:
                from spec001 import get_ims
            
            spec_data, f_max = get_ims(p_end)
            
            return SynthesisResult(
                audio=p_end,
                sample_rate=int(cfg.Param.FS),
                f0=float(f0),
                jitter_percent=float(jitter),
                open_quotient=float(oq),
                snr_db=float(noise[2]),
                spectral_balance=float(sb),
                spectral_ratio=float(sr),
                time=synthesis_obj.t,
                glottal_area=ag,
                glottal_flow=ug,
                vocal_fold_displacement=xg,
                spectrogram=spec_data,
                spectrogram_freq_max=float(f_max),
                success=True
            )
            
        except Exception as e:
            # Return error result instead of raising
            return SynthesisResult(
                audio=np.array([]),
                sample_rate=44100,
                f0=0.0,
                jitter_percent=0.0,
                open_quotient=0.0,
                snr_db=0.0,
                spectral_balance=0.0,
                spectral_ratio=0.0,
                time=np.array([]),
                glottal_area=np.array([]),
                glottal_flow=np.array([]),
                vocal_fold_displacement=np.array([]),
                spectrogram=np.array([[]]),
                spectrogram_freq_max=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _configure(self, params: VoiceParameters):
        """
        Update cfg.Param from VoiceParameters.
        
        Converts GUI units to internal units.
        """
        # Source parameters (convert units)
        cfg.Param.PL = params.lung_pressure * 10.0  # Pa → dyn/cm²
        cfg.Param.MASS = params.mass
        cfg.Param.DAMPING = params.damping * 1000.0  # N·s/m → dyn·s/cm
        cfg.Param.STIFFNESS = params.stiffness * 1000.0  # N/m → dyn/cm
        cfg.Param.TAU = params.tau / 1000.0  # ms → s
        cfg.Param.ABDUCTION = params.abduction
        cfg.Param.GLOTTAL_LENGTH = params.glottal_length
        cfg.Param.GLOTTAL_DEPTH = params.glottal_depth
        
        # Simulation parameters
        cfg.Param.TIME_TOTAL = params.duration
        cfg.Param.TIME_ONSET = params.onset_time
        cfg.Param.TIME_OFFSET = params.offset_time
        cfg.Param.PROSODY = params.pitch_decrease
        
        # Gender-specific parameters
        cfg.Param.GENDER = params.gender
        if params.gender == "Male":
            cfg.Param.GENDER_SCALE = 1.0
            cfg.Param.ETA = 500.0
        else:
            cfg.Param.GENDER_SCALE = 0.8
            cfg.Param.ETA = 1500.0
        
        # Disorder parameters
        cfg.Param.Q = params.asymmetry
        cfg.Param.WOW_SIZE = params.wow
        cfg.Param.TREMOR_SIZE = params.tremor
        cfg.Param.FLUTTER_SIZE = params.jitter
        cfg.Param.ASPIRATION = params.aspiration
        
        # Vocal tract
        cfg.Param.VT_FILE = params.vocal_tract
        
        # Advanced options
        cfg.Param.VISC_LOSS = params.viscous_loss
        cfg.Param.WALL_VIBR = params.wall_vibration


def synthesize_voice_simple(
    gender: str = "Male",
    lung_pressure: float = 80.0,
    jitter: float = 0.0,
    tremor: float = 0.0,
    aspiration: float = 0.0,
    duration: float = 1.5
) -> Tuple[np.ndarray, int, dict]:
    """
    Simplified API for quick synthesis.
    
    Args:
        gender: "Male" or "Female"
        lung_pressure: Lung pressure in Pa (default 80)
        jitter: Jitter level 0-10 (default 0)
        tremor: Tremor level 0-10 (default 0)
        aspiration: Aspiration noise 0-10 (default 0)
        duration: Duration in seconds (default 1.5)
    
    Returns:
        audio: Audio signal as numpy array
        sample_rate: Sample rate in Hz
        measures: Dict with acoustic measures (f0, jitter_percent, etc.)
    
    Example:
        >>> audio, sr, measures = synthesize_voice_simple(
        ...     gender="Female",
        ...     jitter=3.0,
        ...     duration=2.0
        ... )
        >>> print(f"Generated {len(audio)/sr:.1f}s of audio")
        >>> print(f"F0: {measures['f0']:.1f} Hz")
    """
    engine = SimuVoxEngine()
    params = VoiceParameters(
        gender=gender,
        lung_pressure=lung_pressure,
        jitter=jitter,
        tremor=tremor,
        aspiration=aspiration,
        duration=duration
    )
    
    result = engine.synthesize(params)
    
    if not result.success:
        raise RuntimeError(f"Synthesis failed: {result.error_message}")
    
    measures = {
        'f0': result.f0,
        'jitter_percent': result.jitter_percent,
        'open_quotient': result.open_quotient,
        'snr_db': result.snr_db,
        'spectral_balance': result.spectral_balance,
        'spectral_ratio': result.spectral_ratio
    }
    
    return result.audio, result.sample_rate, measures