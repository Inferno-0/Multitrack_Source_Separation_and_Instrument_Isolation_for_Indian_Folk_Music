"""
Utilities for logging experiment executions.

This module provides reusable functionality for saving experiment
execution metadata in a consistent JSON format. Every experiment should
record its execution details to improve reproducibility and simplify
future analysis.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


def write_execution_log(
    execution_info: Dict[str, Any],
    output_path: Union[str, Path],
    append: bool = False,
) -> Path:
    """
    Save experiment execution metadata as a JSON file.

    Parameters
    ----------
    execution_info : dict
        Dictionary containing execution metadata.

    output_path : str | Path
        Destination JSON file.

    append : bool, default=False
        If False:
            Overwrites the existing log.

        If True:
            Appends the execution to a JSON list.

    Returns
    -------
    Path
        Path to the saved log file.

    Raises
    ------
    IOError
        If writing fails.
    """

    path = Path(output_path)

    path.parent.mkdir(parents=True, exist_ok=True)

    execution_info = dict(execution_info)

    execution_info.setdefault(
        "log_created",
        datetime.now().isoformat(timespec="seconds"),
    )

    try:

        if append and path.exists():

            with open(path, "r", encoding="utf-8") as f:

                existing = json.load(f)

            if not isinstance(existing, list):
                existing = [existing]

            existing.append(execution_info)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    existing,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

        else:

            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    execution_info,
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

    except Exception as exc:
        raise IOError(
            f"Unable to write execution log:\n{path}"
        ) from exc

    return path


def create_execution_info(
    *,
    experiment_id: str,
    experiment_name: str,
    dataset_name: str,
    model_name: str,
    command: str,
    start_time: datetime,
    end_time: datetime,
    status: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized execution metadata dictionary.

    Parameters
    ----------
    experiment_id : str
    experiment_name : str
    dataset_name : str
    model_name : str
    command : str
    start_time : datetime
    end_time : datetime
    status : str
    extra : dict, optional

    Returns
    -------
    dict
    """

    duration = (end_time - start_time).total_seconds()

    info = {
        "experiment_id": experiment_id,
        "experiment_name": experiment_name,
        "dataset_name": dataset_name,
        "model_name": model_name,
        "command": command,
        "status": status,
        "start_time": start_time.isoformat(timespec="seconds"),
        "end_time": end_time.isoformat(timespec="seconds"),
        "duration_seconds": round(duration, 3),
    }

    if extra:
        info.update(extra)

    return info


def print_execution_summary(
    execution_info: Dict[str, Any],
) -> None:
    """
    Print a formatted execution summary.
    """

    print("=" * 70)
    print("Execution Summary")
    print("=" * 70)

    for key, value in execution_info.items():
        print(f"{key:<22}: {value}")

    print("=" * 70)