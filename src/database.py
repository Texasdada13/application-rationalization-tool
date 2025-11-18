"""
Database Module - Historical Tracking
SQLite-based storage for assessment history and trend analysis
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class Database:
    """
    Manages SQLite database for historical tracking of application assessments.

    Features:
    - Assessment run tracking
    - Application snapshots over time
    - Score history and trends
    - Change detection
    """

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. Defaults to 'data/assessment_history.db'
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / 'data' / 'assessment_history.db')

        self.db_path = db_path
        self.conn = None
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Use check_same_thread=False to allow access from multiple threads (Flask)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

        self._create_tables()
        logger.info(f"Database initialized at {self.db_path}")

    def _create_tables(self):
        """Create database schema"""
        cursor = self.conn.cursor()

        # Assessment Runs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessment_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                description TEXT,
                applications_count INTEGER NOT NULL,
                avg_composite_score REAL,
                total_cost REAL,
                source_file TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Application Snapshots Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_run_id INTEGER NOT NULL,
                application_name TEXT NOT NULL,
                owner TEXT,
                business_value REAL NOT NULL,
                tech_health REAL NOT NULL,
                cost REAL NOT NULL,
                usage INTEGER,
                security REAL,
                strategic_fit REAL,
                redundancy INTEGER,
                composite_score REAL,
                retention_score REAL,
                recommendation TEXT,
                time_category TEXT,
                time_business_value_score REAL,
                time_technical_quality_score REAL,
                comments TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assessment_run_id) REFERENCES assessment_runs(id),
                UNIQUE(assessment_run_id, application_name)
            )
        """)

        # Score Changes Table (for quick trend access)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS score_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_name TEXT NOT NULL,
                from_assessment_id INTEGER,
                to_assessment_id INTEGER NOT NULL,
                previous_score REAL,
                new_score REAL,
                score_change REAL,
                previous_recommendation TEXT,
                new_recommendation TEXT,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (from_assessment_id) REFERENCES assessment_runs(id),
                FOREIGN KEY (to_assessment_id) REFERENCES assessment_runs(id)
            )
        """)

        # Metadata Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_app_snapshots_run
            ON application_snapshots(assessment_run_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_app_snapshots_name
            ON application_snapshots(application_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_score_changes_app
            ON score_changes(application_name)
        """)

        self.conn.commit()
        logger.info("Database tables created successfully")

    def save_assessment(
        self,
        df: pd.DataFrame,
        description: str = None,
        source_file: str = None
    ) -> int:
        """
        Save an assessment run and all application data.

        Args:
            df: DataFrame containing assessment results
            description: Optional description of this assessment
            source_file: Optional source file path

        Returns:
            Assessment run ID
        """
        cursor = self.conn.cursor()

        # Calculate summary metrics
        applications_count = len(df)
        avg_composite_score = float(df['Composite Score'].mean()) if 'Composite Score' in df.columns else None
        total_cost = float(df['Cost'].sum())

        # Create assessment run record
        cursor.execute("""
            INSERT INTO assessment_runs
            (timestamp, description, applications_count, avg_composite_score, total_cost, source_file)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            description,
            applications_count,
            avg_composite_score,
            total_cost,
            source_file
        ))

        assessment_run_id = cursor.lastrowid

        # Save all application snapshots
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO application_snapshots (
                    assessment_run_id, application_name, owner,
                    business_value, tech_health, cost, usage,
                    security, strategic_fit, redundancy,
                    composite_score, retention_score, recommendation,
                    time_category, time_business_value_score,
                    time_technical_quality_score, comments
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_run_id,
                row['Application Name'],
                row.get('Owner'),
                float(row['Business Value']),
                float(row['Tech Health']),
                float(row['Cost']),
                int(row.get('Usage', 0)),
                float(row.get('Security', 0)),
                float(row.get('Strategic Fit', 0)),
                int(row.get('Redundancy', 0)),
                float(row.get('Composite Score', 0)),
                float(row.get('Retention Score', 0)),
                row.get('Action Recommendation'),
                row.get('TIME Category'),
                float(row.get('TIME Business Value Score', 0)),
                float(row.get('TIME Technical Quality Score', 0)),
                row.get('Comments')
            ))

        # Detect and record score changes
        self._record_score_changes(assessment_run_id, df)

        self.conn.commit()
        logger.info(f"Saved assessment run {assessment_run_id} with {applications_count} applications")

        return assessment_run_id

    def _record_score_changes(self, new_assessment_id: int, new_df: pd.DataFrame):
        """Record score changes compared to previous assessment"""
        cursor = self.conn.cursor()

        # Get previous assessment
        cursor.execute("""
            SELECT id FROM assessment_runs
            WHERE id < ?
            ORDER BY id DESC
            LIMIT 1
        """, (new_assessment_id,))

        prev_row = cursor.fetchone()
        if not prev_row:
            return  # No previous assessment

        prev_assessment_id = prev_row[0]

        # Get previous scores
        cursor.execute("""
            SELECT application_name, composite_score, recommendation
            FROM application_snapshots
            WHERE assessment_run_id = ?
        """, (prev_assessment_id,))

        prev_data = {row[0]: {'score': row[1], 'recommendation': row[2]}
                     for row in cursor.fetchall()}

        # Record changes
        for _, row in new_df.iterrows():
            app_name = row['Application Name']
            new_score = float(row.get('Composite Score', 0))
            new_recommendation = row.get('Action Recommendation')

            if app_name in prev_data:
                prev_score = prev_data[app_name]['score']
                prev_recommendation = prev_data[app_name]['recommendation']
                score_change = new_score - prev_score if prev_score else None

                cursor.execute("""
                    INSERT INTO score_changes (
                        application_name, from_assessment_id, to_assessment_id,
                        previous_score, new_score, score_change,
                        previous_recommendation, new_recommendation, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    app_name, prev_assessment_id, new_assessment_id,
                    prev_score, new_score, score_change,
                    prev_recommendation, new_recommendation,
                    datetime.now().isoformat()
                ))
            else:
                # New application
                cursor.execute("""
                    INSERT INTO score_changes (
                        application_name, from_assessment_id, to_assessment_id,
                        previous_score, new_score, score_change,
                        previous_recommendation, new_recommendation, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    app_name, None, new_assessment_id,
                    None, new_score, None,
                    None, new_recommendation,
                    datetime.now().isoformat()
                ))

    def get_assessment_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of all assessment runs"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, description, applications_count,
                   avg_composite_score, total_cost, source_file, created_at
            FROM assessment_runs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_assessment_by_id(self, assessment_id: int) -> Optional[Dict[str, Any]]:
        """Get specific assessment run details"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, description, applications_count,
                   avg_composite_score, total_cost, source_file, created_at
            FROM assessment_runs
            WHERE id = ?
        """, (assessment_id,))

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_application_history(
        self,
        application_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get historical snapshots for a specific application"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, r.timestamp as assessment_timestamp
            FROM application_snapshots s
            JOIN assessment_runs r ON s.assessment_run_id = r.id
            WHERE s.application_name = ?
            ORDER BY r.timestamp DESC
            LIMIT ?
        """, (application_name, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_score_trends(
        self,
        application_name: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get score trends over time.

        Args:
            application_name: Optional filter for specific application
            limit: Maximum number of records to return

        Returns:
            List of score change records
        """
        cursor = self.conn.cursor()

        if application_name:
            cursor.execute("""
                SELECT sc.*, r.timestamp
                FROM score_changes sc
                JOIN assessment_runs r ON sc.to_assessment_id = r.id
                WHERE sc.application_name = ?
                ORDER BY r.timestamp DESC
                LIMIT ?
            """, (application_name, limit))
        else:
            cursor.execute("""
                SELECT sc.*, r.timestamp
                FROM score_changes sc
                JOIN assessment_runs r ON sc.to_assessment_id = r.id
                ORDER BY r.timestamp DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_applications_at_run(self, assessment_run_id: int) -> pd.DataFrame:
        """Get all applications from a specific assessment run as DataFrame"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM application_snapshots
            WHERE assessment_run_id = ?
            ORDER BY application_name
        """, (assessment_run_id,))

        rows = cursor.fetchall()
        if not rows:
            return pd.DataFrame()

        # Convert to DataFrame
        columns = [description[0] for description in cursor.description]
        return pd.DataFrame([dict(zip(columns, row)) for row in rows])

    def get_top_improvers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get applications with biggest score improvements"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT application_name,
                   AVG(score_change) as avg_change,
                   MAX(new_score) as current_score,
                   COUNT(*) as assessment_count
            FROM score_changes
            WHERE score_change IS NOT NULL
            GROUP BY application_name
            HAVING avg_change > 0
            ORDER BY avg_change DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_top_decliners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get applications with biggest score declines"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT application_name,
                   AVG(score_change) as avg_change,
                   MAX(new_score) as current_score,
                   COUNT(*) as assessment_count
            FROM score_changes
            WHERE score_change IS NOT NULL
            GROUP BY application_name
            HAVING avg_change < 0
            ORDER BY avg_change ASC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_portfolio_trends(self, num_periods: int = 12) -> Dict[str, List]:
        """
        Get portfolio-level trends over time.

        Returns:
            Dictionary with timestamps and metrics
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, applications_count, avg_composite_score, total_cost
            FROM assessment_runs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (num_periods,))

        rows = cursor.fetchall()

        return {
            'timestamps': [row[0] for row in reversed(rows)],
            'app_counts': [row[1] for row in reversed(rows)],
            'avg_scores': [row[2] for row in reversed(rows)],
            'total_costs': [row[3] for row in reversed(rows)]
        }

    def compare_assessments(
        self,
        assessment_id_1: int,
        assessment_id_2: int
    ) -> Dict[str, Any]:
        """
        Compare two assessment runs.

        Returns:
            Comparison statistics and changed applications
        """
        cursor = self.conn.cursor()

        # Get assessment info
        run1 = self.get_assessment_by_id(assessment_id_1)
        run2 = self.get_assessment_by_id(assessment_id_2)

        if not run1 or not run2:
            return {}

        # Get applications from both runs
        cursor.execute("""
            SELECT application_name, composite_score, recommendation
            FROM application_snapshots
            WHERE assessment_run_id = ?
        """, (assessment_id_1,))
        apps1 = {row[0]: {'score': row[1], 'recommendation': row[2]}
                for row in cursor.fetchall()}

        cursor.execute("""
            SELECT application_name, composite_score, recommendation
            FROM application_snapshots
            WHERE assessment_run_id = ?
        """, (assessment_id_2,))
        apps2 = {row[0]: {'score': row[1], 'recommendation': row[2]}
                for row in cursor.fetchall()}

        # Calculate changes
        common_apps = set(apps1.keys()) & set(apps2.keys())
        new_apps = set(apps2.keys()) - set(apps1.keys())
        removed_apps = set(apps1.keys()) - set(apps2.keys())

        score_changes = []
        for app in common_apps:
            score_change = apps2[app]['score'] - apps1[app]['score']
            if abs(score_change) > 0.1:  # Meaningful change
                score_changes.append({
                    'application_name': app,
                    'previous_score': apps1[app]['score'],
                    'new_score': apps2[app]['score'],
                    'change': score_change,
                    'previous_recommendation': apps1[app]['recommendation'],
                    'new_recommendation': apps2[app]['recommendation']
                })

        # Sort by absolute change
        score_changes.sort(key=lambda x: abs(x['change']), reverse=True)

        return {
            'run1': run1,
            'run2': run2,
            'common_applications': len(common_apps),
            'new_applications': len(new_apps),
            'removed_applications': len(removed_apps),
            'new_app_names': list(new_apps),
            'removed_app_names': list(removed_apps),
            'score_changes': score_changes[:20],  # Top 20 changes
            'avg_score_change': sum(c['change'] for c in score_changes) / len(score_changes) if score_changes else 0
        }

    def delete_assessment(self, assessment_id: int) -> bool:
        """Delete an assessment run and all associated data"""
        cursor = self.conn.cursor()

        try:
            # Delete in order to respect foreign keys
            cursor.execute("DELETE FROM score_changes WHERE to_assessment_id = ? OR from_assessment_id = ?",
                          (assessment_id, assessment_id))
            cursor.execute("DELETE FROM application_snapshots WHERE assessment_run_id = ?",
                          (assessment_id,))
            cursor.execute("DELETE FROM assessment_runs WHERE id = ?",
                          (assessment_id,))

            self.conn.commit()
            logger.info(f"Deleted assessment run {assessment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete assessment {assessment_id}: {e}")
            self.conn.rollback()
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
