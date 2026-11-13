import math

from pathlib import Path


def validate_clip_times(
        start_time: float,
        end_time: float,
        video_duration: float
) -> bool:
    """Return True if start_time, end_time and duration follow the correct range/order rules."""

    parameters: list[float] = [
        start_time,
        end_time,
        video_duration
    ]

    CLIP_DURATION: float = 15.0

    for par in parameters:
    # Loop parameters for valid time types (int, float)
        # if not isinstance(par, (int, float)):
        #     return False
        if type(par) not in (int, float):
            return False

    # Loop parameters to check if values are finite
        if not math.isfinite(par):
            return False

    # Check for negative values
        if par < 0:
            return False

    
    # Check that start >= 0, start < end, end > start, end <= video duration
    if not 0 <= start_time < end_time <= video_duration:
        return False

    if end_time - start_time > CLIP_DURATION:
        return False

    # If everything passes return True
    return True


def validate_gif_settings(
        fps: int,
        width: int
) -> bool:
    """Return True if FPS and output width satisfy the GIF settings rules."""

    parameters: list[int] = [
        fps, 
        width
    ]

    # check if fps and width are integers
    for par in parameters:
        if type(par) is not int:
            return False

    # Cap fps rate at 1 till 60
    if not 1 <= fps <= 60:
        return False

    # Ensure that the minimum pixel width is 2
    if width < 2:
        return False

    # Check that the width is an even value
    if width % 2 != 0:
        return False
    
    return True

    
def validate_conversion_paths(
    input_path: str,
    output_path: str
) -> bool:
    """Return True if the input and output paths satisfy conversion requirements."""

    pars: list[str] = [
        input_path,
        output_path
    ]

    for par in pars:

        # Check if path is a string
        if type(par) is not str:
            return False

        # Reject empty paths
        if not par.strip():
            return False

    input_file: Path = Path(input_path)
    output_file: Path = Path(output_path)

    # Check if input path is a regular file
    if not input_file.is_file():
        return False

    # Check if output path exists
    if output_file.exists():
        return False

    # Check if the output file is a ".gif"
    if output_file.suffix.lower() != ".gif":
        return False

    # Check that the output file has a parent directory
    if not output_file.parent.exists() or not output_file.parent.is_dir():
        return False

    if input_file.resolve() == output_file.resolve():
        return False

    return True
    

    