"""HTML report generator for diff results."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, BaseLoader

from policy_diff.models.diff_result import (
    DiffReport,
    ChangeItem,
    Significance,
    ChangeType,
)


# HTML template for the diff report
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Policy Diff Report - {{ report.document_a_name }} vs {{ report.document_b_name }}</title>
    <style>
        :root {
            --critical-color: #dc3545;
            --high-color: #fd7e14;
            --medium-color: #ffc107;
            --low-color: #17a2b8;
            --none-color: #6c757d;
            --added-bg: #d4edda;
            --removed-bg: #f8d7da;
            --modified-bg: #fff3cd;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }

        header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .meta-info {
            display: flex;
            gap: 20px;
            font-size: 14px;
            opacity: 0.9;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }

        .summary-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .summary-card .number {
            font-size: 28px;
            font-weight: bold;
        }

        .summary-card .label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }

        .summary-card.critical .number { color: var(--critical-color); }
        .summary-card.high .number { color: var(--high-color); }
        .summary-card.medium .number { color: var(--medium-color); }
        .summary-card.low .number { color: var(--low-color); }

        .filters {
            padding: 15px 20px;
            background: #fff;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 8px 16px;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .filter-btn:hover, .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        .changes-list {
            padding: 20px;
        }

        .change-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }

        .change-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }

        .change-badges {
            display: flex;
            gap: 8px;
        }

        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-critical { background: var(--critical-color); color: white; }
        .badge-high { background: var(--high-color); color: white; }
        .badge-medium { background: var(--medium-color); color: #333; }
        .badge-low { background: var(--low-color); color: white; }
        .badge-none { background: var(--none-color); color: white; }

        .badge-added { background: #28a745; color: white; }
        .badge-removed { background: #dc3545; color: white; }
        .badge-modified { background: #fd7e14; color: white; }

        .change-location {
            font-size: 12px;
            color: #666;
        }

        .change-content {
            padding: 15px;
        }

        .text-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .text-box {
            padding: 12px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .text-box.before {
            background: var(--removed-bg);
            border-left: 4px solid var(--critical-color);
        }

        .text-box.after {
            background: var(--added-bg);
            border-left: 4px solid #28a745;
        }

        .text-label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
            color: #666;
        }

        .analysis {
            margin-top: 15px;
            padding: 12px;
            background: #e7f1ff;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }

        .analysis h4 {
            font-size: 13px;
            margin-bottom: 8px;
            color: #667eea;
        }

        .analysis p {
            font-size: 13px;
            margin-bottom: 5px;
        }

        .categories {
            display: flex;
            gap: 5px;
            margin-top: 10px;
        }

        .category-tag {
            padding: 3px 8px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            font-size: 11px;
        }

        .review-flag {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 10px;
            background: #fff3cd;
            border-radius: 4px;
            font-size: 12px;
            margin-top: 10px;
        }

        footer {
            padding: 20px;
            text-align: center;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #666;
        }

        @media (max-width: 768px) {
            .text-comparison {
                grid-template-columns: 1fr;
            }

            .meta-info {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 Policy Diff Report</h1>
            <div class="meta-info">
                <span>📄 {{ report.document_a_name }} → {{ report.document_b_name }}</span>
                <span>📅 Generated: {{ report.created_at.strftime('%Y-%m-%d %H:%M') }}</span>
                <span>⏱️ Processing: {{ "%.2f"|format(report.processing_time_seconds) }}s</span>
            </div>
        </header>

        <div class="summary">
            <div class="summary-card">
                <div class="number">{{ report.summary.total_changes }}</div>
                <div class="label">Total Changes</div>
            </div>
            <div class="summary-card critical">
                <div class="number">{{ report.summary.critical_changes }}</div>
                <div class="label">Critical</div>
            </div>
            <div class="summary-card high">
                <div class="number">{{ report.summary.high_changes }}</div>
                <div class="label">High</div>
            </div>
            <div class="summary-card medium">
                <div class="number">{{ report.summary.medium_changes }}</div>
                <div class="label">Medium</div>
            </div>
            <div class="summary-card low">
                <div class="number">{{ report.summary.low_changes }}</div>
                <div class="label">Low</div>
            </div>
        </div>

        <div class="filters">
            <button class="filter-btn active" data-filter="all">All</button>
            <button class="filter-btn" data-filter="critical">Critical</button>
            <button class="filter-btn" data-filter="high">High</button>
            <button class="filter-btn" data-filter="medium">Medium</button>
            <button class="filter-btn" data-filter="added">Added</button>
            <button class="filter-btn" data-filter="removed">Removed</button>
            <button class="filter-btn" data-filter="modified">Modified</button>
        </div>

        <div class="changes-list">
            {% for change in report.changes %}
            <div class="change-item" data-significance="{{ change.significance.value }}" data-type="{{ change.change_type.value }}">
                <div class="change-header">
                    <div class="change-badges">
                        <span class="badge badge-{{ change.significance.value }}">{{ change.significance.value }}</span>
                        <span class="badge badge-{{ change.change_type.value }}">{{ change.change_type.value }}</span>
                        {% if change.is_pii_affected %}
                        <span class="badge" style="background: #6f42c1; color: white;">PII</span>
                        {% endif %}
                    </div>
                    <div class="change-location">
                        {% if change.location_before and change.location_before.page_number %}
                        Page {{ change.location_before.page_number }}
                        {% endif %}
                        {% if change.location_before and change.location_before.section_path %}
                        | {{ change.location_before.section_path }}
                        {% endif %}
                    </div>
                </div>
                <div class="change-content">
                    <div class="text-comparison">
                        <div>
                            <div class="text-label">Before</div>
                            <div class="text-box before">{{ change.text_before or "(Empty)" }}</div>
                        </div>
                        <div>
                            <div class="text-label">After</div>
                            <div class="text-box after">{{ change.text_after or "(Empty)" }}</div>
                        </div>
                    </div>

                    {% if change.semantic_analysis %}
                    <div class="analysis">
                        <h4>🤖 AI Analysis</h4>
                        <p><strong>Explanation:</strong> {{ change.semantic_analysis.explanation }}</p>
                        <p><strong>Business Impact:</strong> {{ change.semantic_analysis.business_impact }}</p>
                        {% if change.semantic_analysis.regulatory_impact %}
                        <p><strong>Regulatory Impact:</strong> {{ change.semantic_analysis.regulatory_impact }}</p>
                        {% endif %}
                        <div class="categories">
                            {% for cat in change.semantic_analysis.categories %}
                            <span class="category-tag">{{ cat.value }}</span>
                            {% endfor %}
                        </div>
                        {% if change.semantic_analysis.requires_review %}
                        <div class="review-flag">⚠️ Requires Human Review</div>
                        {% endif %}
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>

        <footer>
            Generated by Policy Diff Engine | {{ report.llm_calls_made }} LLM calls | {{ report.embeddings_computed }} embeddings computed
        </footer>
    </div>

    <script>
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const filter = this.dataset.filter;
                document.querySelectorAll('.change-item').forEach(item => {
                    if (filter === 'all') {
                        item.style.display = 'block';
                    } else if (['critical', 'high', 'medium', 'low', 'none'].includes(filter)) {
                        item.style.display = item.dataset.significance === filter ? 'block' : 'none';
                    } else {
                        item.style.display = item.dataset.type === filter ? 'block' : 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>
"""


class HTMLReportGenerator:
    """Generates HTML reports from diff results."""

    def __init__(self, template: Optional[str] = None):
        """Initialize report generator.

        Args:
            template: Custom HTML template (uses default if None)
        """
        self.template = template or HTML_TEMPLATE
        self._env = Environment(loader=BaseLoader())

    def generate(self, report: DiffReport) -> str:
        """Generate HTML report from diff results.

        Args:
            report: DiffReport to render

        Returns:
            HTML string
        """
        template = self._env.from_string(self.template)
        return template.render(report=report)

    def generate_to_file(self, report: DiffReport, output_path: Path | str) -> Path:
        """Generate HTML report and save to file.

        Args:
            report: DiffReport to render
            output_path: Path to save HTML file

        Returns:
            Path to generated file
        """
        output_path = Path(output_path)
        html_content = self.generate(report)

        output_path.write_text(html_content, encoding="utf-8")
        return output_path

    def generate_summary_only(self, report: DiffReport) -> str:
        """Generate a summary-only HTML snippet.

        Args:
            report: DiffReport to summarize

        Returns:
            HTML snippet
        """
        return f"""
        <div class="summary">
            <h2>Policy Diff Summary</h2>
            <p><strong>Documents:</strong> {report.document_a_name} → {report.document_b_name}</p>
            <p><strong>Total Changes:</strong> {report.summary.total_changes}</p>
            <ul>
                <li>Critical: {report.summary.critical_changes}</li>
                <li>High: {report.summary.high_changes}</li>
                <li>Medium: {report.summary.medium_changes}</li>
                <li>Low: {report.summary.low_changes}</li>
            </ul>
            <p><strong>Generated:</strong> {report.created_at.strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """


def generate_html_report(report: DiffReport, output_path: Optional[Path | str] = None) -> str:
    """Convenience function to generate HTML report.

    Args:
        report: DiffReport to render
        output_path: Optional path to save file

    Returns:
        HTML string
    """
    generator = HTMLReportGenerator()

    if output_path:
        generator.generate_to_file(report, output_path)

    return generator.generate(report)
