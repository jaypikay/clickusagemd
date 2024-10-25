# Click Usage Markdown Generator

## Installation

Add `clickusagemd` as development dependency to your Poetry project.

```sh
poetry add -D git+ssh://git@github.com/jaypikay/clickusagemd.git
```

By adding a revision tag you can stay on a — at least for you — working version, instead of working with the latest and
possible broken commit.

The latest recommended revision is: **0.6.2**.

**To install:**

```sh
poetry add -D git+ssh://git@github.com/jaypikay/clickusagemd.git@0.6.2
```

After installing, register the _pre-push_ hook.
The hook is installed by executing the command `poetry run clickusagemd install`.
If an previous, untagged version of the _pre-push_ hook was installed you might need to manually delete the file `.git/hooks/pre-push` before installing.
Later versions of _clickusagemd_ will detect its own _pre-hook_ files and will install or update them.

## Updating

To update _clickusagemd_ either run

```sh
poetry update clickusagemd
```

with , or to update all _Poetry_ dependencies at once

```sh
poetry update
```

## Usage

See [USAGE.md](USAGE.md).

## Uninstall

_Clickusagemd_ can be uninstalled by removing the _pre-push_ hook with

```sh
poetry run clickusagemd uninstall
```

or by manually deleting the file `.git/hooks/pre-push`.

To completely remove the `clickusagemd` command use the _Poetry_ package manager to remove the dependency.

```sh
poetry remove -D clickusagemd
```
