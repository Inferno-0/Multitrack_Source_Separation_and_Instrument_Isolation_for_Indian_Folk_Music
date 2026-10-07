"""
Utilities for generating, validating, and managing experiment paths.

This module centralizes all filesystem locations used throughout the
IKS Internship research repository.
"""

from pathlib import Path
from typing import Iterable, List, Union


class ExperimentPaths:
    """
    Manages filesystem paths for an experiment.

    Parameters
    ----------
    project_root : Path | str
        Absolute path to the repository root.

    dataset_name : str
        Dataset / Folk Tradition name.

    experiment_id : str
        Experiment identifier.

    model_name : str
        Source separation model name.
    """

    def __init__(
        self,
        project_root: Union[str, Path],
        dataset_name: str,
        experiment_id: str,
        model_name: str,
    ) -> None:

        self.project_root = Path(project_root).resolve()
        self.dataset_name = dataset_name.upper()
        self.experiment_id = experiment_id.upper()
        self.model_name = model_name

    # ======================================================================
    # Dataset Paths
    # ======================================================================

    @property
    def dataset_dir(self) -> Path:
        return self.project_root / "03_Datasets" / self.dataset_name

    @property
    def audio_dir(self) -> Path:
        return self.dataset_dir / "Audio"

    @property
    def wav_dir(self) -> Path:
        return self.audio_dir / "WAV"

    @property
    def metadata_dir(self) -> Path:
        return self.dataset_dir / "Metadata"

    @property
    def knowledge_dir(self) -> Path:
        return self.project_root / "02_Knowledge"

    @property
    def input_audio_dir(self) -> Path:
        """Alias kept for readability inside notebooks."""
        return self.wav_dir

    # ======================================================================
    # Experiment Paths
    # ======================================================================

    @property
    def experiments_root(self) -> Path:
        return (
            self.project_root
            / "05_Experiments"
            / "Baseline_HT_Demucs"
        )

    @property
    def experiment_dir(self) -> Path:
        return self.experiments_root / self.experiment_id

    # ======================================================================
    # Experiment Output Folders
    # ======================================================================

    @property
    def outputs_dir(self) -> Path:
        return self.experiment_dir / "outputs"

    @property
    def logs_dir(self) -> Path:
        return self.experiment_dir / "logs"

    @property
    def notebook_dir(self) -> Path:
        return self.experiment_dir / "notebook"

    # ======================================================================
    # Helper Methods
    # ======================================================================

    def get_input_file(self, recording_name: str) -> Path:
        return self.input_audio_dir / recording_name

    def get_output_directory(self, recording_name: str) -> Path:
        stem = Path(recording_name).stem
        return self.outputs_dir / stem

    def get_log_file(self) -> Path:
        return (
            self.logs_dir
            / f"{self.experiment_id}_execution_log.txt"
        )

    # ======================================================================
    # Validation
    # ======================================================================

    def validate_inputs(self) -> None:

        required = {
            "Project Root": self.project_root,
            "Dataset": self.dataset_dir,
            "Audio": self.input_audio_dir,
        }

        for name, path in required.items():

            if not path.exists():
                raise FileNotFoundError(
                    f"{name} directory does not exist:\n{path}"
                )

    def validate_recordings(
        self,
        recordings: Iterable[str],
    ) -> List[Path]:

        missing = []
        files = []

        for recording in recordings:

            file = self.get_input_file(recording)

            if file.exists():
                files.append(file)
            else:
                missing.append(recording)

        if missing:

            raise FileNotFoundError(
                "The following recordings were not found:\n"
                + "\n".join(missing)
            )

        return files

    # ======================================================================
    # Directory Creation
    # ======================================================================

    def create_output_folders(self) -> None:

        folders = [
            self.outputs_dir,
            self.logs_dir,
            self.notebook_dir,
        ]

        for folder in folders:
            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ======================================================================
    # Summary
    # ======================================================================

    def summary(self) -> None:

        print("=" * 70)
        print("Experiment Paths")
        print("=" * 70)

        print(f"Project Root : {self.project_root}")
        print(f"Dataset      : {self.dataset_name}")
        print(f"Experiment   : {self.experiment_id}")
        print(f"Model        : {self.model_name}")
        print()

        print(f"Input Audio  : {self.input_audio_dir}")
        print(f"Outputs      : {self.outputs_dir}")
        print(f"Logs         : {self.logs_dir}")
        print(f"Notebook     : {self.notebook_dir}")

        print("=" * 70)