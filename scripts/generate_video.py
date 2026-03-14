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
FPS = 30
FADE_IN = 0.08    # fast snap-in
FADE_OUT = 0.12   # brief blink-out before next sentence
SENTENCE_PAD = 0.1  # gap between sentences
FONT_SIZE = 60
OUTLINE_WIDTH = 4  # pixels of text outline for readability
MAX_CHARS_PER_LINE = 26

# Text appearance
TEXT_COLOR = (255, 255, 255)
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


def load_background(path: str | None) -> Image.Image:
    """Load and prepare a background image, or fall back to gradient."""
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB")
        # Resize to cover 1080x1920 (crop to fill)
        img_ratio = img.width / img.height
        target_ratio = WIDTH / HEIGHT
        if img_ratio > target_ratio:
            # Image is wider — fit height, crop width
            new_height = HEIGHT
            new_width = int(HEIGHT * img_ratio)
        else:
            # Image is taller — fit width, crop height
            new_width = WIDTH
            new_height = int(WIDTH / img_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        # Center crop
        left = (new_width - WIDTH) // 2
        top = (new_height - HEIGHT) // 2
        img = img.crop((left, top, left + WIDTH, top + HEIGHT))
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


def render_sentence_card(
    sentence: str,
) -> Image.Image:
    """Render a single sentence centered on a transparent background."""
    card = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Word-wrap
    lines = textwrap.wrap(sentence, width=MAX_CHARS_PER_LINE)

    # Calculate line heights
    line_metrics = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    line_spacing = 14
    total_height = sum(h for _, h in line_metrics) + line_spacing * (len(lines) - 1)
    # Position in the lower 1/3 of the frame
    y_start = int(HEIGHT * 0.7) - (total_height // 2)

    for i, line in enumerate(lines):
        w, h = line_metrics[i]
        x = (WIDTH - w) // 2
        y = y_start + sum(line_metrics[j][1] for j in range(i)) + line_spacing * i
        draw_outlined_text(draw, (x, y), line, font)

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


# ─── Video Assembly ──────────────────────────────────────────────────────────


def build_video(script: dict, output_dir: str, bg_path: str | None = None) -> str:
    """Build the complete reel from a video script dict."""
    topic = script["topic"]
    voice = script.get("voice", "en-US-Chirp3-HD-Charon")
    sentences = script["sentences"]

    # Load background image
    bg = load_background(bg_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_segments = []
        segment_durations = []

        # ── Synthesize all audio first ──
        print("🎙️  Synthesizing speech...")
        for i, sentence in enumerate(sentences):
            audio_path = os.path.join(tmpdir, f"sentence_{i:02d}.mp3")
            synthesize_speech(sentence, voice, audio_path)
            duration = get_audio_duration(audio_path)
            segment_durations.append(duration)

            audio_segments.append(AudioFileClip(audio_path))

            # Add a short pause between sentences
            if i < len(sentences) - 1:
                pause_path = os.path.join(tmpdir, f"pause_{i:02d}.mp3")
                generate_silence(SENTENCE_PAD, pause_path)
                audio_segments.append(AudioFileClip(pause_path))

            abbrev = sentence[:55] + "..." if len(sentence) > 55 else sentence
            print(f"   [{i+1}/{len(sentences)}] {duration:.1f}s — \"{abbrev}\"")

        # ── Concatenate audio ──
        full_audio = concatenate_audioclips(audio_segments)
        total_duration = full_audio.duration
        print(f"\n📐 Total audio: {total_duration:.1f}s")

        # ── Render text cards and build video clips ──
        print("🎬  Rendering frames...")
        video_clips = []
        current_time = 0.0

        # Background clip for full duration
        bg_path_file = os.path.join(tmpdir, "bg_base.png")
        bg.save(bg_path_file)
        bg_clip = ImageClip(bg_path_file).with_duration(total_duration)
        video_clips.append(bg_clip)

        # Persistent darkening layer (behind all text)
        darkening_layer = prepare_text_region_transparent()
        darkening_path = os.path.join(tmpdir, "darkening.png")
        darkening_layer.save(darkening_path)
        darkening_clip = ImageClip(darkening_path).with_duration(total_duration)
        video_clips.append(darkening_clip)

        for i, sentence in enumerate(sentences):
            # Each sentence card duration = speech duration + pad
            card_dur = segment_durations[i] + SENTENCE_PAD

            # Render the text card (transparent)
            card = render_sentence_card(sentence)
            card_path = os.path.join(tmpdir, f"card_{i:02d}.png")
            card.save(card_path)

            # Create clip with crossfade
            clip = (
                ImageClip(card_path)
                .with_duration(card_dur)
                .with_start(current_time)
                .with_effects([
                    vfx.CrossFadeIn(FADE_IN),
                    vfx.CrossFadeOut(FADE_OUT),
                ])
            )
            video_clips.append(clip)
            current_time += card_dur

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

    build_video(script, output_dir, bg_path=args.background)


if __name__ == "__main__":
    main()
