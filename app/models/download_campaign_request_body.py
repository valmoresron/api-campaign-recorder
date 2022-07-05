from pydantic import BaseModel

class DownloadCampaignRequestBody(BaseModel):
    preview_url: str
    width: int
    height: int
    loops: int = 1
    target_fps: int = 24
    compress: bool = True