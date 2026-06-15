from redis import Redis
from rq import Queue
from rq.job import Job
import os

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_conn = Redis.from_url(REDIS_URL)

# Create the detection queue
# jobs timeout after 5 minutes — prevents stuck jobs
detection_queue = Queue(
    "detection",
    connection=redis_conn,
    default_timeout=300
)


def get_job_status(job_id: str) -> dict:
    """
    Check the status of a queued job by ID.
    Returns a dict with status and result if complete.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        return {"status": "not_found", "job_id": job_id}

    if job.is_finished:
        return {
            "status": "complete",
            "job_id": job_id,
            "result": job.result
        }
    elif job.is_failed:
        return {
            "status": "failed",
            "job_id": job_id,
            "error": str(job.exc_info)
        }
    elif job.is_started:
        return {
            "status": "processing",
            "job_id": job_id
        }
    else:
        return {
            "status": "queued",
            "job_id": job_id
        }