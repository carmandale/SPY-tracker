"""
Version and deployment status API endpoints
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import settings
from ..timezone_utils import get_current_cst_time, get_next_market_open


router = APIRouter(prefix="/api", tags=["version"])


class DeploymentInfo(BaseModel):
    """Deployment information model"""
    timestamp: str
    commit: Optional[str] = None
    branch: Optional[str] = None


class SchedulerInfo(BaseModel):
    """Scheduler status information"""
    running: bool
    jobs_count: int
    next_prediction: Optional[str] = None


class VersionResponse(BaseModel):
    """Version endpoint response model"""
    version: str
    environment: str
    deployment: DeploymentInfo
    scheduler: SchedulerInfo


class NextPredictionResponse(BaseModel):
    """Next prediction time response model"""
    next_run: str  # ISO format datetime
    next_run_cst: str  # Human readable CST time
    time_until: str  # Human readable duration
    market_status: str  # "open", "closed", "weekend", "holiday"
    is_weekend: bool
    is_holiday: bool


class ChangelogResponse(BaseModel):
    """Changelog response model"""
    latest_version: str
    latest_date: str
    changes: list[str]


def get_git_info() -> Dict[str, Optional[str]]:
    """Get current git commit and branch info"""
    try:
        # Get current commit hash
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()[:7]  # First 7 chars of commit hash
        
        # Get current branch
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {"commit": commit, "branch": branch}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"commit": None, "branch": None}


def get_package_version() -> str:
    """Get version from package.json or pyproject.toml"""
    # Try frontend package.json first
    package_json_path = Path(__file__).parent.parent.parent.parent / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path) as f:
                package_data = json.load(f)
                return package_data.get("version", "2.0.0")
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Try backend pyproject.toml
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path) as f:
                for line in f:
                    if line.startswith("version"):
                        # Extract version from: version = "2.0.0"
                        version = line.split("=")[1].strip().strip('"')
                        return version
        except Exception:
            pass
    
    return "2.0.0"  # Default version


def detect_environment() -> str:
    """Detect current environment"""
    # Check common environment variables
    env = os.getenv("ENVIRONMENT", os.getenv("ENV", "")).lower()
    if env in ["production", "prod"]:
        return "production"
    elif env in ["staging", "stage"]:
        return "staging"
    
    # Check if running on Render
    if os.getenv("RENDER"):
        return "production"
    
    # Check if running locally
    if os.getenv("LOCAL_DEV") or not env:
        return "development"
    
    return "development"


def get_scheduler_status() -> SchedulerInfo:
    """Get scheduler status information"""
    # Import here to avoid circular dependency
    try:
        from ..scheduler import scheduler_instance
        
        if scheduler_instance and hasattr(scheduler_instance, 'scheduler'):
            scheduler = scheduler_instance.scheduler
            running = scheduler.running if scheduler else False
            jobs = scheduler.get_jobs() if scheduler else []
            
            # Find next AI prediction job
            next_prediction = None
            for job in jobs:
                if "ai_prediction" in str(job.id).lower():
                    if job.next_run_time:
                        next_prediction = job.next_run_time.isoformat()
                    break
            
            return SchedulerInfo(
                running=running,
                jobs_count=len(jobs),
                next_prediction=next_prediction
            )
    except ImportError:
        pass
    
    # Default if scheduler not available
    return SchedulerInfo(
        running=False,
        jobs_count=0,
        next_prediction=None
    )


@router.get("/version", response_model=VersionResponse)
async def get_version():
    """Get application version and deployment status"""
    git_info = get_git_info()
    
    return VersionResponse(
        version=get_package_version(),
        environment=detect_environment(),
        deployment=DeploymentInfo(
            timestamp=datetime.utcnow().isoformat() + "Z",
            commit=git_info["commit"],
            branch=git_info["branch"]
        ),
        scheduler=get_scheduler_status()
    )


@router.get("/scheduler/next-prediction", response_model=NextPredictionResponse)
async def get_next_prediction_time():
    """Get the next scheduled AI prediction time"""
    from ..market_holidays import is_market_holiday, get_holiday_name
    
    current_time = get_current_cst_time()
    next_run = get_next_market_open(current_time)
    
    # Calculate time until next run
    time_delta = next_run - current_time
    hours, remainder = divmod(int(time_delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    
    if hours > 24:
        days = hours // 24
        time_until = f"{days} day{'s' if days > 1 else ''}, {hours % 24} hours"
    elif hours > 0:
        time_until = f"{hours} hour{'s' if hours > 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        time_until = f"{minutes} minute{'s' if minutes != 1 else ''}"
    
    # Determine market status and holiday info
    weekday = current_time.weekday()
    is_weekend = weekday >= 5  # Saturday = 5, Sunday = 6
    is_holiday = is_market_holiday(current_time.date())
    holiday_name = get_holiday_name(current_time.date()) if is_holiday else None
    
    if is_holiday:
        market_status = f"holiday ({holiday_name})" if holiday_name else "holiday"
    elif is_weekend:
        market_status = "weekend"
    elif current_time.hour < 8:
        market_status = "closed"
    elif current_time.hour >= 15:
        market_status = "closed"
    else:
        market_status = "open"
    
    # Format human-readable CST time
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    next_weekday = weekday_names[next_run.weekday()]
    next_run_cst = f"{next_weekday}, {next_run.strftime('%B %d at %I:%M %p')} CST"
    
    return NextPredictionResponse(
        next_run=next_run.isoformat(),
        next_run_cst=next_run_cst,
        time_until=time_until,
        market_status=market_status,
        is_weekend=is_weekend,
        is_holiday=is_holiday
    )


@router.get("/changelog", response_model=ChangelogResponse)
async def get_changelog():
    """Get latest changelog information"""
    changelog_path = Path(__file__).parent.parent.parent.parent / "CHANGELOG.md"
    
    if not changelog_path.exists():
        raise HTTPException(status_code=404, detail="Changelog not found")
    
    try:
        with open(changelog_path) as f:
            content = f.read()
            
        # Parse latest version section
        lines = content.split("\n")
        latest_version = "2.0.0"
        latest_date = "2025-08-16"
        changes = []
        
        in_version_section = False
        for line in lines:
            if line.startswith("## [") and not line.startswith("## [Unreleased]"):
                if not in_version_section:
                    # First version section found
                    parts = line.split("]")
                    if parts:
                        version_part = parts[0].replace("## [", "")
                        latest_version = version_part
                        
                        if " - " in line:
                            date_part = line.split(" - ")[1]
                            latest_date = date_part
                    in_version_section = True
                else:
                    # Next version section, stop parsing
                    break
            elif in_version_section and line.startswith("- "):
                changes.append(line[2:])  # Remove "- " prefix
        
        return ChangelogResponse(
            latest_version=latest_version,
            latest_date=latest_date,
            changes=changes[:10]  # Return first 10 changes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading changelog: {str(e)}")