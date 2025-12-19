"""
Capital Projects Lifecycle Planner - Web Dashboard
A professional web interface for county engineering capital project portfolio management.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scoring_engine import ProjectScoringEngine
from src.project_health_framework import ProjectHealthFramework
from src.ai_assistant import ProjectAIAssistant, ChatResponse
from src.claude_assistant import ClaudeProjectAssistant

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Initialize engines
scoring_engine = ProjectScoringEngine()
health_framework = ProjectHealthFramework()

# Initialize AI assistants - Claude with fallback to rule-based
claude_assistant = ClaudeProjectAssistant(api_key=os.getenv("ANTHROPIC_API_KEY"))
rule_based_assistant = ProjectAIAssistant()

if claude_assistant.is_available():
    ai_assistant = claude_assistant
    logger.info("Using Claude-powered AI assistant")
else:
    ai_assistant = rule_based_assistant
    logger.info("Claude not available, using rule-based AI assistant")

# Global data store
current_data = None


def load_sample_data():
    """Load sample project data."""
    global current_data
    try:
        sample_file = Path(__file__).parent.parent / 'data' / 'sample_projects.csv'
        if sample_file.exists():
            current_data = pd.read_csv(str(sample_file))
            # Process the data
            current_data = scoring_engine.batch_score_projects(current_data)
            current_data = health_framework.batch_categorize(current_data)
            logger.info(f"Loaded {len(current_data)} projects")
            return True
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
        import traceback
        traceback.print_exc()
    return False


# Load data on startup
load_sample_data()


def get_portfolio_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate executive summary statistics for capital projects."""
    if df is None or df.empty:
        return {}

    # Calculate budget metrics
    total_budget = float(df['Total Budget'].sum())
    total_spent = float(df['Spent to Date'].sum())
    total_forecast = float(df['Forecast at Completion'].sum()) if 'Forecast at Completion' in df.columns else total_budget

    # Phase distribution
    phase_counts = df['Current Phase'].value_counts().to_dict()

    # Status distribution
    status_counts = df['Status'].value_counts().to_dict() if 'Status' in df.columns else {}

    # Projects at risk
    at_risk = 0
    if 'Project Health Score' in df.columns:
        at_risk = len(df[df['Project Health Score'] < 50])

    # Schedule issues
    schedule_issues = 0
    if 'Schedule Health' in df.columns:
        schedule_issues = len(df[df['Schedule Health'] < 50])

    # Budget issues
    budget_issues = 0
    if 'Budget Health' in df.columns:
        budget_issues = len(df[df['Budget Health'] < 50])

    # District distribution
    district_counts = df['District'].value_counts().to_dict() if 'District' in df.columns else {}

    # Type distribution
    type_counts = df['Project Type'].value_counts().to_dict() if 'Project Type' in df.columns else {}

    return {
        'total_projects': len(df),
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_forecast': total_forecast,
        'budget_variance': total_budget - total_forecast,
        'budget_variance_pct': ((total_budget - total_forecast) / total_budget * 100) if total_budget > 0 else 0,
        'avg_health_score': float(df['Project Health Score'].mean()) if 'Project Health Score' in df.columns else 0,
        'avg_strategic_value': float(df['Strategic Value Score'].mean()) if 'Strategic Value Score' in df.columns else 0,
        'avg_deliverability': float(df['Deliverability Score'].mean()) if 'Deliverability Score' in df.columns else 0,
        'projects_at_risk': at_risk,
        'schedule_issues': schedule_issues,
        'budget_issues': budget_issues,
        'phase_distribution': phase_counts,
        'status_distribution': status_counts,
        'district_distribution': district_counts,
        'type_distribution': type_counts,
        'advance_count': status_counts.get('Advance', 0),
        'monitor_count': status_counts.get('Monitor', 0),
        'rescope_count': status_counts.get('Re-scope', 0),
        'defer_count': status_counts.get('Defer', 0),
        'cancel_count': status_counts.get('Cancel', 0)
    }


def create_executive_charts(df: pd.DataFrame) -> Dict[str, str]:
    """Create interactive Plotly charts for the dashboard."""
    charts = {}

    if df is None or df.empty:
        return charts

    # Color schemes
    status_colors = {
        'Advance': '#10B981',    # Green
        'Monitor': '#F59E0B',    # Amber
        'Re-scope': '#F97316',   # Orange
        'Defer': '#6B7280',      # Gray
        'Cancel': '#EF4444'      # Red
    }

    phase_colors = px.colors.qualitative.Set3

    # 1. Project Health Score Distribution
    if 'Project Health Score' in df.columns:
        fig_health = px.histogram(
            df,
            x='Project Health Score',
            nbins=20,
            title='Project Health Score Distribution',
            labels={'Project Health Score': 'Health Score', 'count': 'Number of Projects'},
            color_discrete_sequence=['#3B82F6']
        )
        fig_health.add_vline(x=60, line_dash="dash", line_color="green", annotation_text="Healthy")
        fig_health.add_vline(x=40, line_dash="dash", line_color="red", annotation_text="At Risk")
        fig_health.update_layout(
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['health_distribution'] = json.dumps(fig_health, cls=plotly.utils.PlotlyJSONEncoder)

    # 2. Status Breakdown (Pie Chart)
    if 'Status' in df.columns:
        status_counts = df['Status'].value_counts()
        fig_status = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            marker=dict(colors=[status_colors.get(s, '#6B7280') for s in status_counts.index]),
            hole=0.4
        )])
        fig_status.update_layout(
            title='Project Status Distribution',
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['status_pie'] = json.dumps(fig_status, cls=plotly.utils.PlotlyJSONEncoder)

    # 3. Strategic Value vs Deliverability Quadrant
    if all(col in df.columns for col in ['Strategic Value Score', 'Deliverability Score', 'Status']):
        fig_quadrant = px.scatter(
            df,
            x='Deliverability Score',
            y='Strategic Value Score',
            size='Total Budget',
            color='Status',
            color_discrete_map=status_colors,
            hover_data=['Project Name', 'Project Health Score', 'Current Phase'],
            title='Strategic Value vs Deliverability',
            labels={
                'Deliverability Score': 'Deliverability (Readiness) →',
                'Strategic Value Score': 'Strategic Value →'
            }
        )
        # Add quadrant lines
        fig_quadrant.add_hline(y=65, line_dash="dash", line_color="gray", opacity=0.5)
        fig_quadrant.add_vline(x=65, line_dash="dash", line_color="gray", opacity=0.5)
        # Add quadrant labels
        fig_quadrant.add_annotation(x=32, y=82, text="RE-SCOPE", showarrow=False, font=dict(size=12, color="gray"))
        fig_quadrant.add_annotation(x=82, y=82, text="ADVANCE", showarrow=False, font=dict(size=12, color="gray"))
        fig_quadrant.add_annotation(x=32, y=25, text="DEFER/CANCEL", showarrow=False, font=dict(size=12, color="gray"))
        fig_quadrant.add_annotation(x=82, y=25, text="MONITOR", showarrow=False, font=dict(size=12, color="gray"))
        fig_quadrant.update_layout(
            template='plotly_white',
            height=450,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['quadrant'] = json.dumps(fig_quadrant, cls=plotly.utils.PlotlyJSONEncoder)

    # 4. Projects by Phase (Bar Chart)
    if 'Current Phase' in df.columns:
        phase_order = [
            'Concept/Idea', 'Feasibility/Planning', 'Design',
            'Right-of-Way Acquisition', 'Permitting/Utility Coordination',
            'Procurement/Letting', 'Active Construction',
            'Substantial Completion', 'Final Acceptance/Closeout',
            'Post-Completion/Warranty'
        ]
        phase_counts = df['Current Phase'].value_counts()
        # Reorder
        phase_counts = phase_counts.reindex([p for p in phase_order if p in phase_counts.index])

        fig_phase = go.Figure(data=[
            go.Bar(
                x=phase_counts.index,
                y=phase_counts.values,
                marker_color='#3B82F6'
            )
        ])
        fig_phase.update_layout(
            title='Projects by Lifecycle Phase',
            xaxis_title='Phase',
            yaxis_title='Number of Projects',
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=80),
            xaxis={'tickangle': -45}
        )
        charts['phase_bar'] = json.dumps(fig_phase, cls=plotly.utils.PlotlyJSONEncoder)

    # 5. Top 10 Projects by Budget
    top_budget = df.nlargest(10, 'Total Budget')[['Project Name', 'Total Budget', 'Project Health Score', 'Status']]
    fig_budget = go.Figure(data=[
        go.Bar(
            x=top_budget['Project Name'],
            y=top_budget['Total Budget'],
            marker_color=[
                status_colors.get(s, '#6B7280') for s in top_budget['Status']
            ] if 'Status' in top_budget.columns else '#3B82F6',
            text=top_budget['Total Budget'].apply(lambda x: f'${x/1e6:.1f}M'),
            textposition='outside'
        )
    ])
    fig_budget.update_layout(
        title='Top 10 Projects by Budget',
        xaxis_title='Project',
        yaxis_title='Total Budget ($)',
        template='plotly_white',
        height=350,
        margin=dict(l=20, r=20, t=40, b=100),
        xaxis={'tickangle': -45}
    )
    charts['top_budget'] = json.dumps(fig_budget, cls=plotly.utils.PlotlyJSONEncoder)

    # 6. Budget by District
    if 'District' in df.columns:
        district_budget = df.groupby('District')['Total Budget'].sum().sort_index()
        fig_district = go.Figure(data=[
            go.Bar(
                x=[f'District {d}' for d in district_budget.index],
                y=district_budget.values,
                marker_color='#8B5CF6',
                text=[f'${v/1e6:.1f}M' for v in district_budget.values],
                textposition='outside'
            )
        ])
        fig_district.update_layout(
            title='Total Budget by Commissioner District',
            xaxis_title='District',
            yaxis_title='Total Budget ($)',
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['district_budget'] = json.dumps(fig_district, cls=plotly.utils.PlotlyJSONEncoder)

    # 7. Schedule vs Budget Health
    if all(col in df.columns for col in ['Schedule Health', 'Budget Health']):
        fig_health_scatter = px.scatter(
            df,
            x='Budget Health',
            y='Schedule Health',
            color='Status',
            color_discrete_map=status_colors,
            hover_data=['Project Name', 'Percent Complete'],
            title='Schedule Health vs Budget Health'
        )
        fig_health_scatter.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.5)
        fig_health_scatter.add_vline(x=50, line_dash="dash", line_color="red", opacity=0.5)
        fig_health_scatter.update_layout(
            template='plotly_white',
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['health_scatter'] = json.dumps(fig_health_scatter, cls=plotly.utils.PlotlyJSONEncoder)

    # 8. Project Type Distribution
    if 'Project Type' in df.columns:
        type_counts = df['Project Type'].value_counts()
        fig_type = go.Figure(data=[go.Pie(
            labels=type_counts.index,
            values=type_counts.values,
            hole=0.3
        )])
        fig_type.update_layout(
            title='Projects by Type',
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['type_pie'] = json.dumps(fig_type, cls=plotly.utils.PlotlyJSONEncoder)

    return charts


# ==========================
# ROUTES
# ==========================

@app.route('/')
def index():
    """Redirect to dashboard."""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Executive dashboard page."""
    global current_data

    if current_data is None or current_data.empty:
        load_sample_data()

    summary = get_portfolio_summary(current_data) if current_data is not None else {}
    charts = create_executive_charts(current_data) if current_data is not None else {}

    return render_template('dashboard.html',
                          summary=summary,
                          charts=charts,
                          title='Capital Projects Dashboard')


@app.route('/portfolio')
def portfolio():
    """Project portfolio list view."""
    global current_data

    if current_data is None:
        load_sample_data()

    projects = current_data.to_dict('records') if current_data is not None else []
    return render_template('portfolio.html',
                          projects=projects,
                          title='Project Portfolio')


@app.route('/project/<project_id>')
def project_detail(project_id):
    """Individual project detail view."""
    global current_data

    if current_data is None:
        load_sample_data()

    project = None
    if current_data is not None:
        matches = current_data[current_data['Project ID'] == project_id]
        if not matches.empty:
            project = matches.iloc[0].to_dict()

    if project is None:
        return "Project not found", 404

    return render_template('project_detail.html',
                          project=project,
                          title=project.get('Project Name', 'Project Detail'))


@app.route('/health-framework')
def health_framework_view():
    """Project health framework quadrant view."""
    global current_data

    if current_data is None:
        load_sample_data()

    summary = get_portfolio_summary(current_data) if current_data is not None else {}
    charts = create_executive_charts(current_data) if current_data is not None else {}
    projects = current_data.to_dict('records') if current_data is not None else []

    return render_template('health_framework.html',
                          summary=summary,
                          charts=charts,
                          projects=projects,
                          title='Project Health Framework')


@app.route('/api/projects')
def api_projects():
    """API endpoint for project data."""
    global current_data

    if current_data is None:
        return jsonify([])

    return jsonify(current_data.to_dict('records'))


@app.route('/api/summary')
def api_summary():
    """API endpoint for portfolio summary."""
    global current_data

    if current_data is None:
        return jsonify({})

    return jsonify(get_portfolio_summary(current_data))


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    global current_data

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            current_data = pd.read_csv(file)
            current_data = scoring_engine.batch_score_projects(current_data)
            current_data = health_framework.batch_categorize(current_data)
            return jsonify({
                'success': True,
                'message': f'Loaded {len(current_data)} projects',
                'count': len(current_data)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/export')
def export_data():
    """Export current data as CSV."""
    global current_data

    if current_data is None:
        return jsonify({'error': 'No data available'}), 400

    output = current_data.to_csv(index=False)
    return send_file(
        __import__('io').BytesIO(output.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'capital_projects_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@app.route('/api/chat', methods=['POST'])
def chat():
    """AI Chat endpoint for project Q&A."""
    global current_data

    if current_data is None:
        load_sample_data()

    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        response = ai_assistant.process_query(query, current_data)

        # Convert projects to serializable format
        projects_list = []
        for proj in response.projects[:10]:  # Limit to 10 projects
            # Handle NaN values
            clean_proj = {}
            for k, v in proj.items():
                if pd.isna(v):
                    clean_proj[k] = None
                else:
                    clean_proj[k] = v
            projects_list.append(clean_proj)

        return jsonify({
            'message': response.message,
            'projects': projects_list,
            'key_points': response.key_points,
            'follow_up_prompt': response.follow_up_prompt,
            'filter_params': response.filter_params,
            'show_details_prompt': response.show_details_prompt
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/chat')
def chat_page():
    """AI Chat interface page."""
    global current_data

    if current_data is None:
        load_sample_data()

    summary = get_portfolio_summary(current_data) if current_data is not None else {}

    return render_template('chat.html',
                          summary=summary,
                          title='AI Assistant')


@app.route('/filtered-view')
def filtered_view():
    """Dynamic filtered view based on query parameters."""
    global current_data

    if current_data is None:
        load_sample_data()

    # Get filter parameters
    status = request.args.get('status')
    phase = request.args.get('phase')
    district = request.args.get('district')
    min_health = request.args.get('min_health', type=float)
    max_health = request.args.get('max_health', type=float)
    project_type = request.args.get('type')

    filtered = current_data.copy()
    filter_description = []

    if status:
        if ',' in status:
            statuses = status.split(',')
            filtered = filtered[filtered['Status'].isin(statuses)]
            filter_description.append(f"Status: {', '.join(statuses)}")
        else:
            filtered = filtered[filtered['Status'] == status]
            filter_description.append(f"Status: {status}")

    if phase:
        filtered = filtered[filtered['Current Phase'] == phase]
        filter_description.append(f"Phase: {phase}")

    if district:
        filtered = filtered[filtered['District'] == int(district)]
        filter_description.append(f"District: {district}")

    if min_health:
        filtered = filtered[filtered['Project Health Score'] >= min_health]
        filter_description.append(f"Health >= {min_health}")

    if max_health:
        filtered = filtered[filtered['Project Health Score'] <= max_health]
        filter_description.append(f"Health <= {max_health}")

    if project_type:
        filtered = filtered[filtered['Project Type'] == project_type]
        filter_description.append(f"Type: {project_type}")

    projects = filtered.to_dict('records')
    summary = get_portfolio_summary(filtered)
    charts = create_executive_charts(filtered)

    return render_template('filtered_view.html',
                          projects=projects,
                          summary=summary,
                          charts=charts,
                          filter_description=' | '.join(filter_description) if filter_description else 'All Projects',
                          title='Filtered View')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
