from pathlib import Path

from trading.sdlc_agents import (
    ReleaseAgent,
    RequirementsAgent,
    SyntaxAgent,
)


def test_syntax_agent():

    result = SyntaxAgent(
        Path(".")
    ).run()

    assert result.success


def test_requirements_agent():

    result = RequirementsAgent(
        Path(".")
    ).run()

    assert result.success


def test_release_agent():

    result = ReleaseAgent(
        Path(".")
    ).run()

    assert result.success