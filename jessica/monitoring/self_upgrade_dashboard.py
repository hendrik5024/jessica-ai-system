"""
Self-Upgrade Monitoring Dashboard
Web-based dashboard for visualizing Jessica's self-upgrade system.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger("jessica.monitoring.dashboard")


class MonitoringDashboard:
    """
    Web-based dashboard for monitoring and controlling Jessica's self-upgrade system.
    """

    def __init__(self, self_upgrade_manager, improvement_scheduler=None):
        self.manager = self_upgrade_manager
        self.scheduler = improvement_scheduler
        self.dashboard_path = Path("jessica/ui/self_upgrade_dashboard.html")

    def generate_dashboard_html(self) -> str:
        """
        Generate interactive HTML dashboard for monitoring.
        """
        stats = self.manager.get_improvement_statistics()
        history = self.manager.get_improvement_history(20)
        
        # Prepare data for charts
        actions_by_type = stats.get('by_action', {})
        deployment_stats = stats.get('deployment_statistics', {})
        staging_stats = stats.get('staging_status', {})

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jessica Self-Upgrade Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .status-active {{
            background: #4caf50;
            color: white;
        }}
        
        .status-idle {{
            background: #2196f3;
            color: white;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #667eea;
            font-size: 16px;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            font-size: 14px;
            color: #666;
        }}
        
        .metric-value {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 15px;
        }}
        
        .actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}
        
        button {{
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: #f0f0f0;
            color: #333;
        }}
        
        .btn-secondary:hover {{
            background: #e0e0e0;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        
        .timeline-item {{
            padding: 10px 0;
            border-left: 2px solid #667eea;
            padding-left: 15px;
            position: relative;
            margin-bottom: 15px;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            background: #667eea;
            border-radius: 50%;
            left: -6px;
            top: 15px;
        }}
        
        .timestamp {{
            font-size: 12px;
            color: #999;
        }}
        
        .action-type {{
            display: inline-block;
            padding: 3px 8px;
            background: #f0f0f0;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            header {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Jessica Self-Upgrade System Dashboard</h1>
            <div>
                <span class="status-badge status-active">Active</span>
                <span class="status-badge">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
        </header>
        
        <div class="grid">
            <!-- Deployment Statistics -->
            <div class="card">
                <h2>Deployment Statistics</h2>
                <div class="metric">
                    <span class="metric-label">Total Proposals</span>
                    <span class="metric-value">{deployment_stats.get('total_proposals', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Deployed</span>
                    <span class="metric-value" style="color: #4caf50;">{deployment_stats.get('deployed', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed</span>
                    <span class="metric-value" style="color: #f44336;">{deployment_stats.get('failed', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Rolled Back</span>
                    <span class="metric-value" style="color: #ff9800;">{deployment_stats.get('rolled_back', 0)}</span>
                </div>
                <div class="chart-container">
                    <canvas id="deploymentChart"></canvas>
                </div>
            </div>
            
            <!-- Staging Status -->
            <div class="card">
                <h2>Staging Status</h2>
                <div class="metric">
                    <span class="metric-label">Staged</span>
                    <span class="metric-value">{staging_stats['staged_count']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Testing</span>
                    <span class="metric-value">{staging_stats['testing_count']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Deployed</span>
                    <span class="metric-value">{staging_stats['deployed_count']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Rejected</span>
                    <span class="metric-value">{staging_stats['rejected_count']}</span>
                </div>
                <div class="chart-container">
                    <canvas id="stagingChart"></canvas>
                </div>
            </div>
            
            <!-- Activity by Type -->
            <div class="card">
                <h2>Activity by Type</h2>
"""
        
        # Add action type metrics
        total_actions = sum(actions_by_type.values())
        for action, count in sorted(actions_by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_actions * 100) if total_actions > 0 else 0
            html += f"""
                <div class="metric">
                    <span class="metric-label">{action.replace('_', ' ').title()}</span>
                    <span class="metric-value">{count} ({percentage:.0f}%)</span>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <!-- Timeline -->
        <div class="card">
            <h2>Recent Activity Timeline</h2>
            <div class="timeline">
"""
        
        # Add timeline entries
        for entry in history:
            timestamp = entry.get('timestamp', 'Unknown')
            action = entry.get('action', 'unknown').replace('_', ' ').title()
            html += f"""
                <div class="timeline-item">
                    <div class="action-type">{action}</div>
                    <div class="timestamp">{timestamp}</div>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <!-- Controls -->
        <div class="card">
            <h2>Controls</h2>
            <div class="actions">
                <button class="btn-primary" onclick="runImmediateCheck()">
                    Run Improvement Check Now
                </button>
                <button class="btn-secondary" onclick="refreshDashboard()">
                    Refresh Dashboard
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // Deployment Chart
        const deploymentCtx = document.getElementById('deploymentChart').getContext('2d');
        new Chart(deploymentCtx, {
            type: 'doughnut',
            data: {
                labels: ['Deployed', 'Failed', 'Rolled Back'],
                datasets: [{
                    data: [
                        {deployment_stats.get('deployed', 0)},
                        {deployment_stats.get('failed', 0)},
                        {deployment_stats.get('rolled_back', 0)}
                    ],
                    backgroundColor: ['#4caf50', '#f44336', '#ff9800']
                }]
            },
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Staging Chart
        const stagingCtx = document.getElementById('stagingChart').getContext('2d');
        new Chart(stagingCtx, {
            type: 'bar',
            data: {
                labels: ['Staged', 'Testing', 'Deployed', 'Rejected'],
                datasets: [{
                    label: 'Count',
                    data: [
                        {staging_stats['staged_count']},
                        {staging_stats['testing_count']},
                        {staging_stats['deployed_count']},
                        {staging_stats['rejected_count']}
                    ],
                    backgroundColor: '#667eea'
                }]
            },
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        function runImmediateCheck() {{
            alert('Running improvement check...');
            // Would call API endpoint to trigger check
        }}
        
        function refreshDashboard() {{
            location.reload();
        }}
    </script>
</body>
</html>
"""
        
        return html

    def save_dashboard(self):
        """Save dashboard HTML to file."""
        try:
            self.dashboard_path.parent.mkdir(parents=True, exist_ok=True)
            html = self.generate_dashboard_html()
            with open(self.dashboard_path, 'w') as f:
                f.write(html)
            logger.info(f"Dashboard saved to {self.dashboard_path}")
            return self.dashboard_path
        except Exception as e:
            logger.error(f"Failed to save dashboard: {e}")
            return None

    def get_json_status(self) -> Dict[str, Any]:
        """
        Get current status as JSON (useful for API endpoints).
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.manager.get_improvement_statistics(),
            'recent_history': self.manager.get_improvement_history(10),
            'scheduler_status': self.scheduler.get_scheduler_status() if self.scheduler else None,
        }
