from pathlib import Path

import pytest
import subprocess

from backend.converter import VidToGIFConverter
from backend.exceptions import GIFConversionError


@pytest.mark.parametrize(
    "input_path, output_path, start_time, end_time, fps, width",
    [
        pytest.param("input.mp4", "output.gif", 2, 6, 10, 320, id="normal-expected-options"),
        pytest.param("input.mp4", "output.gif", 0, 5, 15, 480, id="start-from-zero"),
        pytest.param("input.mp4", "output.gif", 1.5, 3.5, 24, 640, id="start-end-float-vals")
    ]
)
def test_build_ffmpeg_command(
    input_path: str,
    output_path: str,
    start_time: float,
    end_time: float,
    fps: int,
    width: int,
) -> None:

    command = VidToGIFConverter().build_ffmpeg_command(
        input_path,
        output_path,
        start_time,
        end_time,
        fps,
        width
    )

    duration_index = command.index("-t")
    assert float(command[duration_index + 1]) == pytest.approx(
        end_time - start_time
    )

    filter_index = command.index("-filter_complex")
    filter_graph = command[filter_index + 1]

    assert f"fps={fps}" in filter_graph
    assert f"scale={width}:-1" in filter_graph
    assert "palettegen" in filter_graph
    assert "paletteuse" in filter_graph

    # Verify ffmpeg executable
    assert command[0] == "ffmpeg"

    # Verify start time
    start_index = command.index("-ss")
    assert float(command[start_index + 1]) == pytest.approx(start_time)
    
    # Verify input path
    input_index = command.index("-i")
    assert command[input_index + 1] == input_path

    # Verify output path
    assert command[-1] == output_path

    # Verify infinite looping
    loop_index = command.index("-loop")
    assert command[loop_index + 1] == "0"


def mock_ffmpeg(
        monkeypatch: pytest.MonkeyPatch,
        returncode: int,
        stderr: str
) -> None:

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=returncode,
            stdout="",
            stderr=stderr
        )

    monkeypatch.setattr(subprocess, "run", fake_run)


def create_test_paths(tmp_path: Path) -> tuple[str, str]:

    input_file = tmp_path / "video.mp4"
    output_file = tmp_path / "output.gif"

    input_file.write_bytes(b"fake video data")

    return str(input_file), str(output_file)


def test_conversion_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path
) -> None:

    input_path, output_path = create_test_paths(tmp_path)

    mock_ffmpeg(monkeypatch, returncode=0, stderr="")

    result = VidToGIFConverter.convert_video_to_gif(
        input_path=input_path,
        output_path=output_path,
        start_time=2,
        end_time=6,
        video_duration=10,
        fps=8,
        width=320
    )

    assert result is None


def test_conversion_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path
) -> None:

    input_path, output_path = create_test_paths(tmp_path)

    mock_ffmpeg(
        monkeypatch,
        returncode=1,
        stderr="invalid data found when processing input"
    )

    with pytest.raises(GIFConversionError) as exc_info:
        VidToGIFConverter.convert_video_to_gif(
            input_path=input_path,
            output_path=output_path,
            start_time=2,
            end_time=6,
            video_duration=10,
            fps=8,
            width=320
        )

    assert "invalid data" in str(exc_info.value).lower()


def test_ffmpeg_not_found(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path
) -> None:

    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess:
        raise FileNotFoundError("ffmpeg not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    input_path, output_path = create_test_paths(tmp_path)

    with pytest.raises(GIFConversionError) as exc_info:
        VidToGIFConverter.convert_video_to_gif(
            input_path=input_path,
            output_path=output_path,
            start_time=2,
            end_time=6,
            video_duration=10,
            fps=8,
            width=320
        )

    assert "ffmpeg executable could not be found" in str(exc_info.value).lower()


def fake_run_helper(monkeypatch: pytest.MonkeyPatch) -> list[tuple]:

    calls = []

    def fake_run(*args, **kwargs) -> None:
        calls.append(args)
        raise AssertionError("FFmpeg should not have been executed.")
    
    monkeypatch.setattr(subprocess, "run", fake_run)

    return calls


def test_invalid_gif_settings(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path
) -> None:

    input_path, output_path = create_test_paths(tmp_path)

    calls = fake_run_helper(monkeypatch)

    with pytest.raises(GIFConversionError) as exc_info:
        VidToGIFConverter.convert_video_to_gif(
            input_path=input_path,
            output_path=output_path,
            start_time=2,
            end_time=6,
            video_duration=10,
            fps=-5,
            width=320
        )

    assert "gif settings" in str(exc_info.value).lower()
    assert calls == []


def test_invalid_clip_times(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path
) -> None:

    input_path, output_path = create_test_paths(tmp_path)

    calls = fake_run_helper(monkeypatch)

    with pytest.raises(GIFConversionError) as exc_info:
        VidToGIFConverter.convert_video_to_gif(
            input_path=input_path,
            output_path=output_path,
            start_time=2,
            end_time=1,
            video_duration=10,
            fps=5,
            width=320
        )

    assert "time settings" in str(exc_info.value).lower()
    assert calls == []


def test_invalid_conversion_path(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path
) -> None:

    input_path = str(tmp_path / "nonexistent_video.mp4")
    
    calls = fake_run_helper(monkeypatch)
    
    with pytest.raises(GIFConversionError) as exc_info:
        VidToGIFConverter.convert_video_to_gif(
            input_path=input_path,
            output_path="output.gif",
            start_time=2,
            end_time=6,
            video_duration=10,
            fps=5,
            width=320
        )
    
    assert "invalid file" in str(exc_info.value).lower()
    assert calls == []
    