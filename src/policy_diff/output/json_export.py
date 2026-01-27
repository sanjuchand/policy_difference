"""JSON export for diff results."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from policy_diff.models.diff_result import DiffReport, Significance


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JSONExporter:
    """Exports diff results to JSON format."""

    def __init__(
        self,
        pretty_print: bool = True,
        include_metadata: bool = True,
        filter_significance: Optional[Significance] = None,
    ):
        """Initialize JSON exporter.

        Args:
            pretty_print: Whether to format JSON with indentation
            include_metadata: Whether to include processing metadata
            filter_significance: Only include changes at or above this level
        """
        self.pretty_print = pretty_print
        self.include_metadata = include_metadata
        self.filter_significance = filter_significance

    def export(self, report: DiffReport) -> str:
        """Export diff report to JSON string.

        Args:
            report: DiffReport to export

        Returns:
            JSON string
        """
        data = self._prepare_data(report)

        kwargs = {"cls": DateTimeEncoder}
        if self.pretty_print:
            kwargs["indent"] = 2

        return json.dumps(data, **kwargs)

    def export_to_file(self, report: DiffReport, output_path: Path | str) -> Path:
        """Export diff report to JSON file.

        Args:
            report: DiffReport to export
            output_path: Path to save JSON file

        Returns:
            Path to generated file
        """
        output_path = Path(output_path)
        json_content = self.export(report)

        output_path.write_text(json_content, encoding="utf-8")
        return output_path

    def _prepare_data(self, report: DiffReport) -> dict:
        """Prepare report data for JSON export.

        Args:
            report: DiffReport to process

        Returns:
            Dictionary ready for JSON serialization
        """
        # Filter changes if needed
        changes = report.changes
        if self.filter_significance:
            significance_order = {
                Significance.CRITICAL: 4,
                Significance.HIGH: 3,
                Significance.MEDIUM: 2,
                Significance.LOW: 1,
                Significance.NONE: 0,
            }
            min_level = significance_order[self.filter_significance]
            changes = [
                c
                for c in changes
                if significance_order.get(c.significance, 0) >= min_level
            ]

        data = {
            "report_id": report.report_id,
            "document_a": report.document_a_name,
            "document_b": report.document_b_name,
            "created_at": report.created_at,
            "summary": report.summary.to_dict(),
            "changes": [c.to_dict() for c in changes],
        }

        if self.include_metadata:
            data["metadata"] = {
                "processing_time_seconds": report.processing_time_seconds,
                "llm_calls_made": report.llm_calls_made,
                "embeddings_computed": report.embeddings_computed,
                "total_changes_before_filter": len(report.changes),
                "changes_after_filter": len(changes),
            }

        return data

    def export_changes_only(self, report: DiffReport) -> str:
        """Export only the changes array.

        Args:
            report: DiffReport to export

        Returns:
            JSON string of changes array
        """
        changes = report.changes
        if self.filter_significance:
            significance_order = {
                Significance.CRITICAL: 4,
                Significance.HIGH: 3,
                Significance.MEDIUM: 2,
                Significance.LOW: 1,
                Significance.NONE: 0,
            }
            min_level = significance_order[self.filter_significance]
            changes = [
                c
                for c in changes
                if significance_order.get(c.significance, 0) >= min_level
            ]

        kwargs = {"cls": DateTimeEncoder}
        if self.pretty_print:
            kwargs["indent"] = 2

        return json.dumps([c.to_dict() for c in changes], **kwargs)

    def export_summary_only(self, report: DiffReport) -> str:
        """Export only the summary.

        Args:
            report: DiffReport to export

        Returns:
            JSON string of summary
        """
        data = {
            "report_id": report.report_id,
            "document_a": report.document_a_name,
            "document_b": report.document_b_name,
            "created_at": report.created_at,
            "summary": report.summary.to_dict(),
        }

        kwargs = {"cls": DateTimeEncoder}
        if self.pretty_print:
            kwargs["indent"] = 2

        return json.dumps(data, **kwargs)


class JSONLExporter:
    """Exports diff results to JSON Lines format (one JSON object per line)."""

    def export(self, report: DiffReport) -> str:
        """Export diff report to JSONL string.

        Args:
            report: DiffReport to export

        Returns:
            JSONL string (one line per change)
        """
        lines = []

        # Add header line with report metadata
        header = {
            "type": "header",
            "report_id": report.report_id,
            "document_a": report.document_a_name,
            "document_b": report.document_b_name,
            "created_at": report.created_at.isoformat(),
            "total_changes": report.summary.total_changes,
        }
        lines.append(json.dumps(header))

        # Add one line per change
        for change in report.changes:
            change_data = {"type": "change", **change.to_dict()}
            lines.append(json.dumps(change_data))

        # Add footer line with summary
        footer = {"type": "footer", "summary": report.summary.to_dict()}
        lines.append(json.dumps(footer))

        return "\n".join(lines)

    def export_to_file(self, report: DiffReport, output_path: Path | str) -> Path:
        """Export diff report to JSONL file.

        Args:
            report: DiffReport to export
            output_path: Path to save JSONL file

        Returns:
            Path to generated file
        """
        output_path = Path(output_path)
        jsonl_content = self.export(report)

        output_path.write_text(jsonl_content, encoding="utf-8")
        return output_path


def export_to_json(
    report: DiffReport,
    output_path: Optional[Path | str] = None,
    **kwargs,
) -> str:
    """Convenience function to export report to JSON.

    Args:
        report: DiffReport to export
        output_path: Optional path to save file
        **kwargs: Arguments passed to JSONExporter

    Returns:
        JSON string
    """
    exporter = JSONExporter(**kwargs)

    if output_path:
        exporter.export_to_file(report, output_path)

    return exporter.export(report)
