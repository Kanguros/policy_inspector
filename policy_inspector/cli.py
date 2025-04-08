import logging
from pathlib import Path
from typing import TypeVar

import rich_click as click
from click import ClickException
from rich_click import UsageError, rich_config

from policy_inspector.loader import Loader, ModelClass
from policy_inspector.model.address_group import AddressGroup
from policy_inspector.model.address_object import AddressObject
from policy_inspector.model.base import MainModel
from policy_inspector.model.security_rule import SecurityRule
from policy_inspector.scenario import Scenario
from policy_inspector.scenario.shadowing import Shadowing
from policy_inspector.scenario.shadowing_by_value import ShadowingByValue
from policy_inspector.utils import (
    Example,
    ExampleChoice,
    FilePath,
    config_logger,
    exclude_check_option,
    verbose_option,
)

logger = logging.getLogger()
config_logger(logger)
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.TEXT_MARKUP = "markdown"
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_METAVARS_COLUMN = True

ConcreteScenario = TypeVar("ConcreteScenario", bound="Scenario")


@click.group(no_args_is_help=True, add_help_option=True)
@verbose_option(logger)
def main():
    """*PINS*
    as Policy Inspector
    """


@main.command("list")
@verbose_option(logger)
def main_list() -> None:
    """List available Scenarios."""
    logger.info("↺ Available Scenarios:")
    for scenario in Scenario.get_available().values():
        logger.info(f"→ '{scenario.name}'")
        logger.debug(f"\t{scenario.__doc__}")
        for check in scenario.checks:
            logger.debug(f"  - {check.__name__}")


@main.group("run", no_args_is_help=True)
@verbose_option(logger)
@rich_config(
    help_config={
        "style_argument": "bold yellow",
        "commands_panel_title": "Scenarios",
    }
)
def main_run():
    """Execute a Scenario.


    To see how it works, run one of the examples


    ```
    pins run example

    ```

    """


@main_run.command("shadowing", no_args_is_help=True)
@verbose_option(logger)
@click.argument(
    "security_rules_path",
    required=True,
    type=FilePath(),
)
@exclude_check_option()
def run_shadowing(
    security_rules_path: Path, exclude_checks: tuple[str]
) -> None:
    process_scenario(
        Shadowing,
        exclude_checks,
        (SecurityRule, security_rules_path),
    )


@main_run.command("shadowingvalue", no_args_is_help=True)
@verbose_option(logger)
@click.argument(
    "security_rules_path",
    required=True,
    type=FilePath(),
)
@click.argument(
    "address_objects_path",
    required=True,
    type=FilePath(),
)
@click.argument(
    "address_groups_path",
    required=True,
    type=FilePath(),
)
@exclude_check_option()
def run_shadowingvalue(
    security_rules_path: Path,
        address_objects_path: Path,
    address_groups_path: Path,

    exclude_checks: tuple[str],
) -> None:
    process_scenario(
        ShadowingByValue,
        exclude_checks,
        (SecurityRule, security_rules_path),

        (AddressObject, address_objects_path),
        (AddressGroup, address_groups_path)
    )



examples = [
    Example(
        name="1",
        args=[Path("1/policies.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="2",
        args=[Path("2/policies.json")],
        cmd=run_shadowing,
    ),
    Example(
        name="3",
        args=[
            Path("1/policies.json"),
            Path("1/address_objects.json"),
Path("1/address_groups.json"),
        ],
        cmd=run_shadowingvalue,
    ),
    Example(
        name="4",
        args=[
            Path("2/policies.json"),
            Path("2/address_objects.json"),
            Path("2/address_groups.json"),
        ],
        cmd=run_shadowingvalue,
    ),
]


@main_run.command("example", no_args_is_help=True)
@verbose_option(logger)
@exclude_check_option()
@click.argument(
    "example",
    type=ExampleChoice(examples),
)
@click.pass_context
def run_example(ctx, example: Example, exclude_checks: tuple[str]) -> None:
    """Run one of the examples."""
    logger.info(f"▶ Selected example: '{example.name}'")
    ctx.invoke(
        example.cmd.callback, *example.args, exclude_checks=exclude_checks
    )


def process_scenario(
    scenario: type[ConcreteScenario],
    exclude_checks: tuple[str],
    *cls_path: tuple[type[MainModel], Path],
    **kwargs,
):
    try:
        models_data = []
        for model_cls, file_path in cls_path:
            logger.info(f"↺ Loading {model_cls.plural} from {file_path.name}")
            instances = Loader.load_model(model_cls, file_path)
            logger.info(f"✓ Loaded {len(instances)} {model_cls.plural} successfully")
            models_data.append(instances)

        logger.info(f"↺ Preparing '{scenario.name}' scenario")
        scenario = scenario(*models_data, **kwargs)
        scenario.exclude_checks(exclude_checks)
        logger.info(f"→ Executing scenario with {len(scenario.checks)} checks")
        output = scenario.execute()
        logger.info("")
        logger.info("▶ Results")
        logger.info("―――――――――")
        scenario.analyze(output)
    except Exception as ex:  # noqa: BLE001
        raise ClickException(f"{str(ex)}\n{ex.args}\n{ex.__cause__}")  # noqa: B904


if __name__ == "__main__":
    main()
