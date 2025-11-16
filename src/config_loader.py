"""
Configuration Loader Module
Loads and manages configuration for the application rationalization tool.

This module provides functionality to load configuration from YAML files,
including scoring weights, TIME framework thresholds, and other settings.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from dataclasses import asdict

from .scoring_engine import ScoringWeights
from .time_framework import TIMEThresholds

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads and manages configuration from YAML files.

    This class provides centralized configuration management, supporting:
    - Scoring weights configuration
    - TIME framework thresholds
    - Application settings
    - Custom parameters

    The configuration is loaded from YAML files with a cascading approach:
    1. Default configuration (built-in)
    2. Global configuration file (config/config.yaml)
    3. User-specific configuration (config/config.local.yaml)
    4. Runtime overrides (passed as parameters)
    """

    DEFAULT_CONFIG_DIR = Path('config')
    DEFAULT_CONFIG_FILE = 'config.yaml'
    LOCAL_CONFIG_FILE = 'config.local.yaml'

    # Default scoring weights (used if no config file exists)
    DEFAULT_SCORING_WEIGHTS = {
        'business_value': 0.25,
        'tech_health': 0.20,
        'cost': 0.15,
        'usage': 0.15,
        'security': 0.10,
        'strategic_fit': 0.10,
        'redundancy': 0.05
    }

    # Default TIME thresholds (used if no config file exists)
    DEFAULT_TIME_THRESHOLDS = {
        'business_value_threshold': 6.0,
        'technical_quality_threshold': 6.0,
        'composite_score_high': 65.0,
        'composite_score_low': 40.0,
        'critical_business_value': 8.0,
        'poor_tech_health': 4.0,
        'poor_security': 5.0
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the configuration loader.

        Args:
            config_dir: Directory containing configuration files.
                       Defaults to ./config
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config = {}
        self._load_configuration()

    def _load_configuration(self):
        """
        Load configuration from files in cascading order.

        Configuration is loaded in this order (later overrides earlier):
        1. Default configuration (hardcoded)
        2. Global config file (config.yaml)
        3. Local config file (config.local.yaml) - gitignored
        """
        # Start with defaults
        self.config = {
            'scoring_weights': self.DEFAULT_SCORING_WEIGHTS.copy(),
            'time_thresholds': self.DEFAULT_TIME_THRESHOLDS.copy(),
            'normalization': {
                'max_cost': 300000,
                'max_usage': 1000
            },
            'output': {
                'default_format': 'csv',
                'timestamp_outputs': True,
                'include_retention_score': True
            }
        }

        # Load global config file if it exists
        global_config_path = self.config_dir / self.DEFAULT_CONFIG_FILE
        if global_config_path.exists():
            self._merge_config_file(global_config_path)
            logger.info(f"Loaded global configuration from {global_config_path}")

        # Load local config file if it exists (overrides global)
        local_config_path = self.config_dir / self.LOCAL_CONFIG_FILE
        if local_config_path.exists():
            self._merge_config_file(local_config_path)
            logger.info(f"Loaded local configuration from {local_config_path}")

    def _merge_config_file(self, config_path: Path):
        """
        Load and merge configuration from a YAML file.

        Args:
            config_path: Path to the YAML configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)

            if file_config:
                # Deep merge configuration
                self._deep_merge(self.config, file_config)

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
            raise

    def _deep_merge(self, base: Dict, update: Dict):
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary to merge into
            update: Dictionary with updates to merge
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get_scoring_weights(self) -> ScoringWeights:
        """
        Get scoring weights configuration.

        Returns:
            ScoringWeights object with configured weights

        Raises:
            ValueError: If weights are invalid or don't sum to 1.0
        """
        weights_config = self.config.get('scoring_weights', self.DEFAULT_SCORING_WEIGHTS)

        weights = ScoringWeights(
            business_value=float(weights_config.get('business_value', 0.25)),
            tech_health=float(weights_config.get('tech_health', 0.20)),
            cost=float(weights_config.get('cost', 0.15)),
            usage=float(weights_config.get('usage', 0.15)),
            security=float(weights_config.get('security', 0.10)),
            strategic_fit=float(weights_config.get('strategic_fit', 0.10)),
            redundancy=float(weights_config.get('redundancy', 0.05))
        )

        # Validate weights
        if not weights.validate():
            logger.warning(
                f"Scoring weights do not sum to 1.0. "
                f"Sum: {sum(asdict(weights).values()):.3f}"
            )

        return weights

    def get_time_thresholds(self) -> TIMEThresholds:
        """
        Get TIME framework thresholds configuration.

        Returns:
            TIMEThresholds object with configured thresholds

        Raises:
            ValueError: If thresholds are invalid
        """
        thresholds_config = self.config.get('time_thresholds', self.DEFAULT_TIME_THRESHOLDS)

        thresholds = TIMEThresholds(
            business_value_threshold=float(
                thresholds_config.get('business_value_threshold', 6.0)
            ),
            technical_quality_threshold=float(
                thresholds_config.get('technical_quality_threshold', 6.0)
            ),
            composite_score_high=float(
                thresholds_config.get('composite_score_high', 65.0)
            ),
            composite_score_low=float(
                thresholds_config.get('composite_score_low', 40.0)
            ),
            critical_business_value=float(
                thresholds_config.get('critical_business_value', 8.0)
            ),
            poor_tech_health=float(
                thresholds_config.get('poor_tech_health', 4.0)
            ),
            poor_security=float(
                thresholds_config.get('poor_security', 5.0)
            )
        )

        # Validate thresholds
        if not thresholds.validate():
            raise ValueError("Invalid TIME framework thresholds")

        return thresholds

    def get_normalization_params(self) -> Dict[str, float]:
        """
        Get normalization parameters for cost and usage.

        Returns:
            Dictionary with max_cost and max_usage values
        """
        norm_config = self.config.get('normalization', {})

        return {
            'max_cost': float(norm_config.get('max_cost', 300000)),
            'max_usage': float(norm_config.get('max_usage', 1000))
        }

    def get_output_settings(self) -> Dict[str, Any]:
        """
        Get output settings.

        Returns:
            Dictionary with output configuration
        """
        return self.config.get('output', {
            'default_format': 'csv',
            'timestamp_outputs': True,
            'include_retention_score': True
        })

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Supports dot notation for nested keys (e.g., 'scoring_weights.business_value')

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set_config_value(self, key: str, value: Any):
        """
        Set a configuration value at runtime.

        Supports dot notation for nested keys.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the nested location
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save_config(self, output_path: Optional[Path] = None):
        """
        Save current configuration to a YAML file.

        Args:
            output_path: Path to save configuration.
                        Defaults to config/config.local.yaml
        """
        if output_path is None:
            output_path = self.config_dir / self.LOCAL_CONFIG_FILE

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Configuration saved to {output_path}")

        except Exception as e:
            logger.error(f"Error saving configuration to {output_path}: {e}")
            raise

    def display_current_config(self) -> str:
        """
        Get a formatted string of the current configuration.

        Returns:
            Formatted configuration string
        """
        lines = ["Current Configuration:", "=" * 60]

        # Scoring Weights
        lines.append("\nScoring Weights:")
        weights = self.config.get('scoring_weights', {})
        for key, value in weights.items():
            lines.append(f"  {key:20} {value:.2f} ({value*100:.0f}%)")

        total = sum(weights.values())
        lines.append(f"  {'TOTAL':20} {total:.2f} ({total*100:.0f}%)")

        # TIME Thresholds
        lines.append("\nTIME Framework Thresholds:")
        thresholds = self.config.get('time_thresholds', {})
        for key, value in thresholds.items():
            lines.append(f"  {key:30} {value:.1f}")

        # Normalization
        lines.append("\nNormalization Parameters:")
        norm = self.config.get('normalization', {})
        for key, value in norm.items():
            if 'cost' in key.lower():
                lines.append(f"  {key:20} ${value:,.0f}")
            else:
                lines.append(f"  {key:20} {value:,.0f}")

        # Output Settings
        lines.append("\nOutput Settings:")
        output = self.config.get('output', {})
        for key, value in output.items():
            lines.append(f"  {key:20} {value}")

        lines.append("=" * 60)

        return "\n".join(lines)


def load_config(config_path: Optional[Path] = None) -> ConfigLoader:
    """
    Convenience function to load configuration.

    Args:
        config_path: Optional path to configuration directory

    Returns:
        Configured ConfigLoader instance
    """
    return ConfigLoader(config_dir=config_path)
