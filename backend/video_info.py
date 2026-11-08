import subprocess
import json
import math

from backend.exceptions import (
    FFprobeNotFoundError,
    InvalidVideoError
)


def inspect_video(file_path: str) -> dict:

    try:
        result: subprocess.CompletedProcess = subprocess.run(
            [
                "ffprobe",
                "-v", 
                "error", 
                "-show_format", 
                "-show_streams", 
                "-of", 
                "json", 
                file_path
            ],
            capture_output=True,
            text=True,
        )

    except FileNotFoundError as error:
        raise FFprobeNotFoundError("FFprobe executable could not be found.") from error

    return_code: int = result.returncode

    if return_code != 0:
        raise InvalidVideoError(
            f"FFprobe could not inspect the selected file: {result.stderr}"
        )

    try:
        metadata: dict = json.loads(result.stdout)

    except json.JSONDecodeError as error:
        raise InvalidVideoError(
            "FFprobe returned invalid JSON"
        ) from error

    if not isinstance(metadata, dict):
        raise InvalidVideoError("Invalid metadata information.")
    
    streams: list[dict] = metadata.get("streams", [])

    if not isinstance(streams, list):
        raise InvalidVideoError("Invalid stream information.")

    video_stream: dict | None = None

    for stream in streams:

        if not isinstance(stream, dict):
            raise InvalidVideoError("Invalid stream information.")

        if stream.get("codec_type") == "video":
            video_stream = stream
            break

    if video_stream is None:
        raise InvalidVideoError("The selected file contains no video stream.")

    format_info: dict = metadata.get("format", {})

    if not isinstance(format_info, dict):
        raise InvalidVideoError("Invalid format information.")

    width = video_stream.get("width")

    if not isinstance(width, int) or width <= 0:
        raise InvalidVideoError(
            "The video has invalid width."
        )

    height = video_stream.get("height")

    if not isinstance(height, int) or height <= 0:
        raise InvalidVideoError(
            "The video has invalid height."
        )

    codec_name = video_stream.get("codec_name")

    if not isinstance(codec_name, str) or not codec_name.strip():
        raise InvalidVideoError(
            "The video has an invalid codec."
        )

    duration_value = format_info.get("duration")

    if duration_value is None:
        raise InvalidVideoError(
            "The video has an invalid duration."
        )

    try:

        duration: float = float(duration_value)

    except (TypeError, ValueError) as error:
        raise InvalidVideoError(
            "The video duration could not be converted into a number."
        ) from error
    
    if not math.isfinite(duration) or duration <= 0:
        raise InvalidVideoError(
            "The video has an invalid duration."
        )

    return {
        "duration": duration,
        "width": width,
        "height": height,
        "codec_name": codec_name
    }

