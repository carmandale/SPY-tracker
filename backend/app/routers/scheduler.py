"""
Scheduler management endpoints for SPY Tracker.
Handles scheduled job status and manual triggers.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db

router = APIRouter(tags=["scheduler"])

# Global scheduler reference - will be set by main.py
_scheduler = None


def set_scheduler(scheduler):
    """Set the scheduler instance (called from main.py)"""
    global _scheduler
    _scheduler = scheduler


@router.get("/scheduler/status")
def get_scheduler_status():
    """Get current scheduler status and job information"""
    if not _scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": getattr(job, 'name', None),
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "max_instances": getattr(job, 'max_instances', None),
        })
    
    return {
        "scheduler_running": _scheduler.running,
        "jobs": jobs,
        "timezone": str(_scheduler.timezone),
        "total_jobs": len(jobs)
    }


@router.post("/scheduler/trigger/{job_id}")
def trigger_scheduler_job(job_id: str, db: Session = Depends(get_db)):
    """Manually trigger a scheduled job for testing"""
    if not _scheduler:
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    
    job = _scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        # Execute the job function manually
        if job_id == "capture_open":
            from ..scheduler import capture_price
            capture_price(db, "open")
            return {"status": "success", "job": job_id, "action": "captured open price"}
        elif job_id == "capture_noon":
            from ..scheduler import capture_price
            capture_price(db, "noon")
            return {"status": "success", "job": job_id, "action": "captured noon price"}
        elif job_id == "capture_2pm":
            from ..scheduler import capture_price
            capture_price(db, "twoPM")
            return {"status": "success", "job": job_id, "action": "captured 2PM price"}
        elif job_id == "capture_close":
            from ..scheduler import capture_price
            capture_price(db, "close")
            return {"status": "success", "job": job_id, "action": "captured close price"}
        elif job_id == "capture_premarket":
            from ..scheduler import capture_price
            capture_price(db, "preMarket")
            return {"status": "success", "job": job_id, "action": "captured premarket price"}
        elif job_id == "ai_predict_0800":
            from ..scheduler import _run_ai_prediction
            from ..database import get_db as get_db_func
            _run_ai_prediction(get_db_func)
            return {"status": "success", "job": job_id, "action": "generated AI predictions"}
        elif job_id == "ai_predict_0830":  # Legacy support
            from ..scheduler import _run_ai_prediction
            from ..database import get_db as get_db_func
            _run_ai_prediction(get_db_func)
            return {"status": "success", "job": "ai_predict_0800", "action": "generated AI predictions (legacy trigger)"}
        else:
            return {"status": "error", "message": f"Unknown job: {job_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job execution failed: {str(e)}")