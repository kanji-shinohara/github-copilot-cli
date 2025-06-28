#!/usr/bin/env python3
import sys

sys.path.append(".")

from github_copilot_cli.__main__ import github_copilot_cli  # noqa: E402


if __name__ == "__main__":
    sys.exit(github_copilot_cli())
