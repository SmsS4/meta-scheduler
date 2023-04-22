from dataclasses import dataclass

from temporalio import workflow

from meta_scheduler.utils.logger import get_logger


@workflow.defn
class Workflow:
    @staticmethod
    def get_name(name: str) -> str:
        return name[name.rfind(".") + 1 :]

    NAME = get_name(__name__)  # pylint: disable=no-value-for-parameter
    logger = get_logger(NAME)

    # logger = get_logger(NAME)
    @dataclass(slots=True)
    class Input:
        ...

    @dataclass(slots=True)
    class Output:
        ...

    @workflow.run
    async def run(
        self, inp: Input
    ) -> Output:  # pylint: disable=unused-argument
        raise NotImplementedError()

    @classmethod
    def get_and_check(cls) -> tuple:
        activities = []
        for value in cls.__dict__.values():
            try:
                if "__temporal_activity_definition" in value.__dict__:
                    activities.append(value)
            except AttributeError:
                ...

        return cls, activities
