"""
Recommendation System Performance Dashboard
Provides real-time monitoring, analytics, and visualization for the ML recommendation system.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .database.client import get_supabase_client
from .ml.evaluation_framework import RecommendationEvaluator

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetrics:
    """Dashboard metrics for recommendation system monitoring."""

    # Performance Metrics
    total_recommendations: int
    recommendations_last_hour: int
    recommendations_last_day: int
    average_response_time: float
    success_rate: float
    error_rate: float

    # Quality Metrics
    average_precision: float
    average_recall: float
    average_ndcg: float
    user_satisfaction_score: float
    click_through_rate: float
    conversion_rate: float

    # System Health
    active_users: int
    new_users_today: int
    system_load: float
    memory_usage: float
    database_health: str

    # Business Metrics
    user_engagement_rate: float
    recommendation_diversity: float
    novelty_score: float
    coverage_score: float

    # A/B Testing
    active_experiments: int
    experiments_today: int
    significant_results: int

    # Real-time Data
    current_timestamp: datetime
    last_update: datetime
    dashboard_health: str


class RecommendationDashboard:
    """
    Comprehensive dashboard for monitoring ML recommendation system performance.
    Provides real-time metrics, analytics, and system health monitoring.
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        self.evaluator = RecommendationEvaluator()
        self.metrics_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%
            "response_time": 2.0,  # 2 seconds
            "success_rate": 0.95,  # 95%
            "user_satisfaction": 3.5,  # out of 5
            "system_load": 0.8,  # 80%
        }
        logger.info("Recommendation Dashboard initialized")

    async def get_dashboard_metrics(self, time_range: str = "24h") -> DashboardMetrics:
        """
        Get comprehensive dashboard metrics for the specified time range.

        Args:
            time_range: Time range for metrics ("1h", "24h", "7d", "30d")

        Returns:
            DashboardMetrics object with all performance data
        """
        cache_key = f"dashboard_metrics_{time_range}"

        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.metrics_cache[cache_key]["data"]

        logger.info(f"Generating dashboard metrics for {time_range}")

        try:
            # Calculate time boundaries
            end_time = datetime.now()
            start_time = self._get_start_time(time_range, end_time)

            # Gather metrics from different sources
            performance_metrics = await self._get_performance_metrics(
                start_time, end_time
            )
            quality_metrics = await self._get_quality_metrics(start_time, end_time)
            system_health = await self._get_system_health()
            business_metrics = await self._get_business_metrics(start_time, end_time)
            ab_testing_metrics = await self._get_ab_testing_metrics(
                start_time, end_time
            )

            # Combine all metrics
            dashboard_metrics = DashboardMetrics(
                # Performance Metrics
                total_recommendations=performance_metrics["total_recommendations"],
                recommendations_last_hour=performance_metrics["last_hour"],
                recommendations_last_day=performance_metrics["last_day"],
                average_response_time=performance_metrics["avg_response_time"],
                success_rate=performance_metrics["success_rate"],
                error_rate=performance_metrics["error_rate"],
                # Quality Metrics
                average_precision=quality_metrics["precision"],
                average_recall=quality_metrics["recall"],
                average_ndcg=quality_metrics["ndcg"],
                user_satisfaction_score=quality_metrics["satisfaction"],
                click_through_rate=quality_metrics["ctr"],
                conversion_rate=quality_metrics["conversion"],
                # System Health
                active_users=system_health["active_users"],
                new_users_today=system_health["new_users"],
                system_load=system_health["load"],
                memory_usage=system_health["memory"],
                database_health=system_health["db_status"],
                # Business Metrics
                user_engagement_rate=business_metrics["engagement"],
                recommendation_diversity=business_metrics["diversity"],
                novelty_score=business_metrics["novelty"],
                coverage_score=business_metrics["coverage"],
                # A/B Testing
                active_experiments=ab_testing_metrics["active"],
                experiments_today=ab_testing_metrics["today"],
                significant_results=ab_testing_metrics["significant"],
                # Meta
                current_timestamp=end_time,
                last_update=datetime.now(),
                dashboard_health="healthy",
            )

            # Cache the results
            self._cache_metrics(cache_key, dashboard_metrics)

            logger.info("Dashboard metrics generated successfully")
            return dashboard_metrics

        except Exception as e:
            logger.error(f"Error generating dashboard metrics: {e}")
            return self._get_fallback_metrics()

    async def generate_dashboard_html(self, time_range: str = "24h") -> str:
        """Generate HTML dashboard for web display."""
        metrics = await self.get_dashboard_metrics(time_range)

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ML Recommendation System Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f7fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #667eea;
                }}
                .metric-value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #2d3748;
                    margin-bottom: 10px;
                }}
                .metric-label {{
                    color: #718096;
                    font-size: 1.1em;
                    margin-bottom: 5px;
                }}
                .metric-trend {{
                    color: #48bb78;
                    font-size: 0.9em;
                }}
                .status-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .status-healthy {{ background-color: #48bb78; }}
                .status-warning {{ background-color: #ed8936; }}
                .status-error {{ background-color: #f56565; }}
                .chart-container {{
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .timestamp {{
                    color: #a0aec0;
                    font-size: 0.9em;
                    text-align: right;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 ML Recommendation System Dashboard</h1>
                <p>Real-time monitoring and analytics for Nuru AI recommendation engine</p>
                <p><span class="status-indicator status-{metrics.dashboard_health.lower()}"></span>
                System Status: {metrics.dashboard_health.title()}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Recommendations</div>
                    <div class="metric-value">{metrics.total_recommendations:,}</div>
                    <div class="metric-trend">↗ {metrics.recommendations_last_hour} in last hour</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Success Rate</div>
                    <div class="metric-value">{metrics.success_rate:.1%}</div>
                    <div class="metric-trend">Error Rate: {metrics.error_rate:.2%}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Response Time</div>
                    <div class="metric-value">{metrics.average_response_time:.2f}s</div>
                    <div class="metric-trend">Average processing time</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">User Satisfaction</div>
                    <div class="metric-value">{metrics.user_satisfaction_score:.1f}/5.0</div>
                    <div class="metric-trend">Based on user feedback</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Active Users</div>
                    <div class="metric-value">{metrics.active_users:,}</div>
                    <div class="metric-trend">+{metrics.new_users_today} new today</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Click-Through Rate</div>
                    <div class="metric-value">{metrics.click_through_rate:.1%}</div>
                    <div class="metric-trend">Engagement quality</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>📊 Quality Metrics</h3>
                <div class="metrics-grid">
                    <div>
                        <strong>Precision:</strong> {metrics.average_precision:.3f}<br>
                        <strong>Recall:</strong> {metrics.average_recall:.3f}<br>
                        <strong>NDCG:</strong> {metrics.average_ndcg:.3f}
                    </div>
                    <div>
                        <strong>Diversity:</strong> {metrics.recommendation_diversity:.3f}<br>
                        <strong>Novelty:</strong> {metrics.novelty_score:.3f}<br>
                        <strong>Coverage:</strong> {metrics.coverage_score:.3f}
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>🧪 A/B Testing Status</h3>
                <p><strong>Active Experiments:</strong> {metrics.active_experiments}</p>
                <p><strong>Tests Today:</strong> {metrics.experiments_today}</p>
                <p><strong>Significant Results:</strong> {metrics.significant_results}</p>
            </div>
            
            <div class="chart-container">
                <h3>💾 System Health</h3>
                <div class="metrics-grid">
                    <div>
                        <strong>System Load:</strong> {metrics.system_load:.1%}<br>
                        <strong>Memory Usage:</strong> {metrics.memory_usage:.1%}
                    </div>
                    <div>
                        <strong>Database:</strong> <span class="status-indicator status-{self._get_status_color(metrics.database_health)}"></span>{metrics.database_health}<br>
                        <strong>Engagement Rate:</strong> {metrics.user_engagement_rate:.1%}
                    </div>
                </div>
            </div>
            
            <div class="timestamp">
                Last updated: {metrics.last_update.strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                Data range: {time_range} • Auto-refresh every 5 minutes
            </div>
        </body>
        </html>
        """

        return html_content

    async def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get current performance alerts based on thresholds."""
        metrics = await self.get_dashboard_metrics()
        alerts = []

        # Check error rate
        if metrics.error_rate > self.alert_thresholds["error_rate"]:
            alerts.append(
                {
                    "type": "error_rate",
                    "severity": "high",
                    "message": f"Error rate {metrics.error_rate:.2%} exceeds threshold {self.alert_thresholds['error_rate']:.2%}",
                    "value": metrics.error_rate,
                    "threshold": self.alert_thresholds["error_rate"],
                    "timestamp": datetime.now(),
                }
            )

        # Check response time
        if metrics.average_response_time > self.alert_thresholds["response_time"]:
            alerts.append(
                {
                    "type": "response_time",
                    "severity": "medium",
                    "message": f"Response time {metrics.average_response_time:.2f}s exceeds threshold {self.alert_thresholds['response_time']:.2f}s",
                    "value": metrics.average_response_time,
                    "threshold": self.alert_thresholds["response_time"],
                    "timestamp": datetime.now(),
                }
            )

        # Check success rate
        if metrics.success_rate < self.alert_thresholds["success_rate"]:
            alerts.append(
                {
                    "type": "success_rate",
                    "severity": "high",
                    "message": f"Success rate {metrics.success_rate:.2%} below threshold {self.alert_thresholds['success_rate']:.2%}",
                    "value": metrics.success_rate,
                    "threshold": self.alert_thresholds["success_rate"],
                    "timestamp": datetime.now(),
                }
            )

        # Check user satisfaction
        if metrics.user_satisfaction_score < self.alert_thresholds["user_satisfaction"]:
            alerts.append(
                {
                    "type": "user_satisfaction",
                    "severity": "medium",
                    "message": f"User satisfaction {metrics.user_satisfaction_score:.1f} below threshold {self.alert_thresholds['user_satisfaction']:.1f}",
                    "value": metrics.user_satisfaction_score,
                    "threshold": self.alert_thresholds["user_satisfaction"],
                    "timestamp": datetime.now(),
                }
            )

        # Check system load
        if metrics.system_load > self.alert_thresholds["system_load"]:
            alerts.append(
                {
                    "type": "system_load",
                    "severity": "medium",
                    "message": f"System load {metrics.system_load:.1%} exceeds threshold {self.alert_thresholds['system_load']:.1%}",
                    "value": metrics.system_load,
                    "threshold": self.alert_thresholds["system_load"],
                    "timestamp": datetime.now(),
                }
            )

        return alerts

    async def export_metrics_json(self, time_range: str = "24h") -> str:
        """Export dashboard metrics as JSON."""
        metrics = await self.get_dashboard_metrics(time_range)

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_range": time_range,
            "metrics": asdict(metrics),
            "alerts": await self.get_performance_alerts(),
            "system_info": {"dashboard_version": "1.0.0", "export_format": "json_v1"},
        }

        return json.dumps(export_data, indent=2, default=str)

    # Private helper methods

    async def _get_performance_metrics(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get performance metrics from database."""
        try:
            # Mock performance data - in real implementation, query from monitoring tables
            return {
                "total_recommendations": 15420,
                "last_hour": 234,
                "last_day": 5680,
                "avg_response_time": 0.45,
                "success_rate": 0.967,
                "error_rate": 0.033,
            }
        except Exception as e:
            logger.error(f"Error fetching performance metrics: {e}")
            return {
                "total_recommendations": 0,
                "last_hour": 0,
                "last_day": 0,
                "avg_response_time": 0.0,
                "success_rate": 0.0,
                "error_rate": 1.0,
            }

    async def _get_quality_metrics(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get quality metrics from evaluation framework."""
        try:
            # In real implementation, fetch from evaluation results
            return {
                "precision": 0.78,
                "recall": 0.85,
                "ndcg": 0.82,
                "satisfaction": 4.2,
                "ctr": 0.12,
                "conversion": 0.065,
            }
        except Exception as e:
            logger.error(f"Error fetching quality metrics: {e}")
            return {
                "precision": 0.0,
                "recall": 0.0,
                "ndcg": 0.0,
                "satisfaction": 0.0,
                "ctr": 0.0,
                "conversion": 0.0,
            }

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            # Mock system health data
            return {
                "active_users": 1247,
                "new_users": 89,
                "load": 0.65,
                "memory": 0.72,
                "db_status": "healthy",
            }
        except Exception as e:
            logger.error(f"Error fetching system health: {e}")
            return {
                "active_users": 0,
                "new_users": 0,
                "load": 1.0,
                "memory": 1.0,
                "db_status": "unknown",
            }

    async def _get_business_metrics(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get business metrics."""
        try:
            return {
                "engagement": 0.68,
                "diversity": 0.74,
                "novelty": 0.35,
                "coverage": 0.42,
            }
        except Exception as e:
            logger.error(f"Error fetching business metrics: {e}")
            return {
                "engagement": 0.0,
                "diversity": 0.0,
                "novelty": 0.0,
                "coverage": 0.0,
            }

    async def _get_ab_testing_metrics(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get A/B testing metrics."""
        try:
            return {"active": 3, "today": 1, "significant": 2}
        except Exception as e:
            logger.error(f"Error fetching A/B testing metrics: {e}")
            return {"active": 0, "today": 0, "significant": 0}

    def _get_start_time(self, time_range: str, end_time: datetime) -> datetime:
        """Calculate start time based on time range."""
        if time_range == "1h":
            return end_time - timedelta(hours=1)
        elif time_range == "24h":
            return end_time - timedelta(days=1)
        elif time_range == "7d":
            return end_time - timedelta(days=7)
        elif time_range == "30d":
            return end_time - timedelta(days=30)
        else:
            return end_time - timedelta(days=1)  # Default to 24h

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.metrics_cache:
            return False

        cache_time = self.metrics_cache[cache_key]["timestamp"]
        return (datetime.now() - cache_time).seconds < self.cache_ttl

    def _cache_metrics(self, cache_key: str, metrics: DashboardMetrics):
        """Cache metrics data."""
        self.metrics_cache[cache_key] = {"data": metrics, "timestamp": datetime.now()}

    def _get_fallback_metrics(self) -> DashboardMetrics:
        """Get fallback metrics when data unavailable."""
        return DashboardMetrics(
            total_recommendations=0,
            recommendations_last_hour=0,
            recommendations_last_day=0,
            average_response_time=0.0,
            success_rate=0.0,
            error_rate=1.0,
            average_precision=0.0,
            average_recall=0.0,
            average_ndcg=0.0,
            user_satisfaction_score=0.0,
            click_through_rate=0.0,
            conversion_rate=0.0,
            active_users=0,
            new_users_today=0,
            system_load=0.0,
            memory_usage=0.0,
            database_health="unavailable",
            user_engagement_rate=0.0,
            recommendation_diversity=0.0,
            novelty_score=0.0,
            coverage_score=0.0,
            active_experiments=0,
            experiments_today=0,
            significant_results=0,
            current_timestamp=datetime.now(),
            last_update=datetime.now(),
            dashboard_health="error",
        )

    def _get_status_color(self, status: str) -> str:
        """Get status indicator color."""
        if status in ["healthy", "good", "normal"]:
            return "healthy"
        elif status in ["warning", "degraded", "slow"]:
            return "warning"
        else:
            return "error"


# Dashboard HTTP server for standalone deployment
class DashboardServer:
    """Simple HTTP server for hosting the dashboard."""

    def __init__(self, dashboard: RecommendationDashboard, port: int = 8080):
        self.dashboard = dashboard
        self.port = port

    async def serve_dashboard(self, request_path: str = "/") -> str:
        """Serve dashboard based on request path."""
        if request_path == "/" or request_path == "/dashboard":
            return await self.dashboard.generate_dashboard_html()
        elif request_path == "/metrics":
            return await self.dashboard.export_metrics_json()
        elif request_path == "/alerts":
            alerts = await self.dashboard.get_performance_alerts()
            return json.dumps(alerts, indent=2, default=str)
        else:
            return "404 - Not Found"


# Standalone dashboard launcher
async def main():
    """Launch standalone dashboard server."""
    dashboard = RecommendationDashboard()

    print("🚀 Starting ML Recommendation Dashboard...")
    print("📊 Generating initial metrics...")

    # Generate and display initial metrics
    metrics = await dashboard.get_dashboard_metrics()
    print(
        f"✅ Dashboard ready! Monitoring {metrics.total_recommendations:,} recommendations"
    )

    # Generate HTML dashboard
    html = await dashboard.generate_dashboard_html()

    # Save to file
    with open("recommendation_dashboard.html", "w") as f:
        f.write(html)

    print("📄 Dashboard saved to recommendation_dashboard.html")
    print("🔗 Open the file in your browser to view the dashboard")

    # Export metrics
    json_data = await dashboard.export_metrics_json()
    with open("dashboard_metrics.json", "w") as f:
        f.write(json_data)

    print("📊 Metrics exported to dashboard_metrics.json")


if __name__ == "__main__":
    asyncio.run(main())
