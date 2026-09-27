from pathlib import Path
import sys

ROOT = Path(
    __file__
).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "src"),
)

from trading.sdlc_agents import (
    SDLCPipeline,
)


def main():

    pipeline = SDLCPipeline()

    results = pipeline.run()

    print()
    print("=" * 70)
    print("              SDLC AUTOMATION PIPELINE")
    print("=" * 70)

    for result in results:

        status = (
            "PASS"
            if result.success
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{result.name}"
        )

        if not result.success:
            print(
                result.message
            )

    print()

    if pipeline.successful(results):

        print(
            "RELEASE STATUS: READY"
        )

    else:

        print(
            "RELEASE STATUS: BLOCKED"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()