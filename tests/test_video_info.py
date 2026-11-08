import json
import subprocess

import pytest
from pytest import MonkeyPatch

from backend import video_info
from backend.video_info import inspect_video
from backend.exceptions import FFprobeNotFoundError, InvalidVideoError


def mock_ffprobe(
        monkeypatch: MonkeyPatch,
        metadata: dict
) -> None:

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=json.dumps(metadata),
            stderr=""
        )
    
    monkeypatch.setattr(subprocess, "run", fake_run)
    

def test_invalid_video_file() -> None:

    with pytest.raises(InvalidVideoError):
        inspect_video("this_video_does_not_exist_12345.mp4")


def test_valid_video_metadata(monkeypatch: MonkeyPatch) -> None:

    metadata = {
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
                "codec_name": "h264"
            }
        ],
        "format": {
            "duration": "8.75"
        }
    }

    mock_ffprobe(monkeypatch, metadata)

    video_info = inspect_video("example.mp4")

    assert video_info["duration"] == 8.75
    assert video_info["width"] == 1920
    assert video_info["height"] == 1080
    assert video_info["codec_name"] == "h264"


def test_missing_video_stream(monkeypatch: MonkeyPatch) -> None:

    metadata = {
        "streams": [
            {
                "codec_type": "audio",
                "codec_name": "aac"
            }
        ],
        "format": {
            "duration": "8.75"
        }
    }

    mock_ffprobe(monkeypatch, metadata)

    with pytest.raises(InvalidVideoError):
        inspect_video("example.mp4")


def test_invalid_duration(monkeypatch: MonkeyPatch) -> None:

    metadata = {
        "streams": [
            {
                "codec_type": "video",
                "width": 1920,
                "height": 1080,
                "codec_name": "h264"
            }
        ],
        "format": {
            "duration": "NaN"
        }
    }

    mock_ffprobe(monkeypatch, metadata)
    
    with pytest.raises(InvalidVideoError) as exc_info:
        inspect_video("example.mp4")

    assert "invalid duration" in str(exc_info.value).lower()


def test_ffprobe_not_found(monkeypatch: MonkeyPatch) -> None:

    def fake_run(*args, **kwargs) -> FileNotFoundError:
        raise FileNotFoundError("ffprobe not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(FFprobeNotFoundError):
        inspect_video("example.mp4")


def test_ffprobe_failure(monkeypatch: MonkeyPatch) -> None:

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="Invalid data found when processing input"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(InvalidVideoError) as exc_info:
        inspect_video("example.mp4")

    assert "Invalid data found when processing input" in str(exc_info.value)