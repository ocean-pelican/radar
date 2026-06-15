import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from redis import Redis
from rq import Worker, Queue
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(REDIS_URL)

if __name__ == "__main__":
    # Listen on the detection queue
    queues = [Queue("detection", connection=redis_conn)]

    worker = Worker(
        queues,
        connection=redis_conn,
        log_job_description=True,
    )

    print("Worker started. Listening on queue: detection")
    print("Waiting for jobs...")
    worker.work(with_scheduler=True)