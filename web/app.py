"""
Application Rationalization Tool - Web Dashboard
A professional web interface for C-suite presentations
"""

import os
import sys
import json
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_handler import DataHandler
from src.scoring_engine import ScoringEngine, ScoringWeights
from src.recommendation_engine import RecommendationEngine
from src.time_framework import TIMEFramework, TIMEThresholds
from src.database import Database
from src.ml_engine import MLEngine
from src.scheduler import SchedulerManager
from src.compliance_engine import ComplianceEngine
from src.ai_summary import ExecutiveSummaryGenerator
from src.ai_chat import AIChatAssistant
from src.predictive_modeling import PredictiveModeler

app = Flask(__name__)
CORS(app)

# Initialize database, ML engine, compliance engine, AI summary generator, AI chat, predictive modeler, and scheduler
db = Database()
ml_engine = MLEngine()
compliance_engine = ComplianceEngine()
ai_summary_generator = ExecutiveSummaryGenerator()
ai_chat = AIChatAssistant()
predictive_modeler = PredictiveModeler()

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

# Initialize scheduler with all components
scheduler_manager = SchedulerManager(
    data_handler=data_handler,
    scoring_engine=scoring_engine,
    recommendation_engine=recommendation_engine,
    time_framework=time_framework,
    database=db
)

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

# Start scheduler
scheduler_manager.start()
logger.info("Scheduler started successfully")


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


@app.route('/history')
def history_page():
    """Historical tracking and trends page"""
    # Get recent assessments
    assessments = db.get_assessment_runs(limit=10)

    # Get portfolio trends
    trends = db.get_portfolio_trends(num_periods=12)

    # Get top improvers and decliners
    improvers = db.get_top_improvers(limit=5)
    decliners = db.get_top_decliners(limit=5)

    return render_template('history.html',
                         assessments=assessments,
                         trends=trends,
                         improvers=improvers,
                         decliners=decliners)


@app.route('/ml-insights')
def ml_insights_page():
    """ML-driven insights and recommendations page"""
    global current_data

    if current_data is None or current_data.empty:
        load_sample_data()

    # Initialize empty data structures
    clusters = None
    anomalies = None
    ml_recommendations = None

    try:
        # Get ML insights
        if current_data is not None and len(current_data) >= 10:
            try:
                clusters = ml_engine.cluster_applications(current_data, n_clusters=5)
            except Exception as e:
                logger.warning(f"Clustering failed: {e}")

            try:
                anomalies = ml_engine.detect_anomalies(current_data, contamination=0.1)
            except Exception as e:
                logger.warning(f"Anomaly detection failed: {e}")

            try:
                ml_recommendations = ml_engine.get_ml_recommendations(current_data, top_n=5)
            except Exception as e:
                logger.warning(f"ML recommendations failed: {e}")
    except Exception as e:
        logger.error(f"Failed to generate ML insights: {e}")

    return render_template('ml_insights.html',
                         clusters=clusters,
                         anomalies=anomalies,
                         ml_recommendations=ml_recommendations)


@app.route('/compliance')
def compliance_page():
    """Compliance assessment page"""
    # Get list of frameworks
    frameworks = compliance_engine.list_frameworks()
    framework_summaries = []
    for fw_name in frameworks:
        summary = compliance_engine.get_framework_summary(fw_name)
        framework_summaries.append(summary)

    return render_template('compliance.html', frameworks=framework_summaries)


@app.route('/scheduler')
def scheduler_page():
    """Scheduler management page"""
    # Get scheduler status
    status = scheduler_manager.get_scheduler_status()
    jobs = scheduler_manager.get_all_jobs()
    history = scheduler_manager.get_job_history(limit=20)

    return render_template('scheduler.html', status=status, jobs=jobs, history=history)


@app.route('/chat')
def chat_page():
    """AI Chat Assistant page"""
    return render_template('chat.html')


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

        # Save to database
        try:
            assessment_id = db.save_assessment(
                df,
                description=f"Upload: {file.filename}",
                source_file=filename
            )
        except Exception as e:
            logger.warning(f"Failed to save to database: {e}")
            assessment_id = None

        # Update global data
        current_data = df

        return jsonify({
            'success': True,
            'message': f'Successfully processed {len(df)} applications',
            'applications_count': len(df),
            'assessment_id': assessment_id
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
# HISTORICAL DATA ENDPOINTS
# ==========================

@app.route('/api/history/assessments')
def get_assessments():
    """Get list of all assessment runs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        assessments = db.get_assessment_runs(limit=limit)
        return jsonify(assessments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/assessment/<int:assessment_id>')
def get_assessment_detail(assessment_id: int):
    """Get detailed information about a specific assessment"""
    try:
        assessment = db.get_assessment_by_id(assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404

        # Get applications from this assessment
        apps_df = db.get_applications_at_run(assessment_id)
        apps_data = apps_df.to_dict('records') if not apps_df.empty else []

        return jsonify({
            'assessment': assessment,
            'applications': apps_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/application/<string:app_name>')
def get_application_history(app_name: str):
    """Get historical snapshots for a specific application"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db.get_application_history(app_name, limit=limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/trends')
def get_trends():
    """Get portfolio-level trends over time"""
    try:
        periods = request.args.get('periods', 12, type=int)
        trends = db.get_portfolio_trends(num_periods=periods)
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/improvers')
def get_top_improvers():
    """Get applications with biggest score improvements"""
    try:
        limit = request.args.get('limit', 10, type=int)
        improvers = db.get_top_improvers(limit=limit)
        return jsonify(improvers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/decliners')
def get_top_decliners():
    """Get applications with biggest score declines"""
    try:
        limit = request.args.get('limit', 10, type=int)
        decliners = db.get_top_decliners(limit=limit)
        return jsonify(decliners)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/compare/<int:id1>/<int:id2>')
def compare_assessments_api(id1: int, id2: int):
    """Compare two assessment runs"""
    try:
        comparison = db.compare_assessments(id1, id2)
        if not comparison:
            return jsonify({'error': 'One or both assessments not found'}), 404
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/score-changes')
def get_score_changes():
    """Get recent score changes"""
    try:
        app_name = request.args.get('application')
        limit = request.args.get('limit', 20, type=int)
        changes = db.get_score_trends(application_name=app_name, limit=limit)
        return jsonify(changes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================
# ML/AI ENDPOINTS
# ==========================

@app.route('/api/ai/summary', methods=['GET'])
def get_ai_summary():
    """Generate AI executive summary from portfolio data"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        summary = ai_summary_generator.generate_full_summary(current_data)
        return jsonify(summary)
    except Exception as e:
        logger.error(f"AI summary generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'overview': 'Error generating summary',
            'narrative': f'An error occurred: {str(e)}',
            'insights': [],
            'recommendations': []
        }), 500


@app.route('/api/ai/chat', methods=['POST'])
def chat_query():
    """Process natural language chat query about portfolio"""
    global current_data

    try:
        data = request.json
        message = data.get('message', '')

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        if current_data is None or current_data.empty:
            return jsonify({
                'response': 'No portfolio data is currently loaded. Please upload data first.',
                'data': []
            }), 200

        result = ai_chat.process_chat(message, current_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        return jsonify({
            'response': f'An error occurred: {str(e)}',
            'data': []
        }), 500


@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Generate predictive cost and risk analysis"""
    global current_data

    try:
        if current_data is None or current_data.empty:
            return jsonify({'error': 'No data loaded'}), 400

        predictions = predictive_modeler.generate_predictions(current_data)
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Predictions error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml/clusters')
def get_ml_clusters():
    """Get application clusters using ML"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        n_clusters = request.args.get('clusters', 5, type=int)
        results = ml_engine.cluster_applications(current_data, n_clusters=n_clusters)
        return jsonify(results)
    except Exception as e:
        logger.error(f"ML clustering error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml/anomalies')
def get_ml_anomalies():
    """Detect anomalous applications using ML"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        contamination = request.args.get('contamination', 0.1, type=float)
        results = ml_engine.detect_anomalies(current_data, contamination=contamination)
        return jsonify(results)
    except Exception as e:
        logger.error(f"ML anomaly detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml/predict/<string:app_name>')
def get_ml_prediction(app_name: str):
    """Predict trends for a specific application"""
    try:
        # Get historical data for this application
        history = db.get_application_history(app_name, limit=20)

        if not history or len(history) < 3:
            return jsonify({
                'error': 'Insufficient historical data for prediction',
                'minimum_required': 3,
                'available': len(history) if history else 0
            }), 400

        # Generate prediction
        prediction = ml_engine.predict_trends(history, app_name)
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"ML prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml/recommendations')
def get_ml_recommendations():
    """Get ML-enhanced recommendations"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        top_n = request.args.get('top_n', 10, type=int)
        results = ml_engine.get_ml_recommendations(current_data, top_n=top_n)
        return jsonify(results)
    except Exception as e:
        logger.error(f"ML recommendations error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ml/insights')
def get_ml_insights():
    """Get comprehensive ML insights"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        # Run all ML analyses
        insights = {}

        # Clustering
        try:
            insights['clusters'] = ml_engine.cluster_applications(current_data, n_clusters=5)
        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
            insights['clusters'] = None

        # Anomaly detection
        try:
            insights['anomalies'] = ml_engine.detect_anomalies(current_data, contamination=0.1)
        except Exception as e:
            logger.warning(f"Anomaly detection failed: {e}")
            insights['anomalies'] = None

        # ML recommendations
        try:
            insights['recommendations'] = ml_engine.get_ml_recommendations(current_data, top_n=5)
        except Exception as e:
            logger.warning(f"ML recommendations failed: {e}")
            insights['recommendations'] = None

        return jsonify(insights)
    except Exception as e:
        logger.error(f"ML insights error: {e}")
        return jsonify({'error': str(e)}), 500


# ==========================
# SCHEDULER API ENDPOINTS
# ==========================

@app.route('/api/scheduler/status')
def get_scheduler_status():
    """Get scheduler status and statistics"""
    try:
        status = scheduler_manager.get_scheduler_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Scheduler status error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/jobs', methods=['GET'])
def list_scheduled_jobs():
    """List all scheduled jobs"""
    try:
        jobs = scheduler_manager.get_all_jobs()
        return jsonify({'jobs': jobs})
    except Exception as e:
        logger.error(f"List jobs error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/jobs', methods=['POST'])
def create_scheduled_job():
    """Create a new scheduled job"""
    try:
        data = request.json

        job_id = data.get('job_id')
        file_path = data.get('file_path')
        schedule_type = data.get('schedule_type', 'cron')
        description = data.get('description')

        if not job_id or not file_path:
            return jsonify({'error': 'job_id and file_path are required'}), 400

        # Get schedule parameters
        if schedule_type == 'cron':
            cron_expression = data.get('cron_expression', {'hour': '9', 'minute': '0'})
            success = scheduler_manager.schedule_assessment(
                job_id=job_id,
                file_path=file_path,
                schedule_type='cron',
                cron_expression=cron_expression,
                description=description
            )
        elif schedule_type == 'interval':
            interval_minutes = data.get('interval_minutes', 60)
            success = scheduler_manager.schedule_assessment(
                job_id=job_id,
                file_path=file_path,
                schedule_type='interval',
                interval_minutes=interval_minutes,
                description=description
            )
        else:
            return jsonify({'error': 'Invalid schedule_type'}), 400

        if success:
            return jsonify({'success': True, 'message': f'Job {job_id} created successfully'})
        else:
            return jsonify({'error': 'Failed to create job'}), 500

    except Exception as e:
        logger.error(f"Create job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/jobs/<string:job_id>', methods=['DELETE'])
def delete_scheduled_job(job_id: str):
    """Delete a scheduled job"""
    try:
        success = scheduler_manager.remove_job(job_id)
        if success:
            return jsonify({'success': True, 'message': f'Job {job_id} deleted'})
        else:
            return jsonify({'error': 'Failed to delete job'}), 500
    except Exception as e:
        logger.error(f"Delete job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/jobs/<string:job_id>/run', methods=['POST'])
def run_job_now(job_id: str):
    """Run a job immediately"""
    try:
        success = scheduler_manager.run_job_now(job_id)
        if success:
            return jsonify({'success': True, 'message': f'Job {job_id} triggered'})
        else:
            return jsonify({'error': 'Failed to run job'}), 500
    except Exception as e:
        logger.error(f"Run job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/jobs/<string:job_id>/pause', methods=['POST'])
def pause_job(job_id: str):
    """Pause a scheduled job"""
    try:
        success = scheduler_manager.pause_job(job_id)
        if success:
            return jsonify({'success': True, 'message': f'Job {job_id} paused'})
        else:
            return jsonify({'error': 'Failed to pause job'}), 500
    except Exception as e:
        logger.error(f"Pause job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/jobs/<string:job_id>/resume', methods=['POST'])
def resume_job(job_id: str):
    """Resume a paused job"""
    try:
        success = scheduler_manager.resume_job(job_id)
        if success:
            return jsonify({'success': True, 'message': f'Job {job_id} resumed'})
        else:
            return jsonify({'error': 'Failed to resume job'}), 500
    except Exception as e:
        logger.error(f"Resume job error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scheduler/history')
def get_job_history():
    """Get job execution history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = scheduler_manager.get_job_history(limit=limit)
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"Job history error: {e}")
        return jsonify({'error': str(e)}), 500


# ==========================
# COMPLIANCE API ENDPOINTS
# ==========================

@app.route('/api/compliance/frameworks')
def list_compliance_frameworks():
    """List all available compliance frameworks"""
    try:
        frameworks = compliance_engine.list_frameworks()
        framework_details = []
        for fw_name in frameworks:
            summary = compliance_engine.get_framework_summary(fw_name)
            framework_details.append(summary)
        return jsonify({'frameworks': framework_details})
    except Exception as e:
        logger.error(f"List frameworks error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance/frameworks/<string:framework_name>')
def get_framework_details(framework_name: str):
    """Get details for a specific framework"""
    try:
        framework_name = framework_name.upper()
        details = compliance_engine.get_framework_summary(framework_name)
        if 'error' in details:
            return jsonify(details), 404
        return jsonify(details)
    except Exception as e:
        logger.error(f"Framework details error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance/assess', methods=['POST'])
def assess_compliance():
    """Assess application(s) against a compliance framework"""
    global current_data

    try:
        data = request.json
        framework_name = data.get('framework', 'SOX').upper()
        app_name = data.get('application_name')
        compliance_data = data.get('compliance_data')

        if app_name:
            # Single application assessment
            if not compliance_data:
                return jsonify({'error': 'compliance_data required for single app assessment'}), 400

            result = compliance_engine.assess_application_compliance(
                app_name=app_name,
                framework_name=framework_name,
                compliance_data=compliance_data
            )
            return jsonify(result)
        else:
            # Batch assessment
            if current_data is None or current_data.empty:
                return jsonify({'error': 'No data loaded'}), 404

            # Use heuristics if no mapping provided
            compliance_mapping = data.get('compliance_mapping')

            df_result = compliance_engine.batch_assess_compliance(
                df=current_data,
                framework_name=framework_name,
                compliance_mapping=compliance_mapping
            )

            # Return summary
            compliance_col = f'{framework_name}_Compliance_Score'
            summary = {
                'framework': framework_name,
                'total_applications': len(df_result),
                'avg_compliance': float(df_result[compliance_col].mean()),
                'min_compliance': float(df_result[compliance_col].min()),
                'max_compliance': float(df_result[compliance_col].max()),
                'applications': df_result[[
                    'Application Name',
                    compliance_col,
                    f'{framework_name}_Compliance_Level',
                    f'{framework_name}_Risk_Level',
                    f'{framework_name}_Gap_Count'
                ]].to_dict('records')
            }

            return jsonify(summary)

    except Exception as e:
        logger.error(f"Compliance assessment error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance/gap-analysis', methods=['POST'])
def generate_gap_analysis():
    """Generate gap analysis report for portfolio"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        data = request.json if request.json else {}
        framework_name = data.get('framework', 'SOX').upper()
        compliance_mapping = data.get('compliance_mapping')

        report = compliance_engine.generate_gap_analysis_report(
            df=current_data,
            framework_name=framework_name,
            compliance_mapping=compliance_mapping
        )

        return jsonify(report)

    except Exception as e:
        logger.error(f"Gap analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance/portfolio')
def get_portfolio_compliance():
    """Get compliance overview for all frameworks"""
    global current_data

    if current_data is None or current_data.empty:
        return jsonify({'error': 'No data loaded'}), 404

    try:
        frameworks = compliance_engine.list_frameworks()
        overview = {}

        for framework_name in frameworks:
            # Quick assessment using heuristics
            df_result = compliance_engine.batch_assess_compliance(
                df=current_data,
                framework_name=framework_name
            )

            compliance_col = f'{framework_name}_Compliance_Score'
            overview[framework_name] = {
                'avg_compliance': float(df_result[compliance_col].mean()),
                'compliant_apps': len(df_result[df_result[f'{framework_name}_Compliance_Level'] == 'Fully Compliant']),
                'non_compliant_apps': len(df_result[df_result[f'{framework_name}_Compliance_Level'] == 'Non-Compliant']),
                'critical_risk_apps': len(df_result[df_result[f'{framework_name}_Risk_Level'] == 'Critical'])
            }

        return jsonify({
            'total_applications': len(current_data),
            'frameworks': overview
        })

    except Exception as e:
        logger.error(f"Portfolio compliance error: {e}")
        return jsonify({'error': str(e)}), 500


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
