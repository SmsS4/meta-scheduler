from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Info

current_task = Info("current_task", "What task worker is doing")
progress = Gauge("progress", "Progess of current task")
recived_strategy = Counter(
    "recived_strategy", "Number of recived strategy", ["symbol"]
)
worker = Info("worker", "Worker info")
