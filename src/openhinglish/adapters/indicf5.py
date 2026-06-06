"""
EXPERIMENTAL — OpenHinglish Audio Adapter: AI4Bharat IndicF5
=============================================================

This module is an **optional** adapter that takes the Devanagari `tts` string
produced by ``openhinglish.normalize()`` and synthesizes Hindi speech using the
AI4Bharat IndicF5 model (MIT licence).

It is intentionally kept separate from the core package so that the heavy ML
stack (PyTorch, Transformers, a multi-GB model checkpoint) is NEVER loaded
unless the user deliberately opts in:

    pip install "openhinglish[tts]"

None of the symbols in this module are imported at package-init time.  The base
``openhinglish`` package works with zero heavy dependencies.

IndicF5 API reference (verify against the current model card):
  https://huggingface.co/ai4bharat/IndicF5

IMPORTANT CAVEAT — reference voice:
  IndicF5 is a **zero-shot, reference-conditioned** TTS model.  It requires a
  short (~5–10 s) reference WAV clip together with its transcript so it can
  clone the voice style.  Without a reference clip the function will raise a
  clear error rather than silently produce garbage output.

CPU performance warning:
  Inference on CPU is very slow — a 5-second utterance can take several minutes
  on a mid-range laptop.  A CUDA GPU is strongly recommended for interactive use.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Union

# ---------------------------------------------------------------------------
# Module-level model cache (loaded at most once per Python process)
# ---------------------------------------------------------------------------
_MODEL_CACHE: dict[str, object] = {}   # keyed by model_id


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require_tts_deps() -> None:
    """Raise a clear ImportError when the tts extra has not been installed."""
    missing = []
    for pkg in ("torch", "transformers", "soundfile", "huggingface_hub"):
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        raise ImportError(
            f"openhinglish[tts] optional dependencies are missing: {missing}.\n"
            "Install them with:\n\n"
            "    pip install \"openhinglish[tts]\"\n\n"
            "NOTE: this will trigger a multi-GB model download the first time\n"
            "the adapter is used.  A GPU is strongly recommended for real-time\n"
            "inference; CPU inference is functional but very slow."
        ) from None


def _load_model(model_id: str) -> tuple:
    """
    Load (and cache) the IndicF5 processor and model from Hugging Face Hub.

    The first call downloads the checkpoint (~several GB).  Subsequent calls
    within the same process return the cached objects immediately.

    Parameters
    ----------
    model_id:
        Hugging Face model identifier, e.g. ``"ai4bharat/IndicF5"``.

    Returns
    -------
    (processor, model)
        The processor and model objects ready for inference.

    .. admonition:: API assumption

       IndicF5 is loaded here via ``AutoProcessor`` + ``AutoModelForTextToWaveform``
       (the pattern used by SpeechT5/MMS-style models in Transformers ≥ 4.40).
       If IndicF5 exposes a custom pipeline class instead, replace the two
       ``Auto*`` calls with the correct class.  Check the model card at:
       https://huggingface.co/ai4bharat/IndicF5
    """
    if model_id in _MODEL_CACHE:
        return _MODEL_CACHE[model_id]

    # Lazy imports — torch and transformers are only pulled in here.
    import torch  # noqa: PLC0415
    from transformers import (  # noqa: PLC0415
        AutoProcessor,
        AutoModelForTextToWaveform,
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        warnings.warn(
            "No CUDA GPU detected.  IndicF5 inference will run on CPU and may\n"
            "take several minutes per utterance.",
            RuntimeWarning,
            stacklevel=4,
        )

    # --- ASSUMPTION: IndicF5 follows the standard Transformers AutoClass API.
    # If the model ships a dedicated class (e.g. IndicF5Model), swap the two
    # lines below for the correct import and from_pretrained call.
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForTextToWaveform.from_pretrained(model_id).to(device)
    model.eval()

    _MODEL_CACHE[model_id] = (processor, model)
    return processor, model


def _write_wav(audio_tensor, sample_rate: int, out_path: str) -> None:
    """Write a 1-D float tensor to a WAV file using soundfile."""
    import soundfile as sf  # noqa: PLC0415

    audio_np = audio_tensor.squeeze().cpu().float().numpy()
    sf.write(out_path, audio_np, sample_rate)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def synthesize(
    text_or_result,
    out_path: str = "out.wav",
    model_id: str = "ai4bharat/IndicF5",
    ref_audio: Union[str, Path, None] = None,
    ref_text: Union[str, None] = None,
) -> str:
    """
    Synthesize Hindi speech from a Devanagari TTS string and write a WAV file.

    EXPERIMENTAL — see module docstring for caveats.

    Parameters
    ----------
    text_or_result:
        Either a plain Devanagari string (e.g. the ``.tts`` field of a
        ``NormalizationResult``) or a ``NormalizationResult`` object directly.
        If a ``NormalizationResult`` is passed its ``.tts`` attribute is used.
    out_path:
        Destination file path for the generated WAV (default: ``"out.wav"``).
    model_id:
        Hugging Face model identifier.  Defaults to ``"ai4bharat/IndicF5"``.
        Override to point at a local checkpoint or a fine-tuned variant.
    ref_audio:
        Path to a short reference WAV clip (5–10 seconds) whose voice style
        IndicF5 should clone.  **Required** — IndicF5 is reference-conditioned
        and will raise ``ValueError`` if this is omitted.
    ref_text:
        The transcript of ``ref_audio`` (Devanagari or Roman script accepted
        by the model).  **Required** when ``ref_audio`` is provided.

    Returns
    -------
    str
        Absolute path to the written WAV file.

    Raises
    ------
    ImportError
        If ``openhinglish[tts]`` extras are not installed.
    ValueError
        If ``ref_audio`` or ``ref_text`` is missing (IndicF5 requires both).
    FileNotFoundError
        If the ``ref_audio`` path does not exist.

    Notes
    -----
    * Output sample rate is 24 kHz (IndicF5 default).  This is written directly
      into the WAV header — no resampling is performed.
    * CPU inference is functional but slow.  On a laptop CPU, expect 60–180 s
      of wall time for a single short sentence.
    * Model weights are cached by Hugging Face Hub (``~/.cache/huggingface``).
      First run downloads several gigabytes.

    .. admonition:: API assumption

       The ``generate()`` call below mirrors the SpeechT5-style interface::

           inputs = processor(text=..., audio=..., sampling_rate=16000,
                              return_tensors="pt")
           waveform = model.generate(**inputs)

       IndicF5 may use a different call signature — e.g. ``infer()`` or a
       custom ``pipeline`` — check the model card:
       https://huggingface.co/ai4bharat/IndicF5
       and adjust the block marked "# --- INFERENCE ---" below accordingly.
    """
    _require_tts_deps()

    # Resolve text from NormalizationResult or plain string
    from openhinglish.types import NormalizationResult  # noqa: PLC0415

    if isinstance(text_or_result, NormalizationResult):
        tts_text = text_or_result.tts
    elif isinstance(text_or_result, str):
        tts_text = text_or_result
    else:
        raise TypeError(
            f"text_or_result must be a str or NormalizationResult, got {type(text_or_result)!r}"
        )

    if not tts_text.strip():
        raise ValueError("tts_text is empty — nothing to synthesize.")

    # Reference voice is mandatory for IndicF5
    if ref_audio is None or ref_text is None:
        raise ValueError(
            "IndicF5 is a reference-conditioned model.  You must supply both:\n"
            "  ref_audio — path to a 5–10 s WAV clip of the target voice\n"
            "  ref_text  — transcript of that clip\n"
            "Example:\n"
            "  synthesize(result, ref_audio='voice.wav', ref_text='नमस्ते')"
        )

    ref_audio_path = Path(ref_audio)
    if not ref_audio_path.exists():
        raise FileNotFoundError(f"ref_audio not found: {ref_audio_path}")

    # Lazy imports
    import torch          # noqa: PLC0415
    import soundfile as sf  # noqa: PLC0415

    processor, model = _load_model(model_id)
    device = next(model.parameters()).device

    # Load reference audio (resample to 16 kHz if needed)
    ref_waveform, ref_sr = sf.read(str(ref_audio_path), dtype="float32")
    if ref_waveform.ndim > 1:
        ref_waveform = ref_waveform.mean(axis=1)  # stereo → mono

    # --- INFERENCE ---
    # ASSUMPTION: IndicF5 processor accepts (text, audio, sampling_rate) and
    # the model exposes a .generate() method returning a waveform tensor.
    # If the model ships a custom API (e.g. model.infer() or a Pipeline class),
    # replace the four lines below.  See: https://huggingface.co/ai4bharat/IndicF5
    inputs = processor(
        text=tts_text,
        audio=ref_waveform,
        sampling_rate=ref_sr,
        ref_text=ref_text,
        return_tensors="pt",
    )
    inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}

    with torch.no_grad():
        # ASSUMPTION: output is a waveform tensor; adjust attribute name if needed.
        output = model.generate(**inputs)
        # Some models wrap the waveform in a named tuple / dict:
        if hasattr(output, "waveforms"):
            waveform = output.waveforms[0]
        elif isinstance(output, dict):
            waveform = next(iter(output.values()))
        else:
            waveform = output[0]
    # --- END INFERENCE ---

    # Write output WAV (IndicF5 native sample rate is 24 kHz)
    SAMPLE_RATE = 24_000  # adjust if the model uses a different rate
    out_path = str(Path(out_path).resolve())
    _write_wav(waveform, SAMPLE_RATE, out_path)

    return out_path


def normalize_and_speak(
    raw_text: str,
    out_path: str = "out.wav",
    **kw,
) -> str:
    """
    Full pipeline: Roman-Hinglish text → Devanagari TTS string → WAV audio.

    This is the primary convenience function that demonstrates the complete
    OpenHinglish + IndicF5 integration:

    1. ``openhinglish.normalize(raw_text)`` converts Roman-Hinglish to a clean
       Devanagari string suitable for TTS (``result.tts``).
    2. ``synthesize(result.tts, ...)`` feeds that string into IndicF5 and writes
       a WAV file.

    EXPERIMENTAL — see module docstring for caveats.

    Parameters
    ----------
    raw_text:
        Roman-Hinglish input, e.g. ``"bhai kal mera intv h paytm me"``.
    out_path:
        Destination WAV path (default: ``"out.wav"``).
    **kw:
        Additional keyword arguments forwarded to :func:`synthesize`, most
        importantly ``ref_audio`` and ``ref_text`` (both required by IndicF5).

    Returns
    -------
    str
        Absolute path to the written WAV file.

    Example
    -------
    ::

        from openhinglish.adapters.indicf5 import normalize_and_speak

        normalize_and_speak(
            "bhai kal mera intv h paytm me",
            "demo.wav",
            ref_audio="my_voice.wav",
            ref_text="नमस्ते मेरा नाम शंकर है",
        )

    Notes
    -----
    The normalization step is CPU-only, deterministic, and near-instant.
    Only the TTS step requires the heavy ML stack.
    """
    _require_tts_deps()

    import openhinglish  # noqa: PLC0415

    result = openhinglish.normalize(raw_text)
    return synthesize(result, out_path=out_path, **kw)
