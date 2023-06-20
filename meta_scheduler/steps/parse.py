from datetime import timedelta

import xmltodict
from temporalio import activity
from temporalio import workflow
from temporalio.common import RetryPolicy

from meta_scheduler.models import file
from meta_scheduler.models import opt
from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

NAME = stepping.get_name(__name__)


@activity.defn
async def parse_xml(xml_file: file.File) -> opt.OptResult:
    xml = xmltodict.parse(xml_file.data.decode())
    workbook = xml["Workbook"]
    properties = workbook["DocumentProperties"]
    rows = workbook["Worksheet"]["Table"]["Row"]
    headers = [cell["Data"]["#text"] for cell in rows[0]["Cell"]]
    headers = [
        (header if header != "Equity DD %" else "drawdown")
        for header in headers
    ]
    headers = list(map(str.lower, headers))
    headers = list(map(lambda x: x.replace(" ", "_"), headers))
    data: dict[str, list] = {header: [] for header in headers}
    for raw_row in rows[1:]:
        row = raw_row["Cell"]
        if len(row) != len(headers):
            raise Exception("failed to parse")
        for i in range(len(headers)):
            x = row[i]["Data"]
            if "#text" in x:
                data[headers[i]].append(x["#text"])
            else:
                data[headers[i]].append(0)
    return opt.OptResult(
        create_time=properties["Created"],
        version=properties["Version"],
        **data,
    )


@activity.defn
async def parse_htm(htm_file: file.File):
    ...


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, inp: file.File) -> opt.OptResult:
        method = None
        if inp.type == file.FileType.XML:
            method = parse_xml
        elif inp.type == file.FileType.BACKTEST_RESULT:
            method = parse_htm
        if method is None:
            raise ValueError(f"unknown file type {inp.type}")
        return await workflow.execute_activity(
            method,
            inp,
            schedule_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(backoff_coefficient=1),
        )


def get() -> tuple:
    return Workflow, [parse_xml, parse_htm]
