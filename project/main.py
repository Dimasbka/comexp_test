from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from worker import (
    create_task_list,
    create_task,
    download_YouTube_url,
    download_file_url,
    download_stream_url,
)
from celery.result import AsyncResult

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.post("/download/YouTube", status_code=201)
async def download_YouTube(payload=Body(...)):
    url = payload.get("url", "").strip()
    if not url:
        return JSONResponse({"error": "Не указан url"}, status_code=422)

    task = download_YouTube_url.apply_async(kwargs={"url": url}, link=create_task.s())
    return JSONResponse({"task_id": task.id})


@app.post("/download/file", status_code=201)
async def download_file(payload=Body(...)) -> JSONResponse:
    url = payload.get("url", "").strip()
    if not url:
        return JSONResponse({"error": "Не указан url"}, status_code=422)

    task = download_file_url.apply_async(kwargs={"url": url}, link=create_task.s())
    return JSONResponse({"task_id": task.id})


@app.post("/download/stream", status_code=201)
async def download_stream(payload=Body(...)) -> JSONResponse:

    playlist_url = payload.get("playlist_url", "").strip()
    recording_duration = payload.get("recording_duration", "").strip()
    max_fragment_duration = payload.get("max_fragment_duration", "").strip()

    kwargs = {}
    if playlist_url:
        kwargs["playlist_url"] = playlist_url
    if recording_duration and recording_duration.isdigit():
        kwargs["recording_duration"] = int(recording_duration)
    if max_fragment_duration and max_fragment_duration.isdigit():
        kwargs["max_fragment_duration"] = int(max_fragment_duration)

    task = download_stream_url.apply_async(kwargs=kwargs, link=create_task_list.s())
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id) -> JSONResponse:
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": str(task_result.status),
        "task_result": str(task_result.result),
    }
    return JSONResponse(result)
