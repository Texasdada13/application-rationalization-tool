"""
Visualization Module
Generates visual representations of application rationalization assessments.

This module provides comprehensive visualization capabilities including:
- Heatmaps for application score matrices
- TIME framework quadrant visualizations
- Priority matrix charts
- Score distribution plots
- Portfolio health dashboards

All visualizations are designed for business presentations and executive reporting.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Configure matplotlib for better output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'


class VisualizationEngine:
    """
    Main visualization engine for application rationalization insights.

    This class provides methods to create various types of visualizations
    from application assessment data, with professional formatting suitable
    for executive presentations and strategic planning sessions.
    """

    # Standard color schemes for different visualization types
    SCORE_COLORMAP = 'RdYlGn'  # Red-Yellow-Green for scores (low to high)
    TIME_COLORS = {
        'Invest': '#2E7D32',      # Dark Green
        'Tolerate': '#FFA726',    # Orange
        'Migrate': '#1976D2',     # Blue
        'Eliminate': '#C62828'    # Dark Red
    }

    PRIORITY_COLORMAP = 'YlOrRd'  # Yellow-Orange-Red for priority/urgency

    def __init__(self, output_dir: Optional[Path] = None, style: str = 'professional'):
        """
        Initialize the visualization engine.

        Args:
            output_dir: Directory for saving visualizations. Defaults to ./output/visualizations
            style: Visualization style ('professional', 'presentation', 'technical')
        """
        self.output_dir = output_dir or Path('./output/visualizations')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.style = style

        # Set style defaults
        if style == 'professional':
            sns.set_style('whitegrid')
            sns.set_palette('deep')
        elif style == 'presentation':
            sns.set_style('white')
            sns.set_palette('bright')
        else:  # technical
            sns.set_style('darkgrid')
            sns.set_palette('muted')

    def create_score_heatmap(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None,
        dimensions: Optional[List[str]] = None,
        max_apps: int = 30,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 10),
        show_values: bool = True
    ) -> Path:
        """
        Create a heatmap showing application scores across all dimensions.

        This visualization displays a matrix of applications (rows) vs. scoring
        dimensions (columns), with color intensity indicating score values.
        Excellent for identifying patterns and outliers across the portfolio.

        Args:
            df: DataFrame containing application assessment data
            output_file: Custom output filename (optional)
            dimensions: List of dimensions to include. Uses defaults if None.
            max_apps: Maximum number of applications to display
            title: Custom title for the heatmap
            figsize: Figure size as (width, height) in inches
            show_values: Whether to annotate cells with numeric values

        Returns:
            Path to the saved heatmap image

        Example:
            >>> viz = VisualizationEngine()
            >>> path = viz.create_score_heatmap(df, dimensions=['Business Value', 'Tech Health'])
        """
        logger.info("Creating application score heatmap...")

        # Default dimensions if not specified
        if dimensions is None:
            dimensions = [
                'Business Value', 'Tech Health', 'Security',
                'Strategic Fit', 'Usage', 'Cost', 'Composite Score'
            ]

        # Filter for available dimensions
        available_dims = [d for d in dimensions if d in df.columns]

        if not available_dims:
            raise ValueError(f"None of the specified dimensions found in data: {dimensions}")

        # Limit number of applications for readability
        plot_df = df.head(max_apps).copy()

        # Prepare data matrix
        app_names = plot_df['Application Name'].values if 'Application Name' in plot_df.columns else plot_df.index
        data_matrix = plot_df[available_dims].values

        # Handle Cost normalization for display (if present and not already normalized)
        if 'Cost' in available_dims:
            cost_idx = available_dims.index('Cost')
            # Normalize cost to 0-10 scale for visualization
            max_cost = data_matrix[:, cost_idx].max()
            if max_cost > 100:  # Assume it's raw cost, not normalized
                normalized_cost = 10 * (1 - np.minimum(data_matrix[:, cost_idx] / max_cost, 1.0))
                data_matrix[:, cost_idx] = normalized_cost

        # Handle Usage normalization (if present and not already normalized)
        if 'Usage' in available_dims:
            usage_idx = available_dims.index('Usage')
            max_usage = data_matrix[:, usage_idx].max()
            if max_usage > 10:  # Assume it's raw usage, not normalized
                normalized_usage = 10 * np.minimum(data_matrix[:, usage_idx] / max_usage, 1.0)
                data_matrix[:, usage_idx] = normalized_usage

        # Normalize Composite Score to 0-10 for consistent color scaling
        if 'Composite Score' in available_dims:
            cs_idx = available_dims.index('Composite Score')
            data_matrix[:, cs_idx] = data_matrix[:, cs_idx] / 10

        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)

        # Create heatmap
        im = ax.imshow(data_matrix, aspect='auto', cmap=self.SCORE_COLORMAP, vmin=0, vmax=10)

        # Set ticks and labels
        ax.set_xticks(np.arange(len(available_dims)))
        ax.set_yticks(np.arange(len(app_names)))
        ax.set_xticklabels(available_dims, rotation=45, ha='right')
        ax.set_yticklabels(app_names, fontsize=9)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Score (0-10 scale)', rotation=270, labelpad=20)

        # Optionally annotate cells with values
        if show_values:
            for i in range(len(app_names)):
                for j in range(len(available_dims)):
                    value = data_matrix[i, j]
                    # For Composite Score, show original 0-100 scale
                    if available_dims[j] == 'Composite Score':
                        display_value = value * 10
                        text = ax.text(j, i, f'{display_value:.1f}',
                                     ha="center", va="center", color="black", fontsize=7)
                    else:
                        text = ax.text(j, i, f'{value:.1f}',
                                     ha="center", va="center", color="black", fontsize=7)

        # Set title
        if title is None:
            title = f'Application Portfolio Score Heatmap\n({len(app_names)} Applications)'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Add grid for better readability
        ax.set_xticks(np.arange(len(available_dims))-.5, minor=True)
        ax.set_yticks(np.arange(len(app_names))-.5, minor=True)
        ax.grid(which="minor", color="white", linestyle='-', linewidth=2)

        plt.tight_layout()

        # Save figure
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'score_heatmap_{timestamp}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"Score heatmap saved to: {output_path}")
        return output_path

    def create_time_quadrant_heatmap(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 10),
        show_labels: bool = True,
        max_label_length: int = 20
    ) -> Path:
        """
        Create a TIME framework quadrant heatmap.

        This scatter plot visualization shows applications positioned based on
        Business Value (Y-axis) vs Technical Quality (X-axis), with quadrants
        colored according to TIME framework categories. Application names can
        optionally be displayed as labels.

        Args:
            df: DataFrame with TIME categorization data
            output_file: Custom output filename
            title: Custom title for the visualization
            figsize: Figure size as (width, height) in inches
            show_labels: Whether to show application names as labels
            max_label_length: Maximum length for application name labels

        Returns:
            Path to the saved visualization

        The four quadrants represent:
            - Top Right: INVEST (High BV, High TQ)
            - Top Left: TOLERATE (High BV, Low TQ)
            - Bottom Left: ELIMINATE (Low BV, Low TQ)
            - Bottom Right: MIGRATE (Low BV, High TQ)
        """
        logger.info("Creating TIME framework quadrant heatmap...")

        # Check for required columns
        required_cols = ['TIME Business Value Score', 'TIME Technical Quality Score']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Extract data
        bv_scores = df['TIME Business Value Score'].values
        tq_scores = df['TIME Technical Quality Score'].values
        app_names = df['Application Name'].values if 'Application Name' in df.columns else df.index
        time_categories = df['TIME Category'].values if 'TIME Category' in df.columns else ['Unknown'] * len(df)

        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)

        # Draw quadrant backgrounds
        ax.axhspan(6, 10, xmin=0, xmax=0.5, alpha=0.1, color=self.TIME_COLORS['Tolerate'], zorder=0)
        ax.axhspan(6, 10, xmin=0.5, xmax=1, alpha=0.1, color=self.TIME_COLORS['Invest'], zorder=0)
        ax.axhspan(0, 6, xmin=0, xmax=0.5, alpha=0.1, color=self.TIME_COLORS['Eliminate'], zorder=0)
        ax.axhspan(0, 6, xmin=0.5, xmax=1, alpha=0.1, color=self.TIME_COLORS['Migrate'], zorder=0)

        # Plot applications by TIME category
        for category, color in self.TIME_COLORS.items():
            mask = time_categories == category
            if mask.any():
                ax.scatter(
                    tq_scores[mask], bv_scores[mask],
                    c=color, label=category, s=100, alpha=0.7,
                    edgecolors='black', linewidth=1.5, zorder=3
                )

        # Add application labels if requested
        if show_labels:
            for i, (tq, bv, name) in enumerate(zip(tq_scores, bv_scores, app_names)):
                # Truncate long names
                display_name = name[:max_label_length] + '...' if len(name) > max_label_length else name
                ax.annotate(
                    display_name, (tq, bv),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=7, alpha=0.8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='gray')
                )

        # Draw quadrant dividing lines
        ax.axhline(y=6, color='black', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
        ax.axvline(x=6, color='black', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)

        # Add quadrant labels
        ax.text(3, 8, 'TOLERATE', fontsize=12, fontweight='bold', alpha=0.3,
                ha='center', va='center', color=self.TIME_COLORS['Tolerate'])
        ax.text(8, 8, 'INVEST', fontsize=12, fontweight='bold', alpha=0.3,
                ha='center', va='center', color=self.TIME_COLORS['Invest'])
        ax.text(3, 3, 'ELIMINATE', fontsize=12, fontweight='bold', alpha=0.3,
                ha='center', va='center', color=self.TIME_COLORS['Eliminate'])
        ax.text(8, 3, 'MIGRATE', fontsize=12, fontweight='bold', alpha=0.3,
                ha='center', va='center', color=self.TIME_COLORS['Migrate'])

        # Set labels and title
        ax.set_xlabel('Technical Quality Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Business Value Score', fontsize=12, fontweight='bold')

        if title is None:
            title = f'TIME Framework Quadrant Analysis\n({len(df)} Applications)'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Set axis limits
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

        # Add grid
        ax.grid(True, alpha=0.3, linestyle=':', zorder=1)

        # Add legend
        ax.legend(loc='upper left', framealpha=0.9, fontsize=10)

        # Add axis annotations
        ax.text(-0.5, 5, 'Business Value →', fontsize=10, rotation=90,
                ha='center', va='center', alpha=0.6)
        ax.text(5, -0.5, 'Technical Quality →', fontsize=10,
                ha='center', va='center', alpha=0.6)

        plt.tight_layout()

        # Save figure
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'time_quadrant_{timestamp}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"TIME quadrant heatmap saved to: {output_path}")
        return output_path

    def create_priority_matrix(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None,
        x_metric: str = 'Composite Score',
        y_metric: str = 'Business Value',
        size_metric: Optional[str] = 'Cost',
        color_metric: str = 'Tech Health',
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 10)
    ) -> Path:
        """
        Create a priority matrix bubble chart.

        This advanced visualization shows applications on a customizable 2D matrix
        with bubble sizes representing a third metric (e.g., cost) and colors
        representing a fourth metric (e.g., tech health). Highly effective for
        identifying priority applications based on multiple criteria.

        Args:
            df: DataFrame containing application data
            output_file: Custom output filename
            x_metric: Column name for X-axis metric
            y_metric: Column name for Y-axis metric
            size_metric: Column name for bubble size (None for uniform size)
            color_metric: Column name for bubble color
            title: Custom title
            figsize: Figure size

        Returns:
            Path to the saved visualization
        """
        logger.info("Creating priority matrix visualization...")

        # Validate required metrics exist
        required_metrics = [x_metric, y_metric, color_metric]
        if size_metric:
            required_metrics.append(size_metric)

        missing = [m for m in required_metrics if m not in df.columns]
        if missing:
            raise ValueError(f"Missing required metrics: {missing}")

        # Extract data
        x_data = df[x_metric].values
        y_data = df[y_metric].values
        color_data = df[color_metric].values

        # Normalize x and y if they're composite scores (0-100 scale)
        if 'Score' in x_metric and x_data.max() > 10:
            x_data = x_data / 10
            x_label = f'{x_metric} (0-10 scale)'
        else:
            x_label = x_metric

        if 'Score' in y_metric and y_data.max() > 10:
            y_data = y_data / 10
            y_label = f'{y_metric} (0-10 scale)'
        else:
            y_label = y_metric

        # Calculate bubble sizes
        if size_metric:
            size_data = df[size_metric].values
            # Normalize sizes for visualization (100-1000 point range)
            size_min, size_max = size_data.min(), size_data.max()
            if size_max > size_min:
                normalized_sizes = 100 + 900 * (size_data - size_min) / (size_max - size_min)
            else:
                normalized_sizes = np.full(len(size_data), 300)
        else:
            normalized_sizes = np.full(len(df), 200)

        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)

        # Create scatter plot
        scatter = ax.scatter(
            x_data, y_data,
            s=normalized_sizes,
            c=color_data,
            cmap=self.SCORE_COLORMAP,
            alpha=0.6,
            edgecolors='black',
            linewidth=1.5,
            vmin=0,
            vmax=10
        )

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(f'{color_metric} (0-10)', rotation=270, labelpad=20)

        # Add application labels for key outliers (top/bottom performers)
        if 'Application Name' in df.columns:
            # Label top 5 and bottom 5 by composite metric
            composite_col = 'Composite Score' if 'Composite Score' in df.columns else y_metric
            top_indices = df.nlargest(5, composite_col).index
            bottom_indices = df.nsmallest(5, composite_col).index
            label_indices = list(top_indices) + list(bottom_indices)

            for idx in label_indices:
                if idx < len(df):
                    name = df.loc[idx, 'Application Name']
                    x_val = x_data[idx]
                    y_val = y_data[idx]
                    ax.annotate(
                        name[:15] + '...' if len(name) > 15 else name,
                        (x_val, y_val),
                        xytext=(8, 8),
                        textcoords='offset points',
                        fontsize=7,
                        alpha=0.8,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', alpha=0.5)
                    )

        # Add quadrant lines (if applicable)
        x_mid = 5 if x_data.max() <= 10 else x_data.mean()
        y_mid = 5 if y_data.max() <= 10 else y_data.mean()
        ax.axhline(y=y_mid, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.axvline(x=x_mid, color='gray', linestyle='--', linewidth=1, alpha=0.5)

        # Set labels and title
        ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')

        if title is None:
            title = f'Application Priority Matrix\n{len(df)} Applications'
            if size_metric:
                title += f' (Bubble size = {size_metric})'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Add grid
        ax.grid(True, alpha=0.3, linestyle=':')

        # Add size legend if applicable
        if size_metric:
            # Create size legend
            sizes_legend = [100, 400, 900]
            size_values = [size_min, (size_min + size_max) / 2, size_max]

            legend_elements = [
                plt.scatter([], [], s=s, c='gray', alpha=0.6, edgecolors='black',
                           label=f'{size_metric}: {v:,.0f}')
                for s, v in zip(sizes_legend, size_values)
            ]

            ax.legend(
                handles=legend_elements,
                loc='upper left',
                framealpha=0.9,
                fontsize=9,
                title=f'{size_metric} Scale'
            )

        plt.tight_layout()

        # Save figure
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'priority_matrix_{timestamp}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"Priority matrix saved to: {output_path}")
        return output_path

    def create_distribution_plots(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (16, 10)
    ) -> Path:
        """
        Create distribution plots for key metrics.

        This visualization shows histograms and box plots for important scoring
        dimensions, helping identify the overall health and distribution of the
        application portfolio.

        Args:
            df: DataFrame containing application data
            output_file: Custom output filename
            metrics: List of metrics to visualize
            title: Custom title
            figsize: Figure size

        Returns:
            Path to the saved visualization
        """
        logger.info("Creating distribution plots...")

        # Default metrics if not specified
        if metrics is None:
            metrics = [
                'Business Value', 'Tech Health', 'Security',
                'Strategic Fit', 'Composite Score'
            ]

        # Filter for available metrics
        available_metrics = [m for m in metrics if m in df.columns]

        if not available_metrics:
            raise ValueError(f"None of the specified metrics found: {metrics}")

        # Create subplots
        n_metrics = len(available_metrics)
        n_cols = 3
        n_rows = (n_metrics + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if n_metrics > 1 else [axes]

        for idx, metric in enumerate(available_metrics):
            ax = axes[idx]
            data = df[metric].dropna()

            # Create histogram with KDE
            ax.hist(data, bins=20, alpha=0.7, color='skyblue', edgecolor='black')

            # Add vertical line for mean
            mean_val = data.mean()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}')

            # Add vertical line for median
            median_val = data.median()
            ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.1f}')

            ax.set_xlabel(metric, fontsize=10, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=10)
            ax.set_title(f'{metric} Distribution', fontsize=11, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3, linestyle=':')

        # Hide unused subplots
        for idx in range(n_metrics, len(axes)):
            axes[idx].set_visible(False)

        # Set overall title
        if title is None:
            title = f'Application Portfolio Metric Distributions\n({len(df)} Applications)'
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.995)

        plt.tight_layout()

        # Save figure
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'distributions_{timestamp}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"Distribution plots saved to: {output_path}")
        return output_path

    def create_time_category_summary(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8)
    ) -> Path:
        """
        Create TIME category summary visualization.

        Shows the distribution of applications across TIME categories with
        both count and percentage information. Useful for executive summaries.

        Args:
            df: DataFrame with TIME categorization
            output_file: Custom output filename
            title: Custom title
            figsize: Figure size

        Returns:
            Path to the saved visualization
        """
        logger.info("Creating TIME category summary...")

        if 'TIME Category' not in df.columns:
            raise ValueError("DataFrame must contain 'TIME Category' column")

        # Count applications by TIME category
        time_counts = df['TIME Category'].value_counts()

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Pie chart
        colors = [self.TIME_COLORS.get(cat, '#CCCCCC') for cat in time_counts.index]
        wedges, texts, autotexts = ax1.pie(
            time_counts.values,
            labels=time_counts.index,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10, 'fontweight': 'bold'}
        )

        # Make percentage text more visible
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)

        ax1.set_title('TIME Category Distribution', fontsize=12, fontweight='bold', pad=20)

        # Bar chart
        bars = ax2.bar(
            time_counts.index,
            time_counts.values,
            color=colors,
            edgecolor='black',
            linewidth=1.5
        )

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=11
            )

        ax2.set_ylabel('Number of Applications', fontsize=11, fontweight='bold')
        ax2.set_title('Application Count by Category', fontsize=12, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, linestyle=':', axis='y')
        ax2.set_axisbelow(True)

        # Rotate x-axis labels if needed
        ax2.tick_params(axis='x', rotation=45)

        # Set overall title
        if title is None:
            title = f'TIME Framework Summary ({len(df)} Total Applications)'
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)

        plt.tight_layout()

        # Save figure
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'time_summary_{timestamp}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"TIME category summary saved to: {output_path}")
        return output_path

    def create_comprehensive_dashboard(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (20, 12)
    ) -> Path:
        """
        Create a comprehensive dashboard with multiple visualizations.

        This all-in-one visualization combines several views into a single
        dashboard suitable for executive presentations. Includes TIME quadrant,
        category distribution, top/bottom applications, and key metrics.

        Args:
            df: DataFrame containing complete assessment data
            output_file: Custom output filename
            title: Custom title
            figsize: Figure size

        Returns:
            Path to the saved dashboard
        """
        logger.info("Creating comprehensive dashboard...")

        # Create figure with grid layout
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 1. TIME Quadrant (top-left, spanning 2x2)
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        self._plot_time_quadrant_on_axis(ax1, df, show_labels=False)

        # 2. TIME Category Distribution (top-right)
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_time_distribution_on_axis(ax2, df)

        # 3. Top Applications (middle-right)
        ax3 = fig.add_subplot(gs[1, 2])
        self._plot_top_apps_on_axis(ax3, df, n=5)

        # 4. Score Distribution (bottom-left)
        ax4 = fig.add_subplot(gs[2, 0])
        self._plot_score_distribution_on_axis(ax4, df)

        # 5. Key Metrics Summary (bottom-middle)
        ax5 = fig.add_subplot(gs[2, 1])
        self._plot_key_metrics_on_axis(ax5, df)

        # 6. Action Recommendations (bottom-right)
        ax6 = fig.add_subplot(gs[2, 2])
        self._plot_recommendations_on_axis(ax6, df)

        # Set overall title
        if title is None:
            title = f'Application Rationalization Dashboard - {len(df)} Applications'
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)

        # Save figure
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'dashboard_{timestamp}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()

        logger.info(f"Comprehensive dashboard saved to: {output_path}")
        return output_path

    # Helper methods for dashboard components

    def _plot_time_quadrant_on_axis(self, ax, df: pd.DataFrame, show_labels: bool = False):
        """Plot TIME quadrant on given axis."""
        if 'TIME Business Value Score' not in df.columns or 'TIME Technical Quality Score' not in df.columns:
            ax.text(0.5, 0.5, 'TIME scores not available', ha='center', va='center')
            return

        bv_scores = df['TIME Business Value Score'].values
        tq_scores = df['TIME Technical Quality Score'].values
        time_categories = df['TIME Category'].values if 'TIME Category' in df.columns else ['Unknown'] * len(df)

        # Draw quadrant backgrounds
        ax.axhspan(6, 10, xmin=0, xmax=0.5, alpha=0.1, color=self.TIME_COLORS['Tolerate'])
        ax.axhspan(6, 10, xmin=0.5, xmax=1, alpha=0.1, color=self.TIME_COLORS['Invest'])
        ax.axhspan(0, 6, xmin=0, xmax=0.5, alpha=0.1, color=self.TIME_COLORS['Eliminate'])
        ax.axhspan(0, 6, xmin=0.5, xmax=1, alpha=0.1, color=self.TIME_COLORS['Migrate'])

        # Plot applications
        for category, color in self.TIME_COLORS.items():
            mask = time_categories == category
            if mask.any():
                ax.scatter(tq_scores[mask], bv_scores[mask], c=color, label=category, s=50, alpha=0.7, edgecolors='black')

        ax.axhline(y=6, color='black', linestyle='--', linewidth=1, alpha=0.7)
        ax.axvline(x=6, color='black', linestyle='--', linewidth=1, alpha=0.7)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xlabel('Technical Quality', fontsize=10, fontweight='bold')
        ax.set_ylabel('Business Value', fontsize=10, fontweight='bold')
        ax.set_title('TIME Framework Quadrant', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(True, alpha=0.3, linestyle=':')

    def _plot_time_distribution_on_axis(self, ax, df: pd.DataFrame):
        """Plot TIME category distribution on given axis."""
        if 'TIME Category' not in df.columns:
            ax.text(0.5, 0.5, 'TIME categories not available', ha='center', va='center')
            return

        time_counts = df['TIME Category'].value_counts()
        colors = [self.TIME_COLORS.get(cat, '#CCCCCC') for cat in time_counts.index]

        ax.pie(time_counts.values, labels=time_counts.index, colors=colors,
               autopct='%1.0f%%', textprops={'fontsize': 8})
        ax.set_title('TIME Distribution', fontsize=11, fontweight='bold')

    def _plot_top_apps_on_axis(self, ax, df: pd.DataFrame, n: int = 5):
        """Plot top applications on given axis."""
        if 'Composite Score' not in df.columns or 'Application Name' not in df.columns:
            ax.text(0.5, 0.5, 'Score data not available', ha='center', va='center')
            return

        top_apps = df.nlargest(n, 'Composite Score')[['Application Name', 'Composite Score']]
        app_names = [name[:20] + '...' if len(name) > 20 else name for name in top_apps['Application Name']]

        bars = ax.barh(range(len(top_apps)), top_apps['Composite Score'], color='green', alpha=0.7, edgecolor='black')
        ax.set_yticks(range(len(top_apps)))
        ax.set_yticklabels(app_names, fontsize=8)
        ax.set_xlabel('Score', fontsize=9)
        ax.set_title(f'Top {n} Applications', fontsize=11, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, linestyle=':', axis='x')

    def _plot_score_distribution_on_axis(self, ax, df: pd.DataFrame):
        """Plot score distribution on given axis."""
        if 'Composite Score' not in df.columns:
            ax.text(0.5, 0.5, 'Score data not available', ha='center', va='center')
            return

        ax.hist(df['Composite Score'], bins=15, color='skyblue', alpha=0.7, edgecolor='black')
        mean_score = df['Composite Score'].mean()
        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_score:.1f}')
        ax.set_xlabel('Composite Score', fontsize=9)
        ax.set_ylabel('Count', fontsize=9)
        ax.set_title('Score Distribution', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, linestyle=':')

    def _plot_key_metrics_on_axis(self, ax, df: pd.DataFrame):
        """Plot key metrics summary on given axis."""
        metrics = []
        values = []

        if 'Business Value' in df.columns:
            metrics.append('Avg Business\nValue')
            values.append(df['Business Value'].mean())
        if 'Tech Health' in df.columns:
            metrics.append('Avg Tech\nHealth')
            values.append(df['Tech Health'].mean())
        if 'Security' in df.columns:
            metrics.append('Avg\nSecurity')
            values.append(df['Security'].mean())

        if metrics:
            bars = ax.bar(metrics, values, color=['#2196F3', '#4CAF50', '#FF9800'], alpha=0.7, edgecolor='black')
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
            ax.set_ylim(0, 10)
            ax.set_ylabel('Average Score', fontsize=9)
            ax.set_title('Key Metrics', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle=':', axis='y')
        else:
            ax.text(0.5, 0.5, 'Metrics not available', ha='center', va='center')

    def _plot_recommendations_on_axis(self, ax, df: pd.DataFrame):
        """Plot action recommendations on given axis."""
        if 'Action Recommendation' not in df.columns:
            ax.text(0.5, 0.5, 'Recommendations not available', ha='center', va='center')
            ax.axis('off')
            return

        rec_counts = df['Action Recommendation'].value_counts().head(5)
        colors = plt.cm.Set3(range(len(rec_counts)))

        bars = ax.barh(range(len(rec_counts)), rec_counts.values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_yticks(range(len(rec_counts)))
        ax.set_yticklabels([r[:15] + '...' if len(r) > 15 else r for r in rec_counts.index], fontsize=8)
        ax.set_xlabel('Count', fontsize=9)
        ax.set_title('Top Recommendations', fontsize=11, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, linestyle=':', axis='x')


def quick_visualize(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    viz_types: Optional[List[str]] = None
) -> Dict[str, Path]:
    """
    Quick visualization function for common use cases.

    This convenience function creates all standard visualizations from an
    assessment results file in a single call.

    Args:
        input_file: Path to CSV or Excel file with assessment results
        output_dir: Directory for output files (default: ./output/visualizations)
        viz_types: List of visualization types to create. Options:
            - 'score_heatmap': Application score heatmap
            - 'time_quadrant': TIME framework quadrant
            - 'priority_matrix': Priority bubble chart
            - 'distributions': Score distributions
            - 'time_summary': TIME category summary
            - 'dashboard': Comprehensive dashboard
            If None, creates all visualizations.

    Returns:
        Dictionary mapping visualization type to output file path

    Example:
        >>> paths = quick_visualize('results.csv', viz_types=['time_quadrant', 'dashboard'])
        >>> print(f"Dashboard saved to: {paths['dashboard']}")
    """
    # Load data
    input_path = Path(input_file)
    if input_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(input_path, engine='openpyxl')
    else:
        df = pd.read_csv(input_path)

    logger.info(f"Loaded {len(df)} applications from {input_file}")

    # Initialize visualization engine
    viz_engine = VisualizationEngine(output_dir=Path(output_dir) if output_dir else None)

    # Default to all visualizations if not specified
    if viz_types is None:
        viz_types = ['score_heatmap', 'time_quadrant', 'priority_matrix',
                    'distributions', 'time_summary', 'dashboard']

    # Create requested visualizations
    results = {}

    if 'score_heatmap' in viz_types:
        try:
            results['score_heatmap'] = viz_engine.create_score_heatmap(df)
        except Exception as e:
            logger.error(f"Failed to create score heatmap: {e}")

    if 'time_quadrant' in viz_types:
        try:
            results['time_quadrant'] = viz_engine.create_time_quadrant_heatmap(df)
        except Exception as e:
            logger.error(f"Failed to create TIME quadrant: {e}")

    if 'priority_matrix' in viz_types:
        try:
            results['priority_matrix'] = viz_engine.create_priority_matrix(df)
        except Exception as e:
            logger.error(f"Failed to create priority matrix: {e}")

    if 'distributions' in viz_types:
        try:
            results['distributions'] = viz_engine.create_distribution_plots(df)
        except Exception as e:
            logger.error(f"Failed to create distribution plots: {e}")

    if 'time_summary' in viz_types:
        try:
            results['time_summary'] = viz_engine.create_time_category_summary(df)
        except Exception as e:
            logger.error(f"Failed to create TIME summary: {e}")

    if 'dashboard' in viz_types:
        try:
            results['dashboard'] = viz_engine.create_comprehensive_dashboard(df)
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")

    logger.info(f"Created {len(results)} visualizations successfully")
    return results
