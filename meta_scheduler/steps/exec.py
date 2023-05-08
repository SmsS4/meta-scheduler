import datetime
import os
from dataclasses import dataclass

from temporalio import activity
from temporalio import workflow

from meta_scheduler import settings
from meta_scheduler.models import mql
from meta_scheduler.utils import command
from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

"""
Notes:
    when you write wine terminal64.exe /config:path_to_config
    path_to_config is should be like C://path_to_config
"""

NAME = stepping.get_name(__name__)

logger = get_logger(NAME)

Input = mql.Strategy

PATHS_TO_CLEAN = [
    "MQL5/Experts/",
    "MQL5/Files/",
    "MQL5/Logs/",
    "MQL5/Presets/",
    "logs/",
    "Tester/",
    "MQL5/Profiles/Tester/",
    "MQL5/report.xml",
    "MQL5/*.png",
    "MQL5/report.htm",
]

STRATEGY = "strategy"

CONFIG_PATH = os.path.join(settings.meta.path, "config.ini")
EX5_PATH = os.path.join(settings.meta.path, "MQL5", "Experts", f"{STRATEGY}.ex5")
TERMINAL_PATH = os.path.join(settings.meta.path, "terminal64.exe")


@activity.defn
async def clean():
    logger.info("Cleaning fodler")
    for folder in PATHS_TO_CLEAN:
        logger.info("Cleaning %s", folder)
        result = command.run(
            "rm",
            "-rf",
            os.path.join(settings.meta.path, folder + "*"),
            raise_on_error=True,
            stdin="y\n",
            shell=True,
        )
    logger.info("Clean done")


@activity.defn
async def write_config(strategy: mql.Strategy):
    logger.info("Writing config to set file at %s", CONFIG_PATH)

    with open(CONFIG_PATH, "w") as f:
        f.write(
            "\n".join(
                [
                    "[Common]",
                    f"Login={settings.meta.login_id}",
                    f"Password={settings.meta.password}",
                    f"Server={settings.meta.server}",
                    "[Experts]",
                    "AllowLiveTrading=0",
                    "AllowDllImport=0",
                    "Enabled=1",
                    "Account=0",
                    "Profile=0",
                    "[Tester]",
                    "ReplaceReport=1",
                    "ShutdownTerminal=1",
                    "ForwardMode=0",
                    f"Expert=strategy",  # remove .ex5
                    f"Symbol={strategy.symbol}",
                    f"Period={strategy.period}",
                    f"Deposit={strategy.deposit}",
                    f"Leverage={strategy.leverage}",
                    f"Model={strategy.model}",
                    f"ExecutionMode={strategy.execution_mode}",
                    f"Optimization={strategy.optimization}",
                    f"OptimizationCriterion={strategy.cost_function}",
                    f"FromDate={strategy.from_date}",
                    f"ToDate={strategy.to_date}",
                    "Report=MQL5\\report",
                    "[TesterInputs]\n",
                ]
            )
            + strategy.set_file
        )
    logger.info("Writing done")


@activity.defn
async def write_strategy(ex5: bytes):
    logger.info("Writing ex5 at %s", EX5_PATH)
    with open(EX5_PATH, "wb") as f:
        f.write(ex5)
    logger.info("Writing done")


@activity.defn
async def run_strategy(strategy: mql.Strategy):
    command.run("wine", f"{TERMINAL_PATH}", f"/config:C:\\meta\\config.ini /portable")


class FileType:
    XML = 1
    CACHE = 2
    CONFIG = 3
    AGENT_LOG = 4
    TESTER_LOG = 5
    MANAGER_LOG = 6
    TERMINAL_LOG = 7
    BACKTEST_RESULT = 8
    BACKTEST_IMAGES = 9


@dataclass(frozen=True, slots=True)
class File:
    path: str
    data: bytes
    type: int


def collect_file(path: str, file_type: int):
    with open(path, "rb") as f:
        return File(path=path, data=f.read(), type=file_type)


def get_file_in_folder(path: str) -> str:
    files = os.listdir(path)
    if len(files) != 1:
        raise ValueError(f"there is more than one file in {path} folder")
    return os.path.join(path, files[0])


@activity.defn
async def collect_result(opt: bool) -> list[File]:
    files = []
    files.append(
        collect_file(
            os.path.join(settings.meta.path, "config.ini"),
            FileType.CONFIG,
        )
    )
    files.append(
        collect_file(
            get_file_in_folder(os.path.join(settings.meta.path, "logs")),
            FileType.TERMINAL_LOG,
        )
    )
    files.append(
        collect_file(
            get_file_in_folder(os.path.join(settings.meta.path, "Tester", "cache")),
            FileType.CACHE,
        )
    )
    if opt:
        files.append(
            collect_file(
                os.path.join(settings.meta.path, "MQL5", "report.xml"),
                FileType.XML,
            )
        )
    else:
        files.append(
            collect_file(
                os.path.join(settings.meta.path, "MQL5", "report.htm"),
                FileType.BACKTEST_RESULT,
            )
        )
        for suffix in ["-holding", "-hst", "-mfemae", ""]:
            files.append(
                collect_file(
                    os.path.join(settings.meta.path, "MQL5", f"report{suffix}.png"),
                    FileType.BACKTEST_IMAGES,
                )
            )

    return files


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, inp: mql.Strategy) -> list[File]:
        logger.info("executing %s", inp.name)
        await workflow.execute_activity(
            clean,
            start_to_close_timeout=datetime.timedelta(seconds=10),
        )
        await workflow.execute_activity(
            write_config,
            inp,
            start_to_close_timeout=datetime.timedelta(seconds=10),
        )
        await workflow.execute_activity(
            write_strategy,
            inp.ex5,
            start_to_close_timeout=datetime.timedelta(seconds=10),
        )
        await workflow.execute_activity(
            run_strategy,
            inp,
            start_to_close_timeout=datetime.timedelta(hours=15),
        )
        return await workflow.execute_activity(
            collect_result,
            inp.optimization != mql.Optimization.DISABLED,
            start_to_close_timeout=datetime.timedelta(seconds=600),
        )


def get() -> tuple:
    return Workflow, [clean, write_config, write_strategy, run_strategy, collect_result]
