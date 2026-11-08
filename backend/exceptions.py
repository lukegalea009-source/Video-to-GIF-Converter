class VideoMetadataError(Exception):
    """Base exception for video metadata features."""


class FFprobeNotFoundError(VideoMetadataError):
    """Raised when the FFprobe executable cannot be found."""


class InvalidVideoError(VideoMetadataError):
    """Raised when the video cannot be inspected or parsed."""