from celery import Celery, group
import requests
import shutil
from pytube import YouTube
from pytube.exceptions import PytubeError
from typing import List
from urllib.parse import urlparse, urljoin
import m3u8

import os
import time

import subprocess

# import httpx


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)
DOWNLOADS_DIR = os.environ.get("DOWNLOADS_DIR", "project/downloads/")


M3U8_URL = os.environ.get(
    "M3U8_URL", "https://live-wuxi.cgtn.com/live/wx_cgtn_1000k_internalnormal.m3u8"
)


@celery.task(name="download_stream_url")
def download_stream_url(
    recording_duration: float = 60.0,
    max_fragment_duration: float = 20.0,
    playlist_url="",
    playlist_url_base="",
) -> List[str]:
    """Downloads a stream from the playlist_url and saves it to the specified DOWNLOADS_DIR directory..
    Parameters:
        recording_duration (int, optional): The duration of the recording in seconds. Defaults to 10.
        max_fragment_duration (int, optional): The duration of each fragment in seconds. Defaults to 10.
        playlist_url (str): The URL of m3u8 stream playlist to download.

    Returns:
        list[str]|None: Returns a list containing the local filename of the downloaded fragments.

    Note: Actual recording duration and duration of the fragments will be summarized from the duration of the stream fragments, but not less than one fragment.

    TODO: for tests the addresses are taken from environment,
            page         http://www.freeintertv.com/view/id-1099
            M3U8_URL =   https://live-wuxi.cgtn.com/live/wx_cgtn_1000k_internalnormal.m3u8
    on production you need to specify the actual address of the playlist
    or add a parser that will look for a link on the page

    TODO: think about how to convert to async while preserving the order of fragments
    """

    if playlist_url == "":
        playlist_url = M3U8_URL

    playlist_url_base = urljoin(playlist_url, ".")

    print(
        f"Recording video... {recording_duration}/{max_fragment_duration} from {playlist_url}"
    )

    total_duration: float = 0.0
    fragment_duration: float = 0.0
    fragment_count: int = 0
    segment_count: int = 0

    loaded_segments_old = set()
    loaded_segments = set()

    fragment_filename_list = []
    fragment_filename = None

    while total_duration < recording_duration:

        print("load m3u8..")
        m3u8_obj = m3u8.load(playlist_url)
        duration = m3u8_obj.data["targetduration"]

        playlist = [el["uri"] for el in m3u8_obj.data["segments"]]

        for ts_url in playlist:

            # pass repeating segment
            if ts_url in loaded_segments_old or ts_url in loaded_segments:
                continue

            stream_url = urljoin(playlist_url_base, ts_url)

            r1 = requests.get(stream_url, stream=True)
            num = 0
            if r1.status_code == 200:
                segment_count += 1

                if (fragment_filename is None) or (
                    fragment_duration > max_fragment_duration
                ):
                    fragment_count += 1
                    fragment_duration = 0.0
                    basename = os.path.basename(ts_url)
                    fragment_filename = os.path.join(DOWNLOADS_DIR, basename)

                    # Numbering of fragments - only needed for better readability in the destination folder
                    fragment_filename = fragment_filename.replace(
                        ".ts", f"-{fragment_count}.ts"
                    )

                    fragment_filename_list.append(fragment_filename)

                print(f"Recording fragment {fragment_count} segment {segment_count}...")
                with open(fragment_filename, "ab") as f:
                    for chunk in r1.iter_content(chunk_size=1024):
                        num += 1
                        f.write(chunk)
                        # watchdog timer, watchdog timer, in case the stream goes in one chunk.
                        if num > 5000:
                            print("end")
                            break

                loaded_segments.add(ts_url)
                fragment_duration += duration
                total_duration += duration

                if total_duration >= recording_duration:
                    break

        # clearing the list, since I only need to compare it to the last attempt.
        loaded_segments_old = loaded_segments
        loaded_segments = set()

        # if there is no required duration, wait for new fragments to appear in the stream
        if total_duration < recording_duration:
            time_to_sleep = 0.5 * duration * len(playlist)
            print(f"sleep {time_to_sleep}s")
            time.sleep(time_to_sleep)

    print(f"    done: fragment_filename_list {fragment_filename_list}")

    return fragment_filename_list


# TODO: add file existence check add file extension for url
@celery.task(name="download_file_url")
def download_file_url(url: str) -> List[str] | None:
    print(f"Downloading file {url}")

    basename = os.path.basename(urlparse(url).path)
    local_filename = os.path.join(DOWNLOADS_DIR, basename)

    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    print(f"    done: local_filename {local_filename}")

    return local_filename


# TODO: add file existence check and slugify filename
@celery.task(name="download_YouTube_url")
def download_YouTube_url(url: str) -> List[str] | None:
    print(f"download YouTube url {url}")

    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    stream.download(filename_prefix=DOWNLOADS_DIR)
    local_filename = stream.get_file_path()
    print(f"    done: local_filename {local_filename} size {stream.filesize_mb:.1f}Mb")
    return local_filename


@celery.task(name="create_task_list")
def create_task_list(filename_list: List[str]):
    if not filename_list:
        return False

    print(f"create_task_list {filename_list}")

    # TODO: add an external utility call here e.g.
    # for filename in filename_list:
    #     subprocess.call(['ffmpeg', '-i', filename' ...], shell=True)

    return True


@celery.task(name="create_task")
def create_task(filename: str | None):

    if filename is None:
        return False

    print(f"create_task {filename}")

    # TODO: add an external utility call here e.g.
    #     subprocess.call(['ffmpeg', '-i', filename' ...], shell=True)

    return True
