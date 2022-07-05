from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse

from .campaign_recorder import CampaignRecorder
from .models.download_campaign_request_body import DownloadCampaignRequestBody

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR, "static"))), name="static")
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))


@app.get("/")
def home():
    return RedirectResponse(url="/docs")


# The recorder will navigate to this page
@app.get("/preview-campaign", response_class=HTMLResponse)
def preview_campaign(request: Request, preview_url: str, width: int, height: int) -> HTMLResponse:
    return templates.TemplateResponse(
        "campaign-preview.html",
        {
            "request": request,
            "preview_url": preview_url,
            "width": width,
            "height": height,
        },
    )


@app.get("/download-campaign")
def download_campaign(request: DownloadCampaignRequestBody) -> FileResponse:
    preview_url = request.preview_url
    width = request.width
    height = request.height
    loops = request.loops
    target_fps = request.target_fps
    compress = request.compress

    recorder = CampaignRecorder(
        preview_url=preview_url,
        width=width,
        height=height,
        loops=loops,
        target_fps=target_fps,
        compress=compress,
        timeout=30,
    )

    filepath = recorder.record()
    filename = filepath.split("/")[-1]

    return FileResponse(path=filepath, media_type="video/mp4", filename=filename)
