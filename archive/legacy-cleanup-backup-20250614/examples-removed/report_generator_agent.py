import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# from swarms import Agent  # REMOVED - Framework migration complete
from extraction.agents.models import (
    RefinedEventData,
)  # Added

# Remove global logger instance
# # Configure logger if needed
# if not logger.hasHandlers():
#     logger.addHandler(logging.StreamHandler())
#     logger.setLevel(logging.INFO)

# Define the output directory (relative to project root)
OUTPUT_DIR = "results"


class ReportGeneratorAgent:
    """Framework-free agent that generates JSON and TXT report files from
    extracted and compiled event data."""

    def __init__(
        self,
        name: str = "ReportGeneratorAgent",
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the ReportGeneratorAgent.

        Args:
            name: Name of the agent.
            logger: Optional logger instance. If None, a default logger is created.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.logger.info("[%s] initialized framework-free agent", self.name)

        # Ensure output directory exists
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            self.logger.info(
                "[%s] Ensured output directory exists: %s", self.name, OUTPUT_DIR
            )
        except OSError as e:
            self.logger.error(
                "[%s] Failed to create output directory %s: %s",
                self.name,
                OUTPUT_DIR,
                e,
            )
            raise RuntimeError(
                f"Agent {self.name} cannot proceed without output directory."
            ) from e

    def _save_json_results(self, data: Any, filename: str) -> str:
        """Saves data to a JSON file inside the agent's output directory."""
        save_path = os.path.join(OUTPUT_DIR, filename)
        self.logger.info(f"[{self.name}] Attempting to save JSON data to {save_path}")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.logger.info(f"[{self.name}] Results successfully saved to {save_path}")
            return f"Success: Saved to {save_path}"
        except (IOError, TypeError) as e:
            self.logger.error(
                f"[{self.name}] Error saving JSON results to {save_path}: {e}"
            )
            return f"Error: Could not save to {save_path} - {e}"

    def _create_readable_report_content(
        self,
        all_data: List[RefinedEventData],
        compiled_data: Dict[
            str, List[Any]
        ],  # compiled_data: output from DataCompilerAgent
    ) -> str:
        report_lines = []
        successful_count = 0
        failed_count = 0
        # manual_fallback_count = 0 # This status might change with the refiner

        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

        for event_data in all_data:
            if not isinstance(event_data, RefinedEventData):
                self.logger.warning(
                    f"[{self.name}] Skipping invalid data entry: type {type(event_data)}, expected RefinedEventData."
                )
                report_lines.append(
                    "============================================================"
                )
                report_lines.append(f"SKIPPED INVALID ENTRY: Type {type(event_data)}")
                report_lines.append(
                    "============================================================\n"
                )
                failed_count += 1
                continue

            # Use extractor_status from RefinedEventData
            status = event_data.extractor_status or "Status Unknown"
            if "Success" in status and "Failed" not in status:  # Basic check
                successful_count += 1
            elif "Failed" in status:
                failed_count += 1
            # Consider how to determine manual_fallback_count if that's still relevant

            report_lines.append(
                "============================================================"
            )
            report_lines.append(f"Event Name: {event_data.event_name}")
            report_lines.append(f"Source URL: {event_data.source_url}")
            report_lines.append(
                f"Initial Extraction Status: {status}"
            )  # Status from original extractor
            report_lines.append(
                "------------------------------------------------------------"
            )

            report_lines.append("Date & Time:")
            if event_data.start_date:
                report_lines.append(
                    f"  Start: {event_data.start_date} {event_data.start_time or ''}".strip()
                )
            if event_data.end_date:
                report_lines.append(
                    f"  End:   {event_data.end_date} {event_data.end_time or ''}".strip()
                )
            if event_data.timezone:
                report_lines.append(f"  Timezone: {event_data.timezone}")

            report_lines.append("Location:")
            if event_data.location_name:
                report_lines.append(f"  Venue: {event_data.location_name}")
            if event_data.location_address:
                report_lines.append(f"  Address: {event_data.location_address}")
            if event_data.location_city:
                report_lines.append(f"  City: {event_data.location_city}")
            if event_data.location_country:
                report_lines.append(f"  Country: {event_data.location_country}")
            if not event_data.location_name and not event_data.location_address:
                report_lines.append("  N/A")

            report_lines.append("Description:")
            if event_data.description_summary:
                report_lines.append(f"  Summary: {event_data.description_summary}")
            # Optionally include full_description if needed, or a note if it exists
            # if event_data.full_description and event_data.full_description != event_data.description_summary:
            #    report_lines.append(f"  Full: {event_data.full_description[:300]}...") # Truncate if long

            report_lines.append("Cost:")
            if event_data.cost_usd is not None:  # Check for None explicitly for float
                report_lines.append(f"  USD: ${event_data.cost_usd:.2f}")
            if event_data.cost_details:
                report_lines.append(f"  Details: {event_data.cost_details}")
            if event_data.cost_usd is None and not event_data.cost_details:
                report_lines.append("  N/A")

            if event_data.website:
                report_lines.append(f"Event Website: {event_data.website}")

            if event_data.tags:
                report_lines.append(f"Tags: {', '.join(event_data.tags)}")
            if event_data.categories:
                report_lines.append(f"Categories: {', '.join(event_data.categories)}")

            if event_data.event_social_media_links:
                report_lines.append("Event Social Media:")
                for link in event_data.event_social_media_links:
                    report_lines.append(f"  - {link}")

            report_lines.append(f"Organizers ({len(event_data.organizers)}):")
            if event_data.organizers:
                for org in event_data.organizers:
                    org_line = f"  - {org.name}"
                    if org.url:
                        org_line += f" [{org.url}]"
                    report_lines.append(org_line)
            else:
                report_lines.append("  None Identified")

            report_lines.append(
                f"Sponsors/Partners ({len(event_data.sponsors_partners)}):"
            )
            if event_data.sponsors_partners:
                for sp_org in event_data.sponsors_partners:
                    sp_line = f"  - {sp_org.name}"
                    if sp_org.url:
                        sp_line += f" [{sp_org.url}]"
                    report_lines.append(sp_line)
            else:
                report_lines.append("  None Identified")

            report_lines.append(f"Speakers ({len(event_data.speakers)}):")
            if event_data.speakers:
                for speaker in event_data.speakers:
                    speaker_line = f"  - {speaker.name}"
                    details_parts = []
                    if speaker.title:
                        details_parts.append(speaker.title)
                    if speaker.organization:
                        details_parts.append(speaker.organization)
                    if details_parts:
                        speaker_line += f" ({', '.join(details_parts)})"
                    if speaker.url:
                        speaker_line += f" [Profile: {speaker.url}]"
                    report_lines.append(speaker_line)
                    if speaker.social_links:
                        for slink in speaker.social_links:
                            report_lines.append(f"    Social: {slink}")
            else:
                report_lines.append("  None Identified")

            report_lines.append(
                "============================================================\n"
            )

        # --- Header / Overall Summary ---
        summary = [
            "==================== TOKEN 2049 SIDE EVENT REPORT (Refined) ====================",
            f"Report Generated: {generation_time}",
            "========================================================================",
            f"Total Events Processed (Refined Entries): {len(all_data)}",
            f"Successful Initial Extractions (pre-refinement): {successful_count}",
            f"Failed Initial Extractions (pre-refinement): {failed_count}",
            # Add more summary stats if needed
            "=======================================================================",
        ]

        # --- Add Overall Compiled Lists from DataCompilerAgent ---
        # This part assumes compiled_data["unique_speakers"] contains dicts
        # and compiled_data["unique_organizations"] contains strings,
        # which is what the modified DataCompilerAgent provides.
        overall_speakers_dicts = compiled_data.get("unique_speakers", [])
        overall_org_names = compiled_data.get("unique_organizations", [])

        summary.append(
            f"\n--- Overall Compiled Speakers ({len(overall_speakers_dicts)}) ---"
        )
        if overall_speakers_dicts:
            for (
                speaker_dict
            ) in overall_speakers_dicts:  # speaker_dict is already a dict
                org = speaker_dict.get("organization", "N/A")
                title = speaker_dict.get("title", "N/A")
                url = speaker_dict.get("url")
                s_line = f"  - {speaker_dict.get('name', 'N/A')}"
                details = []
                if title and title != "N/A":
                    details.append(title)
                if org and org != "N/A":
                    details.append(org)
                if details:
                    s_line += f" ({', '.join(details)})"
                if url:
                    s_line += f" [URL: {url}]"
                # Could also list social_links if desired: speaker_dict.get('social_links', [])
                summary.append(s_line)
        else:
            summary.append("  None Found")

        summary.append(
            f"\n--- Overall Compiled Organizations ({len(overall_org_names)}) ---"
        )
        if overall_org_names:
            for org_name_str in overall_org_names:  # org_name_str is already a string
                summary.append(f"  - {org_name_str}")
        else:
            summary.append("  None Found")

        summary.append(
            "========================================================================\n"
        )

        return "\n".join(summary + report_lines)

    def _save_text_report(self, report_content: str, filename: str) -> str:
        """Saves the text report content to a file."""
        save_path = os.path.join(OUTPUT_DIR, filename)
        self.logger.info(f"[{self.name}] Attempting to save text report to {save_path}")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            self.logger.info(f"[{self.name}] Successfully saved report to {save_path}")
            return f"Success: Saved to {save_path}"
        except IOError as e:
            self.logger.error(
                f"[{self.name}] Error writing report file {save_path}: {e}"
            )
            return f"Error: Could not save to {save_path} - {e}"

    # Note: File I/O is synchronous. If this agent runs in the main asyncio loop
    # and file operations are slow, consider using asyncio.to_thread for the file writes,
    # or run this agent's execution in a separate thread via the orchestrator.
    async def run_async(
        self,
        all_event_data: List[RefinedEventData],
        compiled_data: Dict[str, List[Any]],
    ) -> Dict[str, Any]:
        """
        Generates and saves the JSON and text report files.

        Args:
            all_event_data (List[Dict[str, Any]]): The list of data extracted for each event.
            compiled_data (Dict[str, Dict]): The compiled data (unique speakers/orgs).

        Returns:
            Dict[str, Any]: A dictionary indicating the status and paths of generated files.
        """
        self.logger.info(f"[{self.name}] Starting report generation.")

        # Define filenames
        all_data_filename = "all_event_data.json"
        compiled_filename = "compiled_results.json"
        report_filename = "token2049_report.txt"

        # Save individual event data
        status_all = self._save_json_results(all_event_data, all_data_filename)

        # Save compiled data
        status_compiled = self._save_json_results(compiled_data, compiled_filename)

        try:
            # Log types just before the call
            self.logger.debug(
                f"[{self.name}] Before calling _create_readable_report_content:"
            )
            self.logger.debug(
                f"[{self.name}]   Type of all_event_data variable: {type(all_event_data)}"
            )
            self.logger.debug(
                f"[{self.name}]   Type of compiled_data variable: {type(compiled_data)}"
            )

            # Pass all_event_data (List) first, then compiled_data (Dict)
            report_content = self._create_readable_report_content(
                all_event_data, compiled_data
            )

            report_filepath = self._save_text_report(report_content, report_filename)
            self.logger.info(
                f"[{self.name}] Report generated successfully and saved to {report_filepath}"
            )
        except Exception as e:
            self.logger.error(f"[{self.name}] Error generating report: {e}")
            report_filepath = None

        # Determine overall status
        final_status = "Success"
        if (
            "Error" in status_all
            or "Error" in status_compiled
            or report_filepath is None
        ):
            final_status = "Partial Failure"  # Or "Failure" depending on criticality

        files_generated = [
            os.path.join(OUTPUT_DIR, f)
            for f, status in [
                (all_data_filename, status_all),
                (compiled_filename, status_compiled),
                (report_filename, report_filepath),
            ]
            if status is not None and "Error" not in status
        ]

        self.logger.info(
            f"[{self.name}] Report generation finished with status: {final_status}"
        )

        return {
            "status": final_status,
            "files_generated": files_generated,
            "all_data_save_status": status_all,
            "compiled_data_save_status": status_compiled,
            "report_save_status": report_filepath,
        }


# Instantiate the agent
# report_generator_agent = ReportGeneratorAgent() # Remove instantiation here
