#!/usr/bin/env python3

import importlib
import os
from typing import Iterator

import click
import git
import semver
import toml

from clickusagelib.githook import install_hook, uninstall_hook


def find_git_root(path) -> str:
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


def get_git_repo(path: str) -> git.Repo:
    return git.Repo(path)


def get_latest_version_tag(project_path: str) -> str:
    root = find_git_root(project_path)
    repo = get_git_repo(root)
    for tag in reversed(repo.tags):
        try:
            ver = semver.Version.parse(tag.name.replace("v", ""))
        except ValueError:
            continue
        finally:
            return ver
    print("No suitable version tag found.")
    return "0.0.0"


def iter_commands(
    module_name: str,
    cmd_chain: list,
    cliobj: click.Group | click.Command,
    depth: int = 1,
) -> Iterator[str]:
    assert isinstance(cliobj, click.Command) or isinstance(cliobj, click.Group)

    if isinstance(cliobj, click.Group):
        if depth > 1:
            yield f"{'#'*depth} {cliobj.name}"

        for name in sorted(cliobj.commands):
            yield from iter_commands(
                module_name, cmd_chain + [name], cliobj.commands[name], depth=depth + 1
            )
    else:
        ctx = click.get_current_context()
        cmd = f"{module_name} {' '.join(cmd_chain)}"
        help_message = cliobj.get_help(ctx).replace(ctx.command_path, cmd)

        if cliobj.name == "cli":
            cmd_title = "Default Command Line"
        else:
            cmd_title = cliobj.name

        yield f"{'#'*(depth)} {cmd_title}\n```\n{help_message}\n```"


def generate_usage_md(script: str, version: str):
    assert ":" in script
    module, cliobj = script.split(":")
    if "." in module:
        module_name = module.split(".")[0]
    else:
        module_name = module

    mod = importlib.import_module(module)
    cli = getattr(mod, cliobj)

    with open("USAGE.md", "w") as fd:
        print(
            f"# {module_name.capitalize()} v{version} - Command Usage Overview", file=fd
        )
        for command in iter_commands(module_name, [], cli):
            print(command, file=fd)


@click.group()
def cli():
    pass


@cli.command(help="Generate markdown usage description.")
@click.argument(
    "poetry_project_file",
    type=click.File(),
    default=os.path.join(find_git_root(os.getcwd()), "pyproject.toml"),
)
@click.pass_context
def run(ctx, poetry_project_file):
    click.echo("Generating USAGE.md...")
    latest_verstion = get_latest_version_tag(os.path.abspath(poetry_project_file.name))
    click.echo(f" - Latest Version: {latest_verstion}")
    contents = toml.loads(poetry_project_file.read())
    try:
        scripts = contents["tool"]["poetry"]["scripts"]
        for script in scripts.values():
            generate_usage_md(script, latest_verstion)
    except KeyError:
        click.echo("[ERROR] File does not contain 'tool.poetry.scripts' definitions.")
        ctx.exit(1)


@cli.command(help="Install clickusagemd as pre-push hook.")
def install():
    install_hook(find_git_root(os.getcwd()))


@cli.command(help="Uninstall clickusagemd pre-push hook.")
def uninstall():
    uninstall_hook(find_git_root(os.getcwd()))


cli.add_command(run)
cli.add_command(install)
cli.add_command(uninstall)


if __name__ == "__main__":
    cli()
