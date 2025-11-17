"""
Application Rationalization Tool - Web Dashboard
A professional web interface for C-suite presentations
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import io
import base64

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine, ScoringWeights
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework, TIMEThresholds

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize components
data_handler = DataHandler()
scoring_engine = ScoringEngine()
recommendation_engine = RecommendationEngine()
time_framework = TIMEFramework()

# Global variable to store current assessment data
current_data = None


def load_sample_data():
    """Load sample data for demo purposes"""
    global current_data
    try:
        sample_file = Path(__file__).parent.parent / 'data' / 'assessment_template.csv'
        if sample_file.exists():
            current_data = data_handler.read_csv(str(sample_file))
            # Process the data
            current_data = scoring_engine.batch_calculate_scores(current_data)
            current_data = recommendation_engine.batch_generate_recommendations(current_data)
            current_data = time_framework.batch_categorize(current_data)
            return True
    except Exception as e:
        import traceback
        print(f"Error loading sample data: {e}")
        print(traceback.format_exc())
        # Still load the raw data even if processing fails
        try:
            sample_file = Path(__file__).parent.parent / 'data' / 'assessment_template.csv'
            if sample_file.exists():
                current_data = data_handler.read_csv(str(sample_file))
        except:
            pass
        return False
    return False


# Load sample data on startup
load_sample_data()


def get_portfolio_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate executive summary statistics"""
    if df is None or df.empty:
        return {}

    return {
        'total_applications': len(df),
        'total_cost': float(df['Cost'].sum()),
        'avg_composite_score': float(df['Composite Score'].mean()) if 'Composite Score' in df.columns else 0,
        'avg_business_value': float(df['Business Value'].mean()),
        'avg_tech_health': float(df['Tech Health'].mean()),
        'high_risk_count': len(df[df['Composite Score'] < 40]) if 'Composite Score' in df.columns else 0,
        'retire_candidates': len(df[df['Action Recommendation'] == 'Retire']) if 'Action Recommendation' in df.columns else 0,
        'invest_candidates': len(df[df['Action Recommendation'] == 'Invest']) if 'Action Recommendation' in df.columns else 0,
        'migrate_candidates': len(df[df['Action Recommendation'] == 'Migrate']) if 'Action Recommendation' in df.columns else 0,
        'maintain_candidates': len(df[df['Action Recommendation'] == 'Maintain']) if 'Action Recommendation' in df.columns else 0,
        'recommendations': df['Action Recommendation'].value_counts().to_dict() if 'Action Recommendation' in df.columns else {},
        'time_categories': df['TIME Category'].value_counts().to_dict() if 'TIME Category' in df.columns else {}
    }


def create_executive_charts(df: pd.DataFrame) -> Dict[str, str]:
    """Create interactive Plotly charts for executive dashboard"""
    charts = {}

    if df is None or df.empty or 'Composite Score' not in df.columns:
        return charts

    # 1. Composite Score Distribution
    fig_dist = px.histogram(
        df,
        x='Composite Score',
        nbins=20,
        title='Application Score Distribution',
        labels={'Composite Score': 'Composite Score', 'count': 'Number of Applications'},
        color_discrete_sequence=['#3B82F6']
    )
    fig_dist.update_layout(
        template='plotly_white',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    charts['score_distribution'] = json.dumps(fig_dist, cls=plotly.utils.PlotlyJSONEncoder)

    # 2. Recommendation Breakdown (Pie Chart)
    if 'Action Recommendation' in df.columns:
        recommendation_counts = df['Action Recommendation'].value_counts()
        colors = {
            'Retain': '#10B981',
            'Invest': '#3B82F6',
            'Maintain': '#F59E0B',
            'Tolerate': '#EF4444',
            'Migrate': '#8B5CF6',
            'Consolidate': '#EC4899',
            'Retire': '#DC2626',
            'Immediate Action Required': '#991B1B'
        }
        fig_pie = go.Figure(data=[go.Pie(
            labels=recommendation_counts.index,
            values=recommendation_counts.values,
            marker=dict(colors=[colors.get(label, '#6B7280') for label in recommendation_counts.index]),
            hole=0.4
        )])
        fig_pie.update_layout(
            title='Recommendations Breakdown',
            template='plotly_white',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['recommendations_pie'] = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)

    # 3. Business Value vs Tech Health Scatter
    fig_scatter = px.scatter(
        df,
        x='Tech Health',
        y='Business Value',
        size='Cost',
        color='Action Recommendation' if 'Action Recommendation' in df.columns else None,
        hover_data=['Application Name', 'Composite Score'] if 'Composite Score' in df.columns else ['Application Name'],
        title='Business Value vs Technical Health',
        labels={'Tech Health': 'Technical Health', 'Business Value': 'Business Value'}
    )
    fig_scatter.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    charts['value_vs_health'] = json.dumps(fig_scatter, cls=plotly.utils.PlotlyJSONEncoder)

    # 4. TIME Framework Quadrant
    if all(col in df.columns for col in ['TIME Category', 'TIME Business Value Score', 'TIME Technical Quality Score']):
        fig_time = px.scatter(
            df,
            x='TIME Technical Quality Score',
            y='TIME Business Value Score',
            color='TIME Category',
            hover_data=['Application Name', 'Composite Score', 'Action Recommendation'],
            title='TIME Framework Analysis',
            labels={
                'TIME Technical Quality Score': 'Technical Quality →',
                'TIME Business Value Score': 'Business Value →'
            }
        )

        # Add quadrant lines
        fig_time.add_hline(y=6.0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_time.add_vline(x=6.0, line_dash="dash", line_color="gray", opacity=0.5)

        # Add quadrant labels
        fig_time.add_annotation(x=3, y=8, text="TOLERATE", showarrow=False, font=dict(size=12, color="gray"))
        fig_time.add_annotation(x=8, y=8, text="INVEST", showarrow=False, font=dict(size=12, color="gray"))
        fig_time.add_annotation(x=3, y=3, text="ELIMINATE", showarrow=False, font=dict(size=12, color="gray"))
        fig_time.add_annotation(x=8, y=3, text="MIGRATE", showarrow=False, font=dict(size=12, color="gray"))

        fig_time.update_layout(
            template='plotly_white',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        charts['time_framework'] = json.dumps(fig_time, cls=plotly.utils.PlotlyJSONEncoder)

    # 5. Top 10 Highest Cost Applications
    top_cost = df.nlargest(10, 'Cost')[['Application Name', 'Cost', 'Composite Score']] if 'Composite Score' in df.columns else df.nlargest(10, 'Cost')[['Application Name', 'Cost']]
    fig_cost = go.Figure(data=[
        go.Bar(
            x=top_cost['Application Name'],
            y=top_cost['Cost'],
            marker_color=['#EF4444' if 'Composite Score' in top_cost.columns and score < 50 else '#F59E0B' if 'Composite Score' in top_cost.columns and score < 70 else '#10B981'
                          for score in (top_cost['Composite Score'] if 'Composite Score' in top_cost.columns else [75]*len(top_cost))],
            text=top_cost['Cost'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside'
        )
    ])
    fig_cost.update_layout(
        title='Top 10 Highest Cost Applications',
        xaxis_title='Application',
        yaxis_title='Annual Cost ($)',
        template='plotly_white',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis={'tickangle': -45}
    )
    charts['top_cost'] = json.dumps(fig_cost, cls=plotly.utils.PlotlyJSONEncoder)

    return charts


# ==========================
# ROUTES
# ==========================

@app.route('/')
def index():
    """Redirect to dashboard"""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Executive dashboard page"""
    global current_data

    if current_data is None or current_data.empty:
        load_sample_data()

    summary = get_portfolio_summary(current_data) if current_data is not None else {}
    charts = create_executive_charts(current_data) if current_data is not None else {}

    # Prepare data in format expected by template
    kpis = {
        'total_apps': summary.get('total_applications', 0),
        'avg_score': summary.get('avg_composite_score', 0),
        'total_cost': summary.get('total_cost', 0),
        'high_risk_count': summary.get('high_risk_count', 0)
    }

    actions = {
        'retire': summary.get('retire_candidates', 0),
        'invest': summary.get('invest_candidates', 0),
        'migrate': summary.get('migrate_candidates', 0),
        'maintain': summary.get('maintain_candidates', 0)
    }

    return render_template('dashboard.html', kpis=kpis, actions=actions, charts=charts)


@app.route('/portfolio')
def portfolio():
    """Application portfolio table view"""
    global current_data

    if current_data is None or current_data.empty:
        load_sample_data()

    # Convert DataFrame to dict for template
    apps_data = []
    if current_data is not None:
        for _, row in current_data.iterrows():
            apps_data.append({
                'application_name': row['Application Name'],
                'owner': row.get('Owner', 'N/A'),
                'business_value': float(row['Business Value']),
                'technical_health': float(row['Tech Health']),
                'cost': float(row['Cost']),
                'final_score': float(row.get('Composite Score', 0)),
                'recommendation': row.get('Action Recommendation', 'N/A'),
                'time_category': row.get('TIME Category', 'N/A')
            })

    return render_template('portfolio.html', applications=apps_data)


@app.route('/time-framework')
def time_framework_page():
    """TIME Framework visualization page"""
    global current_data

    if current_data is None or current_data.empty:
        load_sample_data()

    charts = create_executive_charts(current_data) if current_data is not None else {}

    # Get TIME category breakdown
    stats = {}
    if current_data is not None and 'TIME Category' in current_data.columns:
        time_counts = current_data['TIME Category'].value_counts()
        stats = {
            'invest': int(time_counts.get('Invest', 0)),
            'tolerate': int(time_counts.get('Tolerate', 0)),
            'migrate': int(time_counts.get('Migrate', 0)),
            'eliminate': int(time_counts.get('Eliminate', 0))
        }

    # Get the TIME framework chart
    chart = charts.get('time_framework', '{}')

    return render_template('time_framework.html', chart=chart, stats=stats)


@app.route('/reports')
def reports():
    """Reports and exports page"""
    return render_template('reports.html')


@app.route('/upload')
def upload_page():
    """Data upload page"""
    return render_template('upload.html')


# ==========================
# API ENDPOINTS
# ==========================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process assessment"""
    global current_data

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save file
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read and process data
        if filepath.endswith('.csv'):
            df = data_handler.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = data_handler.read_excel(filepath)
        else:
            return jsonify({'error': 'Invalid file format. Please upload CSV or Excel file.'}), 400

        # Validate data
        is_valid, validation_errors = data_handler.validate_data(df)
        if not is_valid:
            return jsonify({'error': 'Data validation failed', 'details': validation_errors}), 400

        # Process data
        df = scoring_engine.batch_calculate_scores(df)
        df = recommendation_engine.batch_generate_recommendations(df)
        df = time_framework.batch_categorize(df)

        # Update global data
        current_data = df

        return jsonify({
            'success': True,
            'message': f'Successfully processed {len(df)} applications',
            'applications_count': len(df)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary')
def api_summary():
    """Get portfolio summary statistics"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    summary = get_portfolio_summary(current_data)
    return jsonify(summary)


@app.route('/api/applications')
def api_applications():
    """Get all applications data"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    # Convert to dict
    data = current_data.to_dict('records')

    # Apply filters if provided
    recommendation = request.args.get('recommendation')
    time_category = request.args.get('time_category')
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)

    if recommendation:
        data = [d for d in data if d.get('Action Recommendation') == recommendation]
    if time_category:
        data = [d for d in data if d.get('TIME Category') == time_category]
    if min_score is not None:
        data = [d for d in data if d.get('Composite Score', 0) >= min_score]
    if max_score is not None:
        data = [d for d in data if d.get('Composite Score', 100) <= max_score]

    return jsonify(data)


@app.route('/api/export/csv')
def export_csv():
    """Export current data as CSV"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    # Create CSV in memory
    output = io.StringIO()
    current_data.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'assessment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@app.route('/api/export/excel')
def export_excel():
    """Export current data as Excel"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    # Create Excel in memory
    output = io.BytesIO()
    filename = f'assessment_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

    temp_file = f'/tmp/{filename}'
    data_handler.write_excel(current_data, temp_file)

    with open(temp_file, 'rb') as f:
        output.write(f.read())
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': current_data is not None and not current_data.empty,
        'applications_count': len(current_data) if current_data is not None else 0
    })


# ==========================
# MAIN
# ==========================

if __name__ == '__main__':
    print("=" * 60)
    print("Application Rationalization Tool - Web Dashboard")
    print("=" * 60)
    print("\n🚀 Starting server...")
    print(f"📊 Dashboard URL: http://localhost:5000")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
