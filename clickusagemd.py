#!/usr/bin/env python3

import importlib
import os
from collections.abc import Iterator
from io import StringIO, TextIOWrapper

import click
import git
import toml

from clickusagelib.githook import install_hook, uninstall_hook


def find_git_root(path) -> str:
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


def get_git_repo(path: str) -> git.Repo:
    return git.Repo(path)


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


def write_usage_md(script: str, version: str):
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


def generate_usage_md(script: str, version: str) -> str:
    assert ":" in script

    module, cliobj = script.split(":")
    if "." in module:
        module_name = module.split(".")[0]
    else:
        module_name = module

    mod = importlib.import_module(module)
    script_cli = getattr(mod, cliobj)

    usage_md = StringIO()
    usage_md.write(
        f"# {module_name.capitalize()} v{version} - Command Usage Overview\n\n"
    )
    for sub_command in iter_commands(module_name, [], script_cli):
        usage_md.write(sub_command)
        usage_md.write("\n\n")

    usage_md.seek(0)
    return usage_md.read()


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
def run(ctx: click.Context, poetry_project_file: TextIOWrapper):
    project_settings = toml.load(poetry_project_file)

    version = project_settings["tool"]["poetry"]["version"]
    scripts = project_settings["tool"]["poetry"]["scripts"]

    click.echo("Writing USAGE.md...")
    click.echo(f" - Version: {version}")

    usage_md_path = os.path.join(find_git_root(os.getcwd()), "USAGE.md")
    with open(usage_md_path, "wt", encoding="utf-8") as f:
        try:
            for script in scripts.values():
                f.write(generate_usage_md(script, version))
        except KeyError:
            click.echo(
                "[ERROR] File does not contain 'tool.poetry.scripts' definitions."
            )
            ctx.exit(1)


@click.command(help="Print markdown usage description'")
@click.argument(
    "poetry_project_file",
    type=click.File(),
    default=os.path.join(find_git_root(os.getcwd()), "pyproject.toml"),
)
@click.pass_context
def print(ctx: click.Context, poetry_project_file: TextIOWrapper):
    project_settings = toml.load(poetry_project_file)

    version = project_settings["tool"]["poetry"]["version"]
    scripts = project_settings["tool"]["poetry"]["scripts"]

    click.echo("Generating USAGE.md...", err=True)
    click.echo(f" - Version: {version}", err=True)
    try:
        for script in scripts.values():
            click.echo(generate_usage_md(script, version))
    except KeyError:
        click.echo("[ERROR] File does not contain 'tool.poetry.scripts' definitions.")
        ctx.exit(1)


@cli.command(help="Install clickusagemd as pre-commit hook.")
def install():
    install_hook(find_git_root(os.getcwd()))


@cli.command(help="Uninstall clickusagemd pre-commit hook.")
def uninstall():
    uninstall_hook(find_git_root(os.getcwd()))


cli.add_command(print)
cli.add_command(run)
cli.add_command(install)
cli.add_command(uninstall)

if __name__ == "__main__":
    cli()
