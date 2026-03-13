---
description: Generate a short-form reel (TikTok/Instagram) from an existing analysis
---

# Generate Reel (`/generate-reel`)

This workflow produces a 60-80 second narrated video from an existing Actor-Narrative Framework analysis.

**Inputs:**
1. A topic name that already has analysis files (e.g., `open-source-ai-war`).

**Execution Steps:**

**1. Verify Analysis Exists**
// turbo
- Confirm that `./analysis/<topic_name>/narrative_analysis.md` and `./analysis/<topic_name>/positioning_comparison.md` exist.
- If they don't exist, stop and tell the user to run `/adopt-persona` first.

**2. Stage 4: The Reel Writer**
- Read the instructions in `./prompts/short_form_writer.md` using the `view_file` tool.
- Adopt this persona and process `narrative_analysis.md` and `positioning_comparison.md`.
- Save your output to `./analysis/<topic_name>/video_script.json`.
- Present the script to the user for review before proceeding.

**3. Generate Background Image**
- Read the `background_prompt` field from the generated `video_script.json`.
- Use the `generate_image` tool with that prompt to create a vibrant, stunning background.
- Save the image to `./videos/<topic_name>_bg.png`.

**4. Generate Video**
// turbo
- Run the video generator: `python3 scripts/generate_video.py analysis/<topic_name>/video_script.json --background videos/<topic_name>_bg.png`
- Wait for the video to finish rendering.

**5. Completion**
- Notify the user with the path to the generated video (`videos/<topic_name>_reel.mp4`) and narration audio (`videos/<topic_name>_narration.mp3`).
- Report the video duration.
