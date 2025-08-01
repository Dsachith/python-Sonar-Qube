import os
import datetime  # Added this import
from typing import Dict, List, DefaultDict
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader
import plotly.graph_objects as go
from collections import defaultdict
from config.settings import TEMPLATES_DIR, OUTPUT_DIR

def generate_report(analysis_results: Dict[str, dict], output_path: str):
    # Prepare data for visualizations
    summary_data = _prepare_summary_data(analysis_results)
    file_metrics = _prepare_file_metrics(analysis_results)
    
    # Create visualizations
    charts = {
        'issue_distribution': _create_issue_distribution_chart(summary_data),
        'issue_by_file': _create_issue_by_file_chart(file_metrics),
        'metrics_radar': _create_metrics_radar_chart(file_metrics),
    }
    
    # Render HTML report
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('report_template.html')
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template.render(
            summary=summary_data,
            file_metrics=file_metrics,
            charts=charts,
            analysis_results=analysis_results,
            now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

def _prepare_summary_data(analysis_results: Dict[str, dict]) -> dict:
    total_issues = 0
    issue_types = defaultdict(int)
    
    for file_analysis in analysis_results.values():
        for issue in file_analysis.issues:
            issue_types[issue.issue_type] += 1
            total_issues += 1
    
    return {
        'total_files': len(analysis_results),
        'total_issues': total_issues,
        'issue_types': dict(issue_types),
    }

def _prepare_file_metrics(analysis_results: Dict[str, dict]) -> List[dict]:
    file_metrics = []
    
    for file_path, analysis in analysis_results.items():
        metrics = analysis.metrics
        file_metrics.append({
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'total_lines': metrics['total_lines'],
            'code_lines': metrics['code_lines'],
            'comment_lines': metrics['comment_lines'],
            'comment_density': metrics['comment_density'],
            'issues': len(analysis.issues),
            'issue_types': {issue.issue_type for issue in analysis.issues},
        })
    
    return file_metrics

def _create_issue_distribution_chart(summary_data: dict) -> str:
    fig = go.Figure()
    
    issue_types = summary_data['issue_types']
    
    fig.add_trace(go.Pie(
        labels=list(issue_types.keys()),
        values=list(issue_types.values()),
        hole=0.3,
        textinfo='label+percent',
    ))
    
    fig.update_layout(
        title='Issue Type Distribution',
        margin=dict(t=40, b=0, l=0, r=0),
    )
    
    return fig.to_html(full_html=False)

def _create_issue_by_file_chart(file_metrics: List[dict]) -> str:
    fig = go.Figure()
    
    file_names = [m['file_name'] for m in file_metrics]
    issues_count = [m['issues'] for m in file_metrics]
    
    fig.add_trace(go.Bar(
        x=file_names,
        y=issues_count,
        text=issues_count,
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Issues by File',
        xaxis_title='File',
        yaxis_title='Number of Issues',
    )
    
    return fig.to_html(full_html=False)

def _create_metrics_radar_chart(file_metrics: List[dict]) -> str:
    fig = go.Figure()
    
    # Select a few representative files to avoid clutter
    sample_files = file_metrics[:min(5, len(file_metrics))]
    
    metrics = ['code_lines', 'comment_lines', 'comment_density', 'issues']
    
    for file_metric in sample_files:
        values = [
            file_metric['code_lines'],
            file_metric['comment_lines'],
            file_metric['comment_density'],
            file_metric['issues'] * 10,  # Scale for better visualization
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name=file_metric['file_name'],
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
            )),
        title='File Metrics Comparison',
    )
    
    return fig.to_html(full_html=False)