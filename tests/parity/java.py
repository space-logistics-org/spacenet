"""
Runs the reference (Java) implementation of SpaceNet in headless mode to
produce the outputs to which the Python implementation is compared.

The reference implementation is only required to (re)generate the parity
fixtures, not to run the tests. Its location is configured with environment
variables:

* ``SPACENET_JAVA_REPO``: clone of https://github.com/space-logistics-org/spacenet
  (default: ``../spacenet`` relative to this repository)
* ``JAVA_HOME``: Java 8 development kit (default: ``java`` on the path)
* ``MAVEN``: Maven executable (default: ``mvn`` on the path)
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[2]

#: Headless modes of the reference implementation.
MODES = ("demands-raw", "demands-agg", "auto-manifest")


class JavaReference:
    """The reference implementation, compiled from its source."""

    def __init__(self, repo: Optional[Path] = None):
        self.repo = Path(
            repo or os.environ.get("SPACENET_JAVA_REPO", ROOT.parent / "spacenet")
        ).resolve()
        if not (self.repo / "pom.xml").exists():
            raise FileNotFoundError(f"No reference implementation at {self.repo}")
        home = os.environ.get("JAVA_HOME")
        self.java = str(Path(home) / "bin" / "java") if home else "java"
        self.maven = os.environ.get("MAVEN") or shutil.which("mvn") or "mvn"
        self._classpath: Optional[str] = None

    @property
    def commit(self) -> str:
        """The commit of the reference implementation."""
        return subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def compile(self):
        """Compiles the reference implementation and resolves its classpath."""
        pom = str(self.repo / "pom.xml")
        subprocess.run([self.maven, "-B", "-q", "-f", pom, "compile"], check=True)
        output = self.repo / "target" / "parity-classpath.txt"
        subprocess.run(
            [
                self.maven,
                "-B",
                "-q",
                "-f",
                pom,
                "dependency:build-classpath",
                f"-Dmdep.outputFile={output}",
            ],
            check=True,
        )
        classes = self.repo / "target" / "classes"
        self._classpath = os.pathsep.join(
            [str(classes), output.read_text(encoding="utf-8").strip()]
        )

    def run(self, mode: str, scenario: Path, output: Path, consume: bool = False):
        """
        Runs a headless mode on a scenario file.

        Args:
            mode (str): The headless mode (see :data:`MODES`).
            scenario (Path): The scenario file (JSON).
            output (Path): The output file (JSON).
            consume (bool): True, to satisfy demands with existing resources.
        """
        if self._classpath is None:
            self.compile()
        command: List[str] = [
            self.java,
            "-Djava.awt.headless=true",
            "-cp",
            self._classpath,
            "edu.mit.spacenet.SpaceNet",
            "-h",
            mode,
            "-i",
            str(scenario),
            "-o",
            str(output),
            "-y",
        ]
        if consume:
            command.append("-c")
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=600, check=False
        )
        if result.returncode != 0 or not output.exists():
            raise RuntimeError(
                f"Reference implementation failed ({mode}, {scenario}): "
                f"{result.stderr[-2000:]}"
            )
