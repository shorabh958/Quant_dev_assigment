from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class AgentResult:
    name: str
    success: bool
    message: str


class SDLCAgent:

    name = "base"

    def run(self) -> AgentResult:
        raise NotImplementedError


class TestAgent(SDLCAgent):

    name = "test-agent"

    def run(self):

        result = subprocess.run(
            ["pytest", "-q"],
            capture_output=True,
            text=True,
        )

        success = result.returncode == 0

        output = (
            result.stdout.strip()
            if result.stdout
            else result.stderr.strip()
        )

        return AgentResult(
            name=self.name,
            success=success,
            message=output,
        )


class SyntaxAgent(SDLCAgent):

    name = "syntax-agent"

    def __init__(self, root=None):
        self.root = Path(
            root or "."
        )

    def run(self):

        src = self.root / "src"

        result = subprocess.run(
            [
                "python",
                "-m",
                "compileall",
                "-q",
                str(src),
            ],
            capture_output=True,
            text=True,
        )

        return AgentResult(
            name=self.name,
            success=result.returncode == 0,
            message=(
                "Python compilation successful"
                if result.returncode == 0
                else result.stderr
            ),
        )


class GitAgent(SDLCAgent):

    name = "git-agent"

    def run(self):

        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return AgentResult(
                self.name,
                False,
                result.stderr.strip(),
            )

        if result.stdout.strip():
            return AgentResult(
                self.name,
                False,
                "Working tree contains uncommitted changes:\n"
                + result.stdout.strip(),
            )

        return AgentResult(
            self.name,
            True,
            "Working tree clean",
        )


class RequirementsAgent(SDLCAgent):

    name = "requirements-agent"

    def __init__(self, root=None):
        self.root = Path(
            root or "."
        )

    def run(self):

        required = [
            self.root / "README.md",
            self.root / "pytest.ini",
            self.root / ".gitignore",
        ]

        missing = [
            str(path)
            for path in required
            if not path.exists()
        ]

        if missing:
            return AgentResult(
                self.name,
                False,
                "Missing files:\n"
                + "\n".join(missing),
            )

        return AgentResult(
            self.name,
            True,
            "Required project files present",
        )


class ReleaseAgent(SDLCAgent):

    name = "release-agent"

    def __init__(self, root=None):
        self.root = Path(
            root or "."
        )

    def run(self):

        required_directories = [
            self.root / "src",
            self.root / "tests",
            self.root / "scripts",
        ]

        missing = [
            str(path)
            for path in required_directories
            if not path.exists()
        ]

        if missing:
            return AgentResult(
                self.name,
                False,
                "Missing directories:\n"
                + "\n".join(missing),
            )

        return AgentResult(
            self.name,
            True,
            "Release structure validated",
        )


class SDLCPipeline:

    def __init__(
        self,
        agents=None,
    ):
        self.agents = agents or [
            SyntaxAgent(),
            TestAgent(),
            RequirementsAgent(),
            ReleaseAgent(),
            GitAgent(),
        ]

    def run(self):

        results = []

        for agent in self.agents:
            result = agent.run()
            results.append(result)

            if not result.success:
                break

        return results

    @staticmethod
    def successful(results):

        return all(
            result.success
            for result in results
        )