from worker import download_YouTube_url, download_file_url, download_stream_url
import sys
import argparse


def main():
    # argv = sys.argv
    # print(argv)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "playlist_url", help="The URL of m3u8 stream playlist to download"
    )
    parser.add_argument(
        "-r",
        "--recording_duration",
        type=int,
        help="The duration of the recording. Defaults to 120 seconds",
    )
    parser.add_argument(
        "-f",
        "--max_fragment_duration",
        type=int,
        help="The duration of each fragment. Defaults to 60 seconds",
    )

    args = parser.parse_args()

    arguments = {"playlist_url": args.playlist_url}
    if args.recording_duration:
        arguments["recording_duration"] = args.recording_duration
    if args.max_fragment_duration:
        arguments["max_fragment_duration"] = args.max_fragment_duration

    return download_stream_url(**arguments)


if __name__ == "__main__":
    sys.exit(main())

    # download_file_url("http://www.freeintertv.com/images/site_logo_11.gif")
    # download_YouTube_url("https://www.youtube.com/shorts/2aF8LHOtKRM")
    # download_YouTube_url("https://www.youtube.com/watch?v=lPiMjv7lkqI")
    # download_stream_url( playlist_url="https://live-wuxi.cgtn.com/live/wx_cgtn_1000k_internalnormal.m3u8" )
