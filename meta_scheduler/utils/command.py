import subprocess
from dataclasses import dataclass
from functools import wraps
from threading import Thread

from meta_scheduler.utils.logger import get_logger

logger = get_logger("command")


@dataclass(slots=True)
class Result:
    stdout: str
    stderr: str
    returncode: int


def run(
    *command: str,
    stdin: str | bytes | None = None,
    timeout: int | None = None,
    raise_on_error: bool = False,
    shell: bool = False,
) -> Result:
    commands_as_list = list(command)
    logger.info("running {}", " ".join(commands_as_list))
    if stdin is not None and isinstance(stdin, str):
        stdin = stdin.encode()
    try:
        res = subprocess.check_output(
            commands_as_list if not shell else " ".join(commands_as_list),
            shell=shell,
            timeout=timeout,
            input=stdin,
        )
        logger.debug("stdout: {}", res)
        return Result(res.decode(), "", 0)
    except subprocess.CalledProcessError as cpe:
        logger.error(
            "stdout: {}\nstderr: {}\nreturn code: {}",
            cpe.stderr,
            cpe.stdout,
            cpe.returncode,
        )
        if raise_on_error:
            raise cpe
        if cpe.stdout is None:
            cpe.stdout = b""
        if cpe.stderr is None:
            cpe.stderr = b""
        return Result(cpe.stdout.decode(), cpe.stderr.decode(), cpe.returncode)


def run_in_background_thread(func):
    @wraps(func)
    def run_async_thread(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.daemon = True
        func_hl.start()
        return func_hl

    run_async_thread.unwrapped = func
    return run_async_thread
