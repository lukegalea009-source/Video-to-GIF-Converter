import subprocess

from backend.exceptions import GIFConversionError
from backend.validators import validate_clip_times, validate_gif_settings, validate_conversion_paths



class VidToGIFConverter:
    """Class containing methods used to communicate with FFmpeg."""


    @staticmethod
    def build_ffmpeg_command(
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
        fps: int,
        width: int
    ) -> list[str]:
        """Build an FFmpeg command for palette-based GIF conversion."""

        duration: float = end_time - start_time

        filter_graph: str = (
            f"[0:v]fps={fps},scale={width}:-1:flags=lanczos,"
            "split[a][b];"
            "[a]palettegen[p];"
            "[b][p]paletteuse"
        )

        command: list[str] = [
            "ffmpeg",
            "-n",
            "-ss", str(start_time),
            "-i", str(input_path),
            "-t", str(duration),
            "-filter_complex",
            filter_graph,
            "-loop", "0",
            str(output_path)
        ]

        return command


    @staticmethod
    def convert_video_to_gif(
            input_path: str,
            output_path: str,
            start_time: float,
            end_time: float,
            video_duration: float,
            fps: int,
            width: int
    ) -> None:
        """Convert a selected video to a GIF"""

        if not validate_conversion_paths(
            input_path,
            output_path
        ):
            raise GIFConversionError(
                "Invalid file paths found."
            ) 

        if not validate_clip_times(
            start_time,
            end_time,
            video_duration
        ):
            raise GIFConversionError(
                "Time settings are in an invalid selection."
            )

        if not validate_gif_settings(
            fps,
            width
        ):
            raise GIFConversionError(
                "GIF settings were entered incorrectly."
            )

        command: list[str] = VidToGIFConverter.build_ffmpeg_command(
            input_path=input_path,
            output_path=output_path,
            start_time=start_time,
            end_time=end_time,
            fps=fps,
            width=width
        )

        try:

            result: subprocess.CompletedProcess = subprocess.run(
                command,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL
            )

        except FileNotFoundError as error:
            raise GIFConversionError(
                "FFmpeg executable could not be found."
            ) from error

        if result.returncode != 0:
            raise GIFConversionError(
                f"Invalid-return-code-detected (code {result.returncode}): "
                f"{result.stderr}"
            )

        return
    