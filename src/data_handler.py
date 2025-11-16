"""
Data Handler Module
Manages reading and writing application portfolio data from/to CSV and Excel files.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataHandler:
    """
    Handles all data I/O operations for the application rationalization tool.

    Supports CSV and Excel formats with validation and error handling.
    """

    REQUIRED_COLUMNS = [
        'Application Name',
        'Owner',
        'Business Value',
        'Tech Health',
        'Cost',
        'Usage',
        'Security',
        'Strategic Fit',
        'Redundancy'
    ]

    OUTPUT_COLUMNS = REQUIRED_COLUMNS + [
        'Composite Score',
        'Action Recommendation',
        'Comments',
        'TIME Category',
        'TIME Rationale',
        'TIME Business Value Score',
        'TIME Technical Quality Score'
    ]

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the data handler.

        Args:
            data_dir: Directory containing data files. Defaults to ./data
        """
        self.data_dir = data_dir or Path('./data')
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def read_csv(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Read application data from CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            DataFrame containing application data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded {len(df)} applications from {file_path}")

            # Validate required columns
            missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            return df

        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise

    def read_excel(self, file_path: Union[str, Path], sheet_name: str = 'Applications') -> pd.DataFrame:
        """
        Read application data from Excel file.

        Args:
            file_path: Path to the Excel file
            sheet_name: Name of the sheet to read

        Returns:
            DataFrame containing application data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            logger.info(f"Successfully loaded {len(df)} applications from {file_path}")

            # Validate required columns
            missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            return df

        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {e}")
            raise

    def write_csv(
        self,
        df: pd.DataFrame,
        output_path: Union[str, Path],
        include_timestamp: bool = True
    ) -> Path:
        """
        Write application data to CSV file.

        Args:
            df: DataFrame containing application data
            output_path: Path for the output file
            include_timestamp: Whether to append timestamp to filename

        Returns:
            Path to the written file
        """
        output_path = Path(output_path)

        if include_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully wrote {len(df)} applications to {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error writing CSV file {output_path}: {e}")
            raise

    def write_excel(
        self,
        df: pd.DataFrame,
        output_path: Union[str, Path],
        sheet_name: str = 'Applications',
        include_timestamp: bool = True
    ) -> Path:
        """
        Write application data to Excel file with formatting.

        Args:
            df: DataFrame containing application data
            output_path: Path for the output file
            sheet_name: Name of the sheet
            include_timestamp: Whether to append timestamp to filename

        Returns:
            Path to the written file
        """
        output_path = Path(output_path)

        if include_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to Excel with openpyxl engine for better formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Auto-adjust column widths
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"Successfully wrote {len(df)} applications to {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error writing Excel file {output_path}: {e}")
            raise

    def validate_data(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Validate application data for completeness and correctness.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Check for empty application names
        if 'Application Name' in df.columns:
            empty_names = df['Application Name'].isna().sum()
            if empty_names > 0:
                errors.append(f"{empty_names} applications have empty names")

        # Validate score ranges (0-10)
        score_columns = ['Business Value', 'Tech Health', 'Security', 'Strategic Fit']
        for col in score_columns:
            if col in df.columns:
                invalid = ((df[col] < 0) | (df[col] > 10)).sum()
                if invalid > 0:
                    errors.append(f"{invalid} invalid values in {col} (must be 0-10)")

        # Validate redundancy (0 or 1)
        if 'Redundancy' in df.columns:
            invalid = (~df['Redundancy'].isin([0, 1])).sum()
            if invalid > 0:
                errors.append(f"{invalid} invalid Redundancy values (must be 0 or 1)")

        # Validate cost (positive numbers)
        if 'Cost' in df.columns:
            invalid = (df['Cost'] < 0).sum()
            if invalid > 0:
                errors.append(f"{invalid} negative Cost values")

        # Validate usage (positive numbers)
        if 'Usage' in df.columns:
            invalid = (df['Usage'] < 0).sum()
            if invalid > 0:
                errors.append(f"{invalid} negative Usage values")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics for the application portfolio.

        Args:
            df: DataFrame containing application data

        Returns:
            Dictionary of summary statistics
        """
        stats = {
            'total_applications': len(df),
            'total_cost': df['Cost'].sum() if 'Cost' in df.columns else 0,
            'average_business_value': df['Business Value'].mean() if 'Business Value' in df.columns else 0,
            'average_tech_health': df['Tech Health'].mean() if 'Tech Health' in df.columns else 0,
            'average_security': df['Security'].mean() if 'Security' in df.columns else 0,
            'redundant_applications': df['Redundancy'].sum() if 'Redundancy' in df.columns else 0,
        }

        if 'Composite Score' in df.columns:
            stats['average_composite_score'] = df['Composite Score'].mean()
            stats['median_composite_score'] = df['Composite Score'].median()

        if 'Action Recommendation' in df.columns:
            stats['action_distribution'] = df['Action Recommendation'].value_counts().to_dict()

        return stats

    def filter_applications(
        self,
        df: pd.DataFrame,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        owner: Optional[str] = None,
        action: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter applications based on criteria.

        Args:
            df: DataFrame to filter
            min_score: Minimum composite score
            max_score: Maximum composite score
            owner: Filter by owner
            action: Filter by action recommendation

        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()

        if min_score is not None and 'Composite Score' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Composite Score'] >= min_score]

        if max_score is not None and 'Composite Score' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Composite Score'] <= max_score]

        if owner is not None and 'Owner' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Owner'].str.contains(owner, case=False, na=False)]

        if action is not None and 'Action Recommendation' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Action Recommendation'] == action]

        return filtered_df
