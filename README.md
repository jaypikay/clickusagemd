# Click Usage Markdown Generator

## Installation

Add `clickusagemd` as development dependency to your Poetry project.

```sh
uv tool add -D git+ssh://git@github.com/jaypikay/clickusagemd.git
```

By adding a revision tag you can stay on a — at least for you — working version, instead of working with the latest and
possible broken commit.

**To install:**

```sh
uv tool add -D git+ssh://git@github.com/jaypikay/clickusagemd.git@<RELEASE_TAG>
```

After installing, register the _pre-push_ hook.
The hook is installed by executing the command `uv run clickusagemd install`.
If an previous, untagged version of the _pre-push_ hook was installed you might need to manually delete the file `.git/hooks/pre-push` before installing.
Later versions of _clickusagemd_ will detect its own _pre-hook_ files and will install or update them.

## Updating

To update _clickusagemd_ either run

```sh
uv tool upgrade clickusagemd
```

## Usage

See [USAGE.md](USAGE.md).

## Uninstall

_Clickusagemd_ can be uninstalled by removing the _pre-push_ hook with

```sh
uv run clickusagemd uninstall
```

or by manually deleting the file `.git/hooks/pre-push`.

To completely remove the `clickusagemd` command use the _uv_ package manager to remove the dependency.

```sh
uv remove --dev clickusagemd
```
