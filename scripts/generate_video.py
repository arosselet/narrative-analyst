#!/usr/bin/env python3
"""
generate_video.py — Short-form video generator for the Actor-Narrative Framework.

Takes a video_script.json and produces a narrated 9:16 reel (TikTok/Instagram).
Uses Google Cloud TTS (Chirp3-HD) for voiceover and Pillow/MoviePy for compositing.

Usage:
    python scripts/generate_video.py analysis/topic/video_script.json
    python scripts/generate_video.py analysis/topic/video_script.json --background path/to/bg.png
"""

import json
import os
import sys
import subprocess
import tempfile
import textwrap
from pathlib import Path
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from google.cloud import texttospeech
from moviepy import (
    ImageClip,
    AudioFileClip,
    VideoFileClip,
    CompositeVideoClip,
    concatenate_audioclips,
    vfx,
)

# ─── Constants ───────────────────────────────────────────────────────────────

WIDTH, HEIGHT = 1080, 1920  # 9:16 portrait
KB_WIDTH, KB_HEIGHT = 1296, 2304  # 1.2x for Ken Burns bleed room
FPS = 30
FADE_IN = 0.08    # fast snap-in
FADE_OUT = 0.12   # brief blink-out before next sentence
SENTENCE_PAD = 0.1  # gap between sentences
FONT_SIZE = 60
OUTLINE_WIDTH = 4  # pixels of text outline for readability
MAX_CHARS_PER_LINE = 26
KB_ZOOM_START = 1.0
KB_ZOOM_END = 1.25

# Whisper model for forced alignment (word timestamps)
WHISPER_MODEL_SIZE = "tiny"  # fast; accurate enough for subtitle alignment

# Text appearance
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (255, 215, 0)  # gold highlight for active word
OUTLINE_COLOR = (0, 0, 0)

# Fallback gradient colors (used if no background image)
BG_TOP = (10, 10, 30)
BG_BOTTOM = (20, 15, 50)

# Font search paths
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/LiberationSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]


def find_font(candidates: list[str]) -> str:
    for path in candidates:
        if os.path.exists(path):
            return path
    return "DejaVuSans-Bold.ttf"


FONT_PATH = find_font(FONT_BOLD_CANDIDATES)


# ─── Background ──────────────────────────────────────────────────────────────


def make_gradient_bg() -> Image.Image:
    """Fallback: vertical dark gradient background."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img


def load_background(path: str | None, ken_burns: bool = True) -> Image.Image:
    """Load and prepare a background image, or fall back to gradient.
    
    When ken_burns=True, the image is sized to KB_WIDTH×KB_HEIGHT (1.2x)
    to provide bleed room for the zoom animation.
    """
    tw = KB_WIDTH if ken_burns else WIDTH
    th = KB_HEIGHT if ken_burns else HEIGHT
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB")
        img_ratio = img.width / img.height
        target_ratio = tw / th
        if img_ratio > target_ratio:
            new_height = th
            new_width = int(th * img_ratio)
        else:
            new_width = tw
            new_height = int(tw / img_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        left = (new_width - tw) // 2
        top = (new_height - th) // 2
        img = img.crop((left, top, left + tw, top + th))
        return img
    return make_gradient_bg()


def prepare_text_region_transparent() -> Image.Image:
    """Create a transparent layer with subtle darkening in the center lower third."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Gradient vignette: darker in the lower third
    target_y = int(HEIGHT * 0.7)
    band_height = HEIGHT // 4
    for y in range(HEIGHT):
        dist = abs(y - target_y)
        if dist < band_height:
            # Closer to target = more darkening
            alpha = int(140 * (1.0 - dist / band_height))
            draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    return img


# ─── Text Rendering ──────────────────────────────────────────────────────────


def draw_outlined_text(
    draw: ImageDraw.Draw,
    position: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple = TEXT_COLOR,
    outline_fill: tuple = OUTLINE_COLOR,
    outline_width: int = OUTLINE_WIDTH,
):
    """Draw text with a solid outline for readability over any background."""
    x, y = position
    # Draw outline by offsetting in all directions
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
    # Draw main text on top
    draw.text((x, y), text, font=font, fill=fill)


def render_stable_sentence(
    sentence: str,
    target_words: int,
    active_word_idx: int,
) -> Image.Image:
    """Render a sentence with stable layout and word-level highlighting.
    
    Uses font metrics (ascent/descent) for fixed line heights and prefix-length 
    tracking for stable horizontal positioning.
    """
    card = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    accent_font = ImageFont.truetype(FONT_PATH, int(FONT_SIZE * 1.1))

    # Font metrics for stable vertical layout
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    line_spacing = 20
    
    accent_ascent, accent_descent = accent_font.getmetrics()

    # Always wrap the FULL sentence to keep the layout / line breaks stable
    lines = textwrap.wrap(sentence, width=MAX_CHARS_PER_LINE)
    
    # Calculate vertical starting point (centered in lower 1/3)
    total_text_height = (line_height * len(lines)) + (line_spacing * (len(lines) - 1))
    y_center = int(HEIGHT * 0.73)
    y_start = y_center - (total_text_height // 2)

    all_words = sentence.split()
    word_counter = 0

    for i, line_text in enumerate(lines):
        # We need to know which words from all_words belong to this line
        line_words_raw = line_text.split()
        y_line = y_start + i * (line_height + line_spacing)

        # Calculate line width for centering
        line_bbox = draw.textbbox((0, 0), line_text, font=font)
        line_w = line_bbox[2] - line_bbox[0]
        x_start = (WIDTH - line_w) // 2
        
        # Draw words one by one
        current_x = x_start
        for word in line_words_raw:
            if word_counter >= target_words:
                break
                
            is_active = (word_counter == active_word_idx)
            use_font = accent_font if is_active else font
            use_color = ACCENT_COLOR if is_active else TEXT_COLOR

            # Metric-based positioning:
            # We anchor to the baseline: y_line + ascent
            baseline_y = y_line + ascent
            
            # For the accent font, we need to adjust its y so its baseline matches
            draw_y = y_line # default
            if is_active:
                # Align accent baseline with regular baseline
                draw_y = baseline_y - accent_ascent
                # Slightly shift x to center the larger word on its space
                word_w = draw.textbbox((0, 0), word, font=font)[2] - draw.textbbox((0, 0), word, font=font)[0]
                acc_w = draw.textbbox((0, 0), word, font=accent_font)[2] - draw.textbbox((0, 0), word, font=accent_font)[0]
                draw_x = current_x - (acc_w - word_w) // 2
            else:
                draw_x = current_x

            draw_outlined_text(draw, (draw_x, draw_y), word, use_font, fill=use_color)

            # Advance x by exactly the word's width in REGULAR font + space
            # This ensures subsequent words don't move when the previous word highlights
            w_w = draw.textbbox((0, 0), word, font=font)[2] - draw.textbbox((0, 0), word, font=font)[0]
            s_w = draw.textbbox((0, 0), " ", font=font)[2] - draw.textbbox((0, 0), " ", font=font)[0]
            current_x += w_w + s_w
            word_counter += 1

        if word_counter >= target_words:
            break

    return card



# ─── TTS ──────────────────────────────────────────────────────────────────────


def synthesize_speech(text: str, voice_name: str, output_path: str) -> None:
    """Synthesize speech using Google Cloud TTS Chirp3-HD."""
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(output_path, "wb") as f:
        f.write(response.audio_content)


def get_audio_duration(path: str) -> float:
    """Get duration of an audio file using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True,
        text=True,
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def generate_silence(duration: float, output_path: str) -> None:
    """Generate a silent audio file."""
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i",
            f"anullsrc=r=24000:cl=mono",
            "-t", str(duration),
            "-q:a", "9", "-acodec", "libmp3lame",
            output_path,
        ],
        capture_output=True,
    )


# ─── Forced Alignment ────────────────────────────────────────────────────────

_whisper_model = None


def _get_whisper_model():
    """Lazy-load the Whisper model (once per process)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print(f"   [align] Loading Whisper {WHISPER_MODEL_SIZE}...")
        _whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    return _whisper_model


def get_word_timestamps(audio_path: str, sentence: str) -> list[float]:
    """Return a list of start-times (in seconds) for each word in the sentence.

    Uses faster-whisper with word_timestamps=True on the sentence audio.
    Falls back to uniform spacing if alignment fails or returns wrong word count.
    """
    words = sentence.split()
    n_words = len(words)
    audio_dur = get_audio_duration(audio_path)

    try:
        model = _get_whisper_model()
        segments, _ = model.transcribe(
            audio_path,
            word_timestamps=True,
            language="en",
            beam_size=1,
        )
        aligned_words = []
        for seg in segments:
            for w in (seg.words or []):
                aligned_words.append(w.start)

        # Whisper may return slightly different word count from punctuation/contraction splits.
        # Align greedily: take the first n_words timestamps we can use.
        if len(aligned_words) >= n_words:
            return aligned_words[:n_words]
        elif len(aligned_words) > 0:
            # Pad missing tail words by spacing evenly after the last timestamp
            last_t = aligned_words[-1]
            remaining = n_words - len(aligned_words)
            gap = (audio_dur - last_t) / (remaining + 1)
            for k in range(1, remaining + 1):
                aligned_words.append(last_t + gap * k)
            return aligned_words
    except Exception as e:
        print(f"   [align] Warning: whisper alignment failed ({e}), using uniform timing")

    # Fallback: uniform spacing
    return [audio_dur * w_idx / n_words for w_idx in range(n_words)]


# ─── Video Assembly ──────────────────────────────────────────────────────────


def build_video(script: dict, output_dir: str, bg_path: str | None = None, max_duration: float | None = None) -> str:
    """Build the complete reel from a video script dict."""
    topic = script["topic"]
    voice = script.get("voice", "en-US-Chirp3-HD-Charon")
    sentences = script["sentences"]

    # Load background image
    bg = load_background(bg_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        # ── Single-call TTS for absolute sync ──
        print("🎙️  Synthesizing full voiceover...")
        full_text = " ".join(sentences)
        audio_path = os.path.join(tmpdir, "full_voiceover.mp3")
        synthesize_speech(full_text, voice, audio_path)
        
        full_audio = AudioFileClip(audio_path)
        if max_duration:
            full_audio = full_audio.subclipped(0, min(max_duration, full_audio.duration))
            
        total_duration = full_audio.duration
        print(f"📐 Total audio: {total_duration:.1f}s")

        # ── Single-pass forced alignment ──
        print("🔤  Aligning all words...")
        try:
            model = _get_whisper_model()
            segments, _ = model.transcribe(
                audio_path,
                word_timestamps=True,
                language="en",
                beam_size=5,
            )
            whisper_results = []
            for seg in segments:
                for w in (seg.words or []):
                    whisper_results.append({
                        "start": w.start, 
                        "end": w.end, 
                        "text": w.word.strip()
                    })
        except Exception as e:
            print(f"❌ Alignment failed: {e}")
            whisper_results = []

        # Map timestamps back to sentence structure using content matching
        script_words = []
        for s in sentences:
            script_words.extend(s.split())

        def clean_token(s):
            return "".join(c.lower() for c in s if c.isalnum())

        clean_script = [clean_token(w) for w in script_words]
        clean_whisper = [clean_token(w["text"]) for w in whisper_results]

        # ── Global Alignment (difflib) ──
        # We align the normalized script with the normalized whisper tokens.
        # This gives us "anchors" for exact/fuzzy matches and identifies gaps (merges/splits).
        import difflib
        
        sm = difflib.SequenceMatcher(None, clean_script, [clean_token(w["text"]) for w in whisper_results])
        all_word_timestamps = [None] * len(script_words)
        
        # 1. Map anchors
        for block in sm.get_matching_blocks():
            for idx in range(block.size):
                w_res = whisper_results[block.b + idx]
                all_word_timestamps[block.a + idx] = {
                    "start": w_res["start"],
                    "end": w_res["end"]
                }
        
        # 2. Fill gaps via interpolation
        last_idx = -1
        for i in range(len(all_word_timestamps) + 1):
            if i < len(all_word_timestamps) and all_word_timestamps[i] is not None:
                if i > last_idx + 1:
                    t0 = all_word_timestamps[last_idx]["end"] if last_idx >= 0 else 0.0
                    t1 = all_word_timestamps[i]["start"]
                    
                    gap_words = clean_script[last_idx+1 : i]
                    char_counts = [max(1, len(w)) for w in gap_words]
                    total_chars = sum(char_counts)
                    
                    current_t = t0
                    for k, word_idx in enumerate(range(last_idx+1, i)):
                        duration = (t1 - t0) * (char_counts[k] / total_chars)
                        all_word_timestamps[word_idx] = {
                            "start": current_t,
                            "end": current_t + duration
                        }
                        current_t += duration
                last_idx = i
            elif i == len(all_word_timestamps):
                if i > last_idx + 1:
                    t0 = all_word_timestamps[last_idx]["end"] if last_idx >= 0 else 0.0
                    t1 = total_duration
                    
                    gap_words = clean_script[last_idx+1:]
                    char_counts = [max(1, len(w)) for w in gap_words]
                    total_chars = sum(char_counts)
                    
                    current_t = t0
                    for k, word_idx in enumerate(range(last_idx+1, i)):
                        duration = (t1 - t0) * (char_counts[k] / total_chars)
                        all_word_timestamps[word_idx] = {
                            "start": current_t,
                            "end": current_t + duration
                        }
                        current_t += duration

        # Safety Fallback
        if any(t is None for t in all_word_timestamps):
            print("   [align] Warning: logic mismatch in SequenceMatcher, using uniform fallback")
            all_word_timestamps = []
            for i in range(len(script_words)):
                all_word_timestamps.append({
                    "start": total_duration * i / len(script_words),
                    "end": total_duration * (i + 1) / len(script_words)
                })

        if not all_word_timestamps or len(all_word_timestamps) != len(script_words):
             print("   [align] Warning: logic mismatch, falling back to interpolation...")
             if not whisper_results:
                  all_word_timestamps = [{"start": total_duration * i / len(script_words), "end": total_duration * (i + 1) / len(script_words)} for i in range(len(script_words))]
             else:
                  import numpy as np
                  w_starts = [w["start"] for w in whisper_results]
                  w_ends = [w["end"] for w in whisper_results]
                  old_indices = np.linspace(0, 1, len(w_starts))
                  new_indices = np.linspace(0, 1, len(script_words))
                  interp_starts = np.interp(new_indices, old_indices, w_starts).tolist()
                  interp_ends = np.interp(new_indices, old_indices, w_ends).tolist()
                  all_word_timestamps = [{"start": s, "end": e} for s, e in zip(interp_starts, interp_ends)]

        # ── Render text cards and build video clips ──
        print("🎬  Rendering frames...")
        video_clips = []

        # Background clip with Ken Burns zoom
        bg_path_file = os.path.join(tmpdir, "bg_base.png")
        bg.save(bg_path_file)
        bg_clip = ImageClip(bg_path_file).with_duration(total_duration)

        def kb_zoom(t):
            return KB_ZOOM_START + (KB_ZOOM_END - KB_ZOOM_START) * (t / total_duration)

        bg_clip = bg_clip.resized(kb_zoom).cropped(
            x_center=KB_WIDTH / 2, y_center=KB_HEIGHT / 2, width=WIDTH, height=HEIGHT
        )
        video_clips.append(bg_clip)

        # Persistent darkening layer
        darkening_layer = prepare_text_region_transparent()
        darkening_path = os.path.join(tmpdir, "darkening.png")
        darkening_layer.save(darkening_path)
        darkening_clip = ImageClip(darkening_path).with_duration(total_duration)
        video_clips.append(darkening_clip)

        # Build sentence cards based on word timing
        word_idx_global = 0
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            n_words = len(words)
            if n_words == 0: continue

            # Sentence timestamps
            sent_start = all_word_timestamps[word_idx_global]["start"]
            last_word_idx_abs = word_idx_global + n_words - 1
            sent_end_audio = all_word_timestamps[last_word_idx_abs]["end"]
            
            # The actual duration this sentence occupies is from its start to the 
            # start of the NEXT sentence, to ensure no "dead air" captions.
            if last_word_idx_abs + 1 < len(all_word_timestamps):
                sent_next_start = all_word_timestamps[last_word_idx_abs + 1]["start"]
                sent_limit = sent_next_start
            else:
                sent_limit = total_duration

            # Iterate words within sentence
            for w_idx_in_sent in range(n_words):
                w_idx_abs = word_idx_global + w_idx_in_sent
                w_timing = all_word_timestamps[w_idx_abs]
                w_start = w_timing["start"]
                
                if max_duration and w_start >= max_duration:
                    break
                
                # word duration logic:
                # Normal words hold until the next word starts.
                # The LAST word holds until the end of the sentence's allocated time (sent_limit).
                if w_idx_in_sent < n_words - 1:
                    w_next_t = all_word_timestamps[w_idx_abs + 1]["start"]
                else:
                    # Last word: hold until next sentence starts, 
                    # but at LEAST until the audio for this word ends.
                    w_next_t = max(w_timing["end"], sent_limit)
                
                # Render card for this specific state
                card = render_stable_sentence(sentence, w_idx_in_sent + 1, w_idx_in_sent)
                card_path = os.path.join(tmpdir, f"card_s{i}_w{w_idx_in_sent}.png")
                card.save(card_path)
                
                duration = max(0.05, w_next_t - w_start)
                clip = (
                    ImageClip(card_path)
                    .with_start(w_start)
                    .with_duration(duration)
                )
                
                # Fade in first word, fade out last word of sentence
                if w_idx_in_sent == 0:
                    clip = clip.with_effects([vfx.CrossFadeIn(FADE_IN)])
                if w_idx_in_sent == n_words - 1:
                    # The fade out should happen at the VERY end of the hold duration
                    clip = clip.with_effects([vfx.CrossFadeOut(FADE_OUT)])
                
                video_clips.append(clip)
            
            word_idx_global += n_words


        # ── Composite ──
        print("🔧  Compositing...")
        final = CompositeVideoClip(
            video_clips, size=(WIDTH, HEIGHT)
        ).with_audio(full_audio).with_duration(total_duration)

        # ── Write output ──
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{topic}_reel.mp4")

        final.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            logger="bar",
        )

        # Also save narration audio
        narration_path = os.path.join(output_dir, f"{topic}_narration.mp3")
        full_audio.write_audiofile(narration_path, logger=None)

        print(f"\n✅ Output: {output_path}")
        print(f"🔊 Audio:  {narration_path}")
        print(f"⏱️  Duration: {total_duration:.1f}s")

        return output_path


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a short-form video reel from a video_script.json"
    )
    parser.add_argument("script", help="Path to video_script.json")
    parser.add_argument(
        "--background", "-b",
        help="Path to background image (1080x1920 recommended). Falls back to gradient.",
        default=None,
    )
    parser.add_argument(
        "--limit", "-l",
        type=float,
        help="Limit video duration to N seconds (partial render).",
        default=None,
    )
    args = parser.parse_args()

    if not os.path.exists(args.script):
        print(f"Error: {args.script} not found")
        sys.exit(1)

    with open(args.script) as f:
        script = json.load(f)

    # Validate
    required = ["topic", "sentences"]
    for field in required:
        if field not in script:
            print(f"Error: Missing required field '{field}' in script")
            sys.exit(1)
    if not isinstance(script["sentences"], list) or len(script["sentences"]) < 3:
        print("Error: 'sentences' must be a list with at least 3 items")
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent
    output_dir = str(project_root / "videos")

    build_video(script, output_dir, bg_path=args.background, max_duration=args.limit)


if __name__ == "__main__":
    main()
