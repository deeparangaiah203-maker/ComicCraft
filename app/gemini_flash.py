import logging
from app.config import settings
from app.models.schemas import ComicOutline, ComicPanel
from app.services.gemini_client import get_client

logger = logging.getLogger(__name__)

def _get_mock_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> dict:
    """
    Fallback mock outline generator when API is offline or mock_mode is enabled.
    """
    title = f"{character_name}'s Adventure in {setting}"
    panels = [
        ComicPanel(
            panel_number=1,
            title="The Beginning",
            description=f"{character_name} stands at the threshold of {setting}, contemplating the journey ahead.",
            image_prompt=f"Wide cinematic shot of {character_name} in {setting}, style of {art_style}, morning light, highly detailed.",
            caption=f"Every journey begins with a single step into {setting}."
        ),
        ComicPanel(
            panel_number=2,
            title="A Discovery",
            description=f"{character_name} discovers an unexpected anomaly in {setting} that changes everything.",
            image_prompt=f"Close up of {character_name} examining a mysterious glowing clue in {setting}, {art_style} style, dramatic lighting.",
            caption=f"Something unusual catches {character_name}'s eye."
        ),
        ComicPanel(
            panel_number=3,
            title="The Challenge",
            description=f"A sudden conflict erupts, testing {character_name}'s resolve and {tone.lower()} spirit.",
            image_prompt=f"Dynamic action composition of {character_name} facing an obstacle in {setting}, dynamic angles, {art_style} style.",
            caption=f"Danger approaches without warning!"
        ),
        ComicPanel(
            panel_number=4,
            title="The Turning Point",
            description=f"{character_name} makes a courageous move, overcoming doubts to turn the tide.",
            image_prompt=f"Heroic pose of {character_name} unleashing their ability or solving the puzzle, vibrant colors, {art_style} style.",
            caption=f"This is the moment of truth."
        ),
        ComicPanel(
            panel_number=5,
            title="Triumph & Beyond",
            description=f"Peace returns to {setting} as {character_name} reflects on the victory.",
            image_prompt=f"Golden hour scenic view of {character_name} smiling overlooking {setting}, peaceful atmosphere, {art_style} style.",
            caption=f"With the challenge overcome, a new chapter begins for {character_name}."
        ),
    ]

    return {
        "title": title,
        "panels": [p.model_dump() for p in panels]
    }

def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> dict:
    """
    Generate a 5-panel comic story outline using Gemini, with graceful fallback.
    """
    if settings.mock_mode:
        return _get_mock_outline(story_prompt, character_name, setting, tone, art_style)

    client = get_client()
    if not client:
        logger.warning("No Gemini client found, using mock outline.")
        return _get_mock_outline(story_prompt, character_name, setting, tone, art_style)

    prompt = f"""
You are an expert comic book story planner and script writer.

Create a cohesive comic story containing EXACTLY 5 panels based on the user's idea.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

STORY TONE:
{tone}

ART STYLE:
{art_style}

Requirements:
1. Provide a catchy, exciting comic Title.
2. Create exactly 5 panels numbered 1 through 5.
3. Each panel must continue naturally from the previous panel.
4. Keep the main character consistent throughout the story.
5. Give each panel a short and interesting title.
6. Give each panel a concise scene description.
7. Create a detailed visual prompt for image generation describing character appearance, action, environment, lighting, and camera composition in the specified art style.
8. Do NOT put text, captions, speech bubbles, logos, or watermarks inside visual image prompts.
9. Provide an engaging dialogue line or narration caption for each panel.
10. The story must progress:
    - Panel 1: Beginning / Inciting moment
    - Panel 2: Development / Exploration
    - Panel 3: Challenge / Escalation
    - Panel 4: Climax / Decisive action
    - Panel 5: Resolution / Ending

Return ONLY structured JSON matching the ComicOutline schema.
"""

    # Candidate models to try in order of preference
    candidate_models = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ComicOutline,
                    "temperature": 0.7,
                }
            )

            if response and response.text:
                result = ComicOutline.model_validate_json(response.text)
                if len(result.panels) == 5:
                    return {
                        "title": result.title or f"{character_name}'s Adventure",
                        "panels": [p.model_dump() for p in result.panels]
                    }
        except Exception as exc:
            logger.warning("Error with model %s: %s", model_name, exc)
            continue

    logger.warning("All Gemini model attempts failed; falling back to mock outline.")
    return _get_mock_outline(story_prompt, character_name, setting, tone, art_style)