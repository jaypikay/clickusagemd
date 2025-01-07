from pathlib import Path

PRE_COMMIT_SCRIPT = """#!/usr/bin/env bash
#:clickusagemd:

set -e

poetry run clickusagemd run pyproject.toml
if ! git diff --quiet USAGE.md; then
    echo " - USAGE.md was updated"
    git add USAGE.md && git commit --amend --no-edit
fi

exit 0
"""


def is_gitdir(func):
    def path_check(*args, **kwargs) -> bool:  # dead: disable
        path = Path(args[0] or "./") / ".git/hooks"
        if path.exists():
            return func(path)
        else:
            return False

    return path_check


def is_clickusagemd_hook(path: Path) -> bool:
    githook = path / "pre-commit"
    if githook.exists():
        with githook.open("rt") as fd:
            file_contents = fd.read()
            if ":clickusagemd:" in file_contents:
                return True
    return False


@is_gitdir
def install_hook(path: Path) -> bool:
    githook = path / "pre-commit"
    if not githook.exists() or is_clickusagemd_hook(path):
        with githook.open("wt") as fd:
            fd.write(PRE_COMMIT_SCRIPT)
            githook.chmod(0o755)
            print(f"Hook installed as `{githook}'.")
            return True
    else:
        print(f"A hook is already installed as `{githook}'. Installation aborted.\n")
        print(
            "To manually install the hook add the command logic to the script '.git/hooks/pre-commit':\n"
        )
        print(PRE_COMMIT_SCRIPT)
    return False


@is_gitdir
def uninstall_hook(path: Path) -> bool:
    githook = path / "pre-commit"
    if githook.exists() and is_clickusagemd_hook(path):
        githook.unlink()
        print(f"Hook `{githook}' uninstalled.")
        return True
    else:
        print(f"The `{githook}' file was not uninstalled.")

    return False
