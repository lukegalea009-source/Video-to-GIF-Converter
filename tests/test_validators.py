import pytest

from pathlib import Path

from backend.validators import validate_clip_times, validate_gif_settings, validate_conversion_paths


@pytest.mark.parametrize(
    "start_time, end_time, video_duration, expected",
    [
        pytest.param(2, 6, 8.75, True, id="valid-selection"),
        pytest.param(0, 5, 8.75, True, id="valid-selection"),
        pytest.param(5, 3, 8.75, False, id="end-before-start"),
        pytest.param(-1, 4, 8.75, False, id="negative-start-time"),
        pytest.param(2, 10, 8.75, False, id="exceeds-video-duration"),
        pytest.param(0, 16, 30, False, id="exceeds-clipping-limit"),
        pytest.param(0, 15, 30, True, id="limit-clip-duration"),
        pytest.param(2, 2, 30, False, id="start-equal-end"),
        pytest.param(0, 14.9, 15, True, id="edgecase-endtime"),
        pytest.param(0, 0.1, 10, True, id="short-positive-clip"),
        pytest.param(0, 15.1, 30, False, id="exceeds-maximum"),
        pytest.param(float("nan"), 5, 10, False, id="NaN"),
        pytest.param(0, float("inf"), 10, False, id="infinity"),
        pytest.param(1, 5, 0, False, id="invalid-video-duration"),
        pytest.param(True, 5, 10, False, id="boolean-input"),
        pytest.param("5", 10, 15, False, id="str-input")
    ]
)
def test_validate_clip_times(
    start_time: float,
    end_time: float,
    video_duration: float,
    expected: bool
) -> None:

    result = validate_clip_times(
        start_time,
        end_time,
        video_duration
    )

    assert result is expected


@pytest.mark.parametrize(
    "fps, width, expected",
    [
        pytest.param(10, 320, True, id="normal-case-test"),
        pytest.param(15, 480, True, id="normal-case-test"),
        pytest.param(1, 2, True, id="edge-case-test"),
        pytest.param(60, 1920, True, id="fps-edge-case-test"),
        pytest.param(0, 320, False, id="fps-under-range-test"),
        pytest.param(61, 320, False, id="fps-over-range-test"),
        pytest.param(10, 321, False, id="odd-width-test"),
        pytest.param(10, 0, False, id="width-under-range-test"),
        pytest.param(True, 320, False, id="fps-bool-test"),
        pytest.param(15.5, 480, False, id="fps-float-test")
    ]
)
def test_validate_gif_settings(
    fps: int,
    width: int,
    expected: bool
) -> None:

    result = validate_gif_settings(
        fps,
        width
    )

    assert result is expected


@pytest.mark.parametrize(
    "create_input, create_output, extension, expected",
    [
        (True, False, ".gif", True),
        (False, False, ".gif", False),
        (True, True, ".gif", False),
        (True, False, ".mp4", False),
        (True, False, ".GIF", True),
    ]
)
def test_conversion_paths(
    tmp_path: Path,
    create_input: bool,
    create_output: bool,
    extension: str,
    expected: bool
) -> None:

    input_file = tmp_path / "video.mp4"
    output_file = tmp_path / f"output{extension}"

    if create_input:
        input_file.write_bytes(b"fake video")

    if create_output:
        output_file.write_bytes(b"existing file")

    result = validate_conversion_paths(
        str(input_file),
        str(output_file)
    )

    assert result is expected


def test_input_is_directory(tmp_path: Path) -> None:

    input_directory = tmp_path / "videos"
    input_directory.mkdir()

    output_file = tmp_path / "output.gif"

    assert validate_conversion_paths(
        str(input_directory),
        str(output_file)
    ) is False


def test_missing_output_directory(tmp_path: Path) -> None:

    input_file = tmp_path / "video.mp4"
    input_file.write_bytes(b"fake video")

    output_directory = tmp_path / "outputs"
    output_file = output_directory / "output.gif"

    assert validate_conversion_paths(
        str(input_file),
        str(output_directory)
    ) is False