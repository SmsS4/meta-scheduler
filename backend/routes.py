import base64
from uuid import uuid4

from fastapi import APIRouter
from sqlalchemy.orm import Session
from temporalio.client import Client

from backend import schemas
from meta_scheduler import models
from meta_scheduler import settings
from meta_scheduler.models import mql
from meta_scheduler.steps import recv
from meta_scheduler.utils import db_session

router = APIRouter()

db: Session = db_session.DBSession()


@router.delete("/results")
def delete(uid: str):
    db.query(models.db.OptResult).filter_by(id=uid).delete()
    db.commit()


@router.get("/results")
def get_results():
    result = db.query(models.db.OptResult).all()
    return [res.__dict__ for res in result]


@router.post("/")
async def new_strategy(strategy: schemas.Strategy):
    client = await Client.connect(
        f"{settings.temporal.HOST}:{settings.temporal.PORT}",
        namespace=settings.temporal.NAMESPACE,
    )

    await client.start_workflow(
        recv.Workflow.run,
        recv.Input(
            mql.Strategy(
                ex5=base64.b64decode(strategy.ex5),
                name=strategy.name,
                period=strategy.period,
                model=strategy.model,
                optimization=strategy.optimization,
                cost_function=strategy.cost_function,
                from_date=strategy.from_date,
                to_date=strategy.to_date,
                set_file=strategy.set_file,
            ),
            symbols=strategy.symbols,
        ),
        id=str(uuid4()),
        task_queue=settings.temporal.task_queue,
    )
