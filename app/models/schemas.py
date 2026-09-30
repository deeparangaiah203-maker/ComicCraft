from pydantic import BaseModel, Field
from typing import List, Optional

class PromptRequest(BaseModel):
    story_prompt: str
    character_name: str
    setting: str
    tone: str
    art_style: str

class ComicPanel(BaseModel):
    panel_number: int = Field(..., description="Panel sequence number, from 1 to 5")
    title: str = Field(..., description="Short catchy title for the panel")
    description: str = Field(..., description="Brief description of what happens in this scene")
    image_prompt: str = Field(..., description="Detailed visual prompt for generating the image")
    caption: Optional[str] = Field(default="", description="Narrative caption or dialogue for this panel")
    image_url: Optional[str] = Field(default=None, description="URL or path to generated panel image")

class ComicOutline(BaseModel):
    title: str = Field(..., description="Catchy title of the comic story")
    panels: List[ComicPanel] = Field(..., description="List of exactly 5 comic panels")