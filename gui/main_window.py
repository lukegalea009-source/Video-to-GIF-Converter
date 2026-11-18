from pathlib import Path
import math

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
    QFileDialog,
    QMessageBox,
    QDoubleSpinBox,
    QSpinBox,
)

from PyQt6.QtMultimedia import (
    QMediaPlayer,
)

from PyQt6.QtMultimediaWidgets import (
    QVideoWidget,
)

from PyQt6.QtCore import (
    QUrl,
    Qt
)

from backend.video_info import inspect_video
from backend.exceptions import VideoMetadataError
from backend.validators import (
    validate_clip_times,
    validate_gif_settings,
    validate_conversion_paths
)
from backend.converter import VidToGIFConverter


# Allowed extensions
SUPPORTED_VIDEO_EXTENSIONS: set[str] = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi"
}


class MainWindow(QMainWindow):
    """Defines/Structures/Connects the backend to a GUI interface."""


    def __init__(self) -> None:
        super().__init__()

        # Setting window title
        self.setWindowTitle("VIDEO-TO-GIF-CONVERTER")

        # Setting window dimensions
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        # Defining the application central widget
        self.central_widget: QWidget = QWidget()
        self.setCentralWidget(self.central_widget)


        # === Structuring the application layout ===

        # Application is structured primarly using a verival layout
        self.main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        # Content layout -> left_side=media_viewer, right_side=GIF_controls
        self.content_layout: QHBoxLayout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Content widgets
        self.viewer_container: QWidget = QWidget()
        self.controls_container: QWidget = QWidget()

        self.content_layout.addWidget(self.viewer_container, stretch=3)
        self.content_layout.addWidget(self.controls_container, stretch=2)


        # === Viewer_container widgets ===
        self.viewer_layout: QVBoxLayout = QVBoxLayout(self.viewer_container)

        self.media_player: QMediaPlayer = QMediaPlayer(self)
        self.video_widget: QVideoWidget = QVideoWidget()

        self.media_player.setVideoOutput(self.video_widget)
        
        # Set default video info value and default input/output paths
        self.video_info: dict | None = None
        self.input_path: str | None = None
        self.output_path: str | None = None

        # Input file select button
        self.select_video_button: QPushButton = QPushButton("Select Video")

        self.viewer_layout.addWidget(self.select_video_button)
        self.viewer_layout.addWidget(self.video_widget)

        # Play/Pause button for viewer layout
        self.play_button: QPushButton = QPushButton()
        self.play_button.setText("Play")

        self.viewer_layout.addWidget(self.play_button)

        # Viewer controls
        self.timeline_slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setRange(0, 0)

        self.position_label: QLabel = QLabel("00:00")
        self.duration_label: QLabel = QLabel("00:00")

        self.timeline_controls: QHBoxLayout = QHBoxLayout()

        self.timeline_controls.addWidget(self.position_label)
        self.timeline_controls.addWidget(self.timeline_slider)
        self.timeline_controls.addWidget(self.duration_label)

        self.viewer_layout.addLayout(self.timeline_controls)

        # Video info labels
        self.video_duration_label: QLabel = QLabel()
        self.video_duration_label.setText("Duration: N/A")

        self.video_resolution_label: QLabel = QLabel()
        self.video_resolution_label.setText("Resolution: N/A")

        self.video_codec_label: QLabel = QLabel()
        self.video_codec_label.setText("Codec: N/A")

        self.video_info_labels: QHBoxLayout = QHBoxLayout()
        self.video_info_labels.addWidget(self.video_duration_label)
        self.video_info_labels.addWidget(self.video_resolution_label)
        self.video_info_labels.addWidget(self.video_codec_label)

        self.viewer_layout.addLayout(self.video_info_labels)


        # === Control container widgets ===
        self.controls_layout: QVBoxLayout = QVBoxLayout(self.controls_container)

        self.start_time_label: QLabel = QLabel("Start time")

        self.start_time_spinbox: QDoubleSpinBox = QDoubleSpinBox()
        self.start_time_spinbox.setValue(0.0)
        self.start_time_spinbox.setRange(0.0, 0.0)
        self.start_time_spinbox.setSuffix(" s")
        self.start_time_spinbox.setDecimals(1)
        self.start_time_spinbox.setSingleStep(0.1)

        self.control_duration_label: QLabel = QLabel("Clip Duration")

        self.duration_spinbox: QDoubleSpinBox = QDoubleSpinBox()
        self.duration_spinbox.setValue(5.0)
        self.duration_spinbox.setRange(0.1, 15.0)
        self.duration_spinbox.setSuffix(" s")
        self.duration_spinbox.setDecimals(1)
        self.duration_spinbox.setSingleStep(0.1)

        self.duration_slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setValue(50)
        self.duration_slider.setRange(1, 150)

        self.end_time_label: QLabel = QLabel("End time: 5.0 s")

        # Children layouts
        self.start_time_controls: QHBoxLayout = QHBoxLayout()
        self.start_time_controls.addWidget(self.start_time_label)
        self.start_time_controls.addWidget(self.start_time_spinbox)

        self.duration_controls: QHBoxLayout = QHBoxLayout()
        self.duration_controls.addWidget(self.control_duration_label)
        self.duration_controls.addWidget(self.duration_spinbox)

        self.controls_layout.addLayout(self.start_time_controls)
        self.controls_layout.addLayout(self.duration_controls)
        self.controls_layout.addWidget(self.duration_slider)
        self.controls_layout.addWidget(self.end_time_label)

        # FPS and Width controls
        self.gif_settings_layout: QHBoxLayout = QHBoxLayout()

        self.fps_label: QLabel = QLabel("FPS:")

        self.fps_spinbox: QSpinBox = QSpinBox()
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(15)
        self.fps_spinbox.setSuffix(" FPS")

        self.width_label: QLabel = QLabel("Width:")

        self.width_spinbox: QSpinBox = QSpinBox()
        self.width_spinbox.setRange(2, 1920)
        self.width_spinbox.setValue(480)
        self.width_spinbox.setSingleStep(2)
        self.width_spinbox.setSuffix(" px")

        self.gif_settings_layout.addWidget(self.fps_label)
        self.gif_settings_layout.addWidget(self.fps_spinbox)
        self.gif_settings_layout.addWidget(self.width_label)
        self.gif_settings_layout.addWidget(self.width_spinbox)

        self.output_path_label: QLabel = QLabel("No output selected")
        self.select_output_button: QPushButton = QPushButton("Select Output")

        self.controls_layout.addLayout(self.gif_settings_layout)
        self.controls_layout.addWidget(self.select_output_button)
        self.controls_layout.addWidget(self.output_path_label)

        # Convert button
        self.convert_button: QPushButton = QPushButton("Convert to GIF")
        self.convert_button.setEnabled(False)

        self.controls_layout.addWidget(self.convert_button)

        # === Signal Handling ===
        self.play_button.clicked.connect(
            self.toggle_playback
        )

        self.media_player.playbackStateChanged.connect(
            self.update_play_button_state
        )

        self.media_player.positionChanged.connect(
            self.timeline_slider.setValue
        )

        self.media_player.positionChanged.connect(
            self.update_position_label
        )

        self.media_player.durationChanged.connect(
            self.timeline_slider.setMaximum
        )

        self.media_player.durationChanged.connect(
            self.update_duration_label
        )

        self.timeline_slider.sliderMoved.connect(
            self.media_player.setPosition
        )

        self.select_video_button.clicked.connect(
            self.select_video
        )

        self.duration_slider.valueChanged.connect(
            self.update_duration_from_slider
        )

        self.duration_spinbox.valueChanged.connect(
            self.update_slider_from_duration
        )

        self.duration_spinbox.valueChanged.connect(
            self.update_end_time
        )

        self.start_time_spinbox.valueChanged.connect(
            self.update_end_time
        )

        self.start_time_spinbox.valueChanged.connect(
            self.update_available_duration
        )

        self.fps_spinbox.valueChanged.connect(
            self.update_convert_button_state
        )

        self.width_spinbox.valueChanged.connect(
            self.update_convert_button_state
        )

        self.select_output_button.clicked.connect(
            self.select_output_path
        )

        self.convert_button.clicked.connect(
            self.prepare_conversion
        )



        # === TEMPORARY AREA ===

        # Display layout temporarily
        # self.controls_container.setStyleSheet(
        #     "background-color: #56f5e2;"
        # )

        # self.video_widget.setStyleSheet(
        #     "background-color: #20242e;"
        # )


    @staticmethod
    def format_timestamp(milliseconds: int) -> str:
        """Returns a formatted timestamp for duration and position labels."""

        total_seconds: int = milliseconds // 1000

        minutes: int = total_seconds // 60
        seconds: int = total_seconds % 60

        timestamp = f"{minutes:02d}:{seconds:02d}"

        return timestamp


    # Controls the play button
    def update_play_button_state(self, state: QMediaPlayer.PlaybackState) -> None:
        """Modifies the text on the play button."""

        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("Pause")

        else:
            self.play_button.setText("Play")
    

    def toggle_playback(self) -> None:

        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
            

    # Updates viewer control labels
    def update_position_label(self, position: int) -> None:
        timestamp = self.format_timestamp(position)
        self.position_label.setText(timestamp)


    def update_duration_label(self, duration: int) -> None:
        timestamp = self.format_timestamp(duration)
        self.duration_label.setText(timestamp)


    # Selecting a video
    def select_video(self) -> None:
        """Opens a file dialouge to select an appropriate file."""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Video",
            "",
            "Video Files (*.mp4 *.mov *.mkv *.avi);;All Files (*)"
        )

        if not file_path:
            return

        extension = Path(file_path).suffix.lower()

        if extension not in SUPPORTED_VIDEO_EXTENSIONS:
            QMessageBox.warning(
                self,
                "Invalid Input Extension",
                f"An unsupported input extension was detected!\nValid extensions: {", ".join(sorted(SUPPORTED_VIDEO_EXTENSIONS))}"
            )
            return

        # Inspect the selected video
        try:
            metadata = inspect_video(file_path)

        except VideoMetadataError as error:
            QMessageBox.warning(
                self,
                "Video Inspection Failed",
                str(error)
            )
            return

        self.video_info = metadata
        self.input_path = file_path

        self.configure_clip_duration()

        # Update video info labels
        self.video_duration_label.setText(
            f"Duration: {str(round(self.video_info["duration"], 2))}"
        )

        self.video_resolution_label.setText(
            f"Resolution: {self.video_info["width"]} x {self.video_info["height"]}"
        )

        self.video_codec_label.setText(
            f"Codec: {self.video_info["codec_name"]}"
        )

        # Display the selected video
        self.media_player.setSource(
            QUrl.fromLocalFile(file_path)
        )

        self.update_convert_button_state()
        return

        
    def update_duration_from_slider(self, slider_value: int) -> None:
        duration_value = slider_value / 10
        self.duration_spinbox.setValue(duration_value)


    def update_slider_from_duration(self, duration: float) -> None:
        duration_value = round(duration * 10)
        self.duration_slider.setValue(duration_value)


    def update_end_time(self) -> None:
        st, dur = self.start_time_spinbox.value(), self.duration_spinbox.value()
        summed = st + dur
        self.end_time_label.setText(f"End time: {summed:.1f}s")


    def configure_clip_duration(self) -> None:

        if self.video_info is None:
            return
        
        video_duration: float = self.video_info["duration"]

        total_tenths = math.floor(video_duration * 10)

        if total_tenths < 1:
            self.start_time_spinbox.setEnabled(False)
            self.duration_spinbox.setEnabled(False)
            self.duration_slider.setEnabled(False)
            self.end_time_label.setText("Clip too short")

            QMessageBox.warning(
                self,
                "Invalid Clip Duration",
                "The selected video is too short for GIF conversion (minimum 0.1 seconds)."
            )
            return

        self.start_time_spinbox.setEnabled(True)
        self.duration_spinbox.setEnabled(True)
        self.duration_slider.setEnabled(True)
        
        maximum_start = (total_tenths - 1) / 10

        self.start_time_spinbox.setValue(0.0)
        self.start_time_spinbox.setRange(0.0, maximum_start)

        self.update_available_duration()

        default_duration = min(
            5.0,
            self.duration_spinbox.maximum()
        )

        self.duration_spinbox.setValue(default_duration)


    def update_available_duration(self) -> None:
        """Update the allowed clip duration based on the start time."""

        if self.video_info is None:
            return

        video_duration: float = self.video_info["duration"]
        start_time: float = self.start_time_spinbox.value()

        remaining_time = video_duration - start_time

        maximum_tenths = min(
            150,
            math.floor(remaining_time * 10)
        )

        maximum_seconds = maximum_tenths / 10

        self.duration_spinbox.setMaximum(maximum_seconds)
        self.duration_slider.setMaximum(maximum_tenths)

        self.update_end_time()


    def update_convert_button_state(self) -> None:
        if (
            self.input_path is None
            or self.output_path is None
            or self.video_info is None
        ):
            self.convert_button.setEnabled(False)
            return

        if not validate_gif_settings(
            self.fps_spinbox.value(),
            self.width_spinbox.value()
        ):
            self.convert_button.setEnabled(False)
            return

        if not self.start_time_spinbox.isEnabled():
            self.convert_button.setEnabled(False)
            return

        self.convert_button.setEnabled(True)


    def select_output_path(self) -> None:
        """Determines the output path"""

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save GIF",
            "",
            "GIF Files (*.gif)"
        )

        if not output_path:
            return

        if Path(output_path).exists():
            QMessageBox.warning(
                self,
                "Duplicate File Path",
                "This file path is already being used by another file."
            )
            return

        if Path(output_path).suffix.lower() != ".gif":
            QMessageBox.warning(
                self,
                "Invalid Extension",
                "Your selected path has an invalid extension (valid extension: *.gif)."
            )
            return

        self.output_path = output_path
        self.output_path_label.setText(Path(output_path).name)
        self.update_convert_button_state()


    def prepare_conversion(self) -> None:

        if self.input_path is None or self.output_path is None or self.video_info is None:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Check whether valid input/output file paths have been selected."
            )
            return

        # Validate paths
        if not validate_conversion_paths(
            input_path=self.input_path,
            output_path=self.output_path
        ):
            QMessageBox.warning(
                self,
                "Invalid File Paths",
                "Check your selected input and output paths for mistakes."
            )
            return

        start_time = self.start_time_spinbox.value()
        duration = self.duration_spinbox.value()
        end_time = round(start_time + duration, 1)

        # Validate time settings
        if not validate_clip_times(
            start_time=start_time,
            end_time=end_time,
            video_duration=self.video_info["duration"]
        ):
            QMessageBox.warning(
                self,
                "Invalid Time Settings",
                "Your requested time values are incorrect\nRemember: (0 <= start_time < end_time <= total duration)."
            )
            return
        
        fps = self.fps_spinbox.value()
        width = self.width_spinbox.value()

        # Validate gif settings
        if not validate_gif_settings(
            fps=fps,
            width=width
        ):
            QMessageBox.warning(
                self,
                "Invalid GIF Settings",
                "Your requested FPS or Width are invalid (Width must be an even number)."
            )
            return

        command = VidToGIFConverter.build_ffmpeg_command(
            input_path=self.input_path,
            output_path=self.output_path,
            start_time=start_time,
            end_time=end_time,
            fps=fps,
            width=width
        )

        print("Prepared FFmpeg command:")
        print(command)

    


        

        
        



        
