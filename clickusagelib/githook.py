from pathlib import Path

PRE_PUSH_SCRIPT = """#!/usr/bin/env bash
#:clickusagemd:

set -e

poetry run clickusagemd run pyproject.toml
if ! git diff --quiet USAGE.md; then
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
    githook = path / "pre-push"
    if githook.exists():
        with githook.open("rt") as fd:
            file_contents = fd.read()
            if ":clickusagemd:" in file_contents:
                return True
    return False


@is_gitdir
def install_hook(path: Path) -> bool:
    githook = path / "pre-push"
    if not githook.exists() or is_clickusagemd_hook(path):
        with githook.open("wt") as fd:
            fd.write(PRE_PUSH_SCRIPT)
            fd.close()
            githook.chmod(0o755)
            print(f"Hook installed as `{githook}'.")
            return True
    else:
        print(f"A hook is already installed as `{githook}'. Installation aborted.")
    return False


@is_gitdir
def uninstall_hook(path: Path) -> bool:
    githook = path / "pre-push"
    if githook.exists() and is_clickusagemd_hook(path):
        githook.unlink()
        print(f"Hook `{githook}' uninstalled.")
        return True
    else:
        print(f"The `{githook}' file was not uninstalled.")

    return False
