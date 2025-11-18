"""
Scheduler Module - Automated Assessment Scheduling
Provides continuous assessment capabilities with APScheduler
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
import json

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import pandas as pd

logger = logging.getLogger(__name__)


class SchedulerManager:
    """
    Manages automated assessment scheduling and continuous monitoring.

    Features:
    - Scheduled assessment runs (cron-based)
    - Interval-based monitoring
    - File system watching for new data
    - Email notifications (optional)
    - Job persistence and management
    """

    def __init__(
        self,
        data_handler=None,
        scoring_engine=None,
        recommendation_engine=None,
        time_framework=None,
        database=None,
        notification_callback: Optional[Callable] = None
    ):
        """
        Initialize scheduler manager.

        Args:
            data_handler: DataHandler instance
            scoring_engine: ScoringEngine instance
            recommendation_engine: RecommendationEngine instance
            time_framework: TIMEFramework instance
            database: Database instance for storing results
            notification_callback: Optional callback for notifications
        """
        self.data_handler = data_handler
        self.scoring_engine = scoring_engine
        self.recommendation_engine = recommendation_engine
        self.time_framework = time_framework
        self.database = database
        self.notification_callback = notification_callback

        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=3)
        }
        job_defaults = {
            'coalesce': False,  # Run all missed jobs
            'max_instances': 1  # Only one instance of each job
        }

        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )

        # Track watched directories
        self.watched_directories: Dict[str, Dict[str, Any]] = {}

        # Job history
        self.job_history: List[Dict[str, Any]] = []
        self.max_history = 100

        logger.info("Scheduler Manager initialized")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    def schedule_assessment(
        self,
        job_id: str,
        file_path: str,
        schedule_type: str = 'cron',
        cron_expression: Dict[str, str] = None,
        interval_minutes: int = None,
        description: str = None
    ) -> bool:
        """
        Schedule a recurring assessment.

        Args:
            job_id: Unique identifier for the job
            file_path: Path to data file to process
            schedule_type: 'cron' or 'interval'
            cron_expression: Cron schedule (e.g., {'hour': '9', 'minute': '0'} for 9 AM daily)
            interval_minutes: Interval in minutes (for interval type)
            description: Human-readable job description

        Returns:
            Success status
        """
        try:
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # Create trigger based on type
            if schedule_type == 'cron':
                if cron_expression is None:
                    cron_expression = {'hour': '9', 'minute': '0'}  # Default: 9 AM daily
                trigger = CronTrigger(**cron_expression)
            elif schedule_type == 'interval':
                if interval_minutes is None:
                    interval_minutes = 60  # Default: hourly
                trigger = IntervalTrigger(minutes=interval_minutes)
            else:
                logger.error(f"Invalid schedule type: {schedule_type}")
                return False

            # Add job
            self.scheduler.add_job(
                func=self._run_scheduled_assessment,
                trigger=trigger,
                args=[job_id, file_path, description],
                id=job_id,
                name=description or f"Assessment: {Path(file_path).name}",
                replace_existing=True
            )

            logger.info(f"Scheduled job '{job_id}' for file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule job '{job_id}': {e}")
            return False

    def _run_scheduled_assessment(
        self,
        job_id: str,
        file_path: str,
        description: str = None
    ):
        """
        Execute a scheduled assessment.

        Args:
            job_id: Job identifier
            file_path: Path to data file
            description: Optional description
        """
        start_time = datetime.now()
        logger.info(f"Starting scheduled assessment: {job_id}")

        try:
            # Check if file exists
            if not Path(file_path).exists():
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                self._record_job_execution(job_id, 'failed', error=error_msg)
                self._send_notification(
                    f"Assessment Failed: {job_id}",
                    error_msg
                )
                return

            # Load data
            if self.data_handler is None:
                error_msg = "DataHandler not initialized"
                logger.error(error_msg)
                self._record_job_execution(job_id, 'failed', error=error_msg)
                return

            df = self.data_handler.read_csv(file_path)

            # Validate data
            is_valid, errors = self.data_handler.validate_data(df)
            if not is_valid:
                error_msg = f"Data validation failed: {', '.join(errors)}"
                logger.error(error_msg)
                self._record_job_execution(job_id, 'failed', error=error_msg)
                self._send_notification(
                    f"Assessment Failed: {job_id}",
                    error_msg
                )
                return

            # Process data
            if self.scoring_engine:
                df = self.scoring_engine.batch_calculate_scores(df)

            if self.recommendation_engine:
                df = self.recommendation_engine.batch_generate_recommendations(df)

            if self.time_framework:
                df = self.time_framework.batch_categorize(df)

            # Save to database
            if self.database:
                assessment_id = self.database.save_assessment(
                    df=df,
                    description=description or f"Scheduled Assessment: {job_id}",
                    source_file=file_path
                )

                # Calculate summary
                summary = {
                    'total_apps': len(df),
                    'avg_score': float(df['Composite Score'].mean()) if 'Composite Score' in df.columns else 0,
                    'total_cost': float(df['Cost'].sum())
                }

                # Record success
                elapsed = (datetime.now() - start_time).total_seconds()
                self._record_job_execution(
                    job_id,
                    'success',
                    assessment_id=assessment_id,
                    summary=summary,
                    elapsed_seconds=elapsed
                )

                # Send success notification
                self._send_notification(
                    f"Assessment Completed: {job_id}",
                    f"Successfully processed {summary['total_apps']} applications. "
                    f"Average Score: {summary['avg_score']:.1f}. "
                    f"Total Cost: ${summary['total_cost']:,.0f}"
                )

                logger.info(f"Scheduled assessment '{job_id}' completed successfully in {elapsed:.2f}s")
            else:
                logger.warning("Database not initialized, results not saved")

        except Exception as e:
            import traceback
            error_msg = f"Assessment execution failed: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self._record_job_execution(job_id, 'failed', error=error_msg)
            self._send_notification(
                f"Assessment Failed: {job_id}",
                error_msg
            )

    def schedule_directory_watch(
        self,
        watch_id: str,
        directory_path: str,
        file_pattern: str = "*.csv",
        check_interval_minutes: int = 30,
        description: str = None
    ) -> bool:
        """
        Watch a directory for new files and automatically process them.

        Args:
            watch_id: Unique identifier for the watch job
            directory_path: Directory to watch
            file_pattern: File pattern to match (e.g., "*.csv", "assessment_*.xlsx")
            check_interval_minutes: How often to check for new files
            description: Human-readable description

        Returns:
            Success status
        """
        try:
            # Ensure directory exists
            dir_path = Path(directory_path)
            if not dir_path.exists():
                logger.error(f"Directory does not exist: {directory_path}")
                return False

            # Track watched directory
            self.watched_directories[watch_id] = {
                'directory': directory_path,
                'pattern': file_pattern,
                'processed_files': set(),
                'description': description
            }

            # Schedule periodic check
            trigger = IntervalTrigger(minutes=check_interval_minutes)
            self.scheduler.add_job(
                func=self._check_directory_for_new_files,
                trigger=trigger,
                args=[watch_id],
                id=f"watch_{watch_id}",
                name=description or f"Watch: {directory_path}",
                replace_existing=True
            )

            logger.info(f"Started watching directory: {directory_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to setup directory watch '{watch_id}': {e}")
            return False

    def _check_directory_for_new_files(self, watch_id: str):
        """Check watched directory for new files"""
        try:
            watch_info = self.watched_directories.get(watch_id)
            if not watch_info:
                logger.warning(f"Watch info not found for: {watch_id}")
                return

            directory = Path(watch_info['directory'])
            pattern = watch_info['pattern']
            processed_files = watch_info['processed_files']

            # Find matching files
            new_files = []
            for file_path in directory.glob(pattern):
                if file_path.is_file() and str(file_path) not in processed_files:
                    new_files.append(file_path)

            # Process new files
            for file_path in new_files:
                logger.info(f"Found new file: {file_path}")
                job_id = f"auto_{watch_id}_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Process immediately
                self._run_scheduled_assessment(
                    job_id=job_id,
                    file_path=str(file_path),
                    description=f"Auto-processed from watch: {watch_id}"
                )

                # Mark as processed
                processed_files.add(str(file_path))

            if new_files:
                logger.info(f"Processed {len(new_files)} new file(s) from watch '{watch_id}'")

        except Exception as e:
            logger.error(f"Error checking directory for watch '{watch_id}': {e}")

    def _record_job_execution(
        self,
        job_id: str,
        status: str,
        assessment_id: int = None,
        summary: Dict[str, Any] = None,
        elapsed_seconds: float = None,
        error: str = None
    ):
        """Record job execution in history"""
        execution_record = {
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'assessment_id': assessment_id,
            'summary': summary,
            'elapsed_seconds': elapsed_seconds,
            'error': error
        }

        self.job_history.append(execution_record)

        # Trim history if too long
        if len(self.job_history) > self.max_history:
            self.job_history = self.job_history[-self.max_history:]

    def _send_notification(self, subject: str, message: str):
        """Send notification via callback"""
        if self.notification_callback:
            try:
                self.notification_callback(subject, message)
            except Exception as e:
                logger.error(f"Notification callback failed: {e}")

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs

    def get_job_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent job execution history"""
        return self.job_history[-limit:]

    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job '{job_id}': {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job '{job_id}': {e}")
            return False

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")

            # Remove from watched directories if it's a watch job
            if job_id.startswith('watch_'):
                watch_id = job_id[6:]  # Remove 'watch_' prefix
                if watch_id in self.watched_directories:
                    del self.watched_directories[watch_id]

            return True
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {e}")
            return False

    def run_job_now(self, job_id: str) -> bool:
        """Trigger immediate execution of a scheduled job"""
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                logger.error(f"Job not found: {job_id}")
                return False

            # Execute job immediately
            job.func(*job.args, **job.kwargs)
            logger.info(f"Triggered immediate execution of job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to run job '{job_id}': {e}")
            return False

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        return {
            'running': self.scheduler.running,
            'total_jobs': len(self.scheduler.get_jobs()),
            'watched_directories': len(self.watched_directories),
            'job_history_count': len(self.job_history),
            'recent_executions': self.job_history[-10:] if self.job_history else []
        }

    def export_job_config(self, output_path: str) -> bool:
        """Export job configurations to JSON file"""
        try:
            jobs_config = []
            for job in self.scheduler.get_jobs():
                job_config = {
                    'id': job.id,
                    'name': job.name,
                    'trigger': str(job.trigger),
                    # Note: Cannot serialize full job function, only metadata
                }
                jobs_config.append(job_config)

            with open(output_path, 'w') as f:
                json.dump({
                    'jobs': jobs_config,
                    'watched_directories': {
                        k: {
                            'directory': v['directory'],
                            'pattern': v['pattern'],
                            'description': v.get('description')
                        }
                        for k, v in self.watched_directories.items()
                    }
                }, f, indent=2)

            logger.info(f"Exported job config to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export job config: {e}")
            return False
