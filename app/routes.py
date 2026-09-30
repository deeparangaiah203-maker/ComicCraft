from pathlib import Path
import logging
import traceback

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
)

from app.config import settings
from app.models.schemas import PromptRequest
from app.gemini_flash import generate_outline
from app.services.image_generator import generate_image, create_comic_pdf

logger = logging.getLogger(__name__)
router = APIRouter()

templates = None

def get_templates():
    """
    Lazily initialize Jinja templates.
    """
    global templates
    if templates is None:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory=str(settings.templates_dir))
    return templates


# ============================================================
# HOME PAGE
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
    name="home",
)
async def home(request: Request):
    return get_templates().TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None,
            "mock_mode": settings.mock_mode,
        },
    )


# ============================================================
# HTML COMIC GENERATION
# ============================================================

@router.post(
    "/generate",
    response_class=HTMLResponse,
    name="generate",
)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        # 1. Generate story outline and panels
        outline = generate_outline(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        title = outline.get("title", f"{character_name}'s Adventure")
        panels = outline.get("panels", [])

        # 2. Generate visuals for each panel
        for panel in panels:
            img_url = generate_image(
                prompt=panel.get("image_prompt", ""),
                panel_number=panel.get("panel_number", 1),
                title=panel.get("title", ""),
                art_style=art_style,
            )
            panel["image_url"] = img_url

        # 3. Create PDF export
        pdf_url = create_comic_pdf(title=title, panels=panels)

        return get_templates().TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": title,
                "story_prompt": story_prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style,
                "panels": panels,
                "pdf_url": pdf_url,
                "mock_mode": settings.mock_mode,
            },
        )

    except Exception as exc:
        traceback.print_exc()
        return get_templates().TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc),
                "mock_mode": settings.mock_mode,
            },
            status_code=500,
        )


# ============================================================
# JSON API
# ============================================================

@router.post(
    "/generate-comic/json",
    response_model=dict,
    name="generate_comic_json",
)
async def generate_comic_json(
    payload: PromptRequest,
):
    try:
        outline = generate_outline(
            story_prompt=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style,
        )

        title = outline.get("title", f"{payload.character_name}'s Adventure")
        panels = outline.get("panels", [])

        for panel in panels:
            img_url = generate_image(
                prompt=panel.get("image_prompt", ""),
                panel_number=panel.get("panel_number", 1),
                title=panel.get("title", ""),
                art_style=payload.art_style,
            )
            panel["image_url"] = img_url

        pdf_url = create_comic_pdf(title=title, panels=panels)

        return JSONResponse(
            content={
                "title": title,
                "panels": panels,
                "pdf_url": pdf_url,
            }
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# ============================================================
# PDF DOWNLOAD
# ============================================================

@router.get(
    "/download/{filename}",
    name="download_pdf",
)
async def download_pdf(
    filename: str,
):
    # Prevent path traversal
    if (
        Path(filename).name != filename
        or not filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid export filename.",
        )

    file_path = settings.exports_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Export not found.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
    )


# ============================================================
# EXPORT SUCCESS PAGE
# ============================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse,
    name="export_success",
)
async def export_success(
    request: Request,
    pdf_url: str | None = None,
):
    return get_templates().TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url,
        },
    )


# ============================================================
# IMAGE TEST
# ============================================================

@router.get(
    "/test-image",
    response_class=JSONResponse,
    name="test_image",
)
async def test_image(
    prompt: str = "A friendly fox in a magical forest, comic book style",
):
    try:
        image_url = generate_image(
            prompt=prompt,
            panel_number=1,
            title="Test Panel",
            art_style="Comic Book",
        )
        return {
            "image_url": image_url
        }
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc