"""
Event Data Refiner Agent

🎯 PART OF MAIN EXTRACTOR SYSTEM
This agent is a core component of the comprehensive 13+ agent extraction framework.
Main orchestrator: /main_extractor.py (previously enhanced_orchestrator.py)

This agent takes extracted event data and refines it using Vertex AI's Gemini model.
It performs intelligent analysis to improve data quality, standardize formats,
and extract additional insights from the raw event information.

The main extractor coordinates this agent along with 12+ other specialized agents
for comprehensive crypto conference event extraction with database integration.
"""

import json
import logging
from typing import Any, Dict, Optional

from pydantic import ValidationError
from vertexai.generative_models import GenerationConfig, GenerativeModel, Part

from extraction.agents.models import (
    RefinedEventData,
)  # Import the new models

# Configure logger for this agent
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

# Configuration for the Vertex AI model (can be externalized later)
REFINER_MODEL_NAME = "gemini-1.5-flash-001"  # Or another suitable model
REFINER_PROJECT_ID = None  # Needs to be configured, e.g., from env
REFINER_LOCATION = None  # Needs to be configured, e.g., from env

# Safety settings for the generative model (can be adjusted)
SAFETY_SETTINGS = {
    # HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Generation config for the model
GENERATION_CONFIG = GenerationConfig(
    temperature=0.2,  # Lower temperature for more factual extraction
    top_p=0.8,
    top_k=20,
    max_output_tokens=8192,  # Maximize output tokens for potentially large JSON
    response_mime_type="application/json",  # Request JSON output
)


class EventDataRefinerAgent:
    """AI-powered data enhancement and structuring - Framework-free implementation."""

    def __init__(
        self,
        name: str = "EventDataRefinerAgent",
        model_name: str = REFINER_MODEL_NAME,
        project_id: Optional[str] = REFINER_PROJECT_ID,
        location: Optional[str] = REFINER_LOCATION,
        logger_instance: Optional[logging.Logger] = None,
    ):
        """Initialize the framework-free Event Data Refiner Agent."""
        self.name = name
        self.logger = logger_instance if logger_instance else logger

        self.logger.info(
            f"[{self.name}] Initialized framework-free Event Data Refiner Agent"
        )

        if not project_id or not location:
            self.logger.warning(
                f"[{self.name}] Vertex AI project_id or location not provided. LLM calls will fail."
            )
            self.model = None
        else:
            try:
                self.model = GenerativeModel(
                    model_name,
                    # project=project_id, # project and location are picked up from gcloud auth/env
                    # location=location,
                )
                self.logger.info(
                    f"[{self.name}] Initialized Vertex AI model: {model_name}"
                )
            except Exception as e:
                self.logger.error(
                    f"[{self.name}] Failed to initialize Vertex AI model {model_name}: {e}"
                )
                self.model = None

        self.project_id = project_id
        self.location = location

    def _generate_extraction_prompt(self, raw_text: str, source_url: str) -> str:
        # Create a JSON schema from the Pydantic model to guide the LLM
        # Pydantic v2 .model_json_schema(), v1 .schema_json()
        try:
            schema = RefinedEventData.model_json_schema()
        except AttributeError:  # Fallback for Pydantic v1 if necessary
            schema = RefinedEventData.schema_json()

        prompt = f"""
Given the following raw text extracted from an event page ({source_url}), please act as an expert event data analyst.
Your task is to extract detailed and structured information about the event and respond ONLY with a valid JSON object that strictly adheres to the provided JSON schema.

JSON Schema:
```json
{schema}
```

Key instructions for extraction:
- **event_name**: The official title of the event.
- **source_url**: Use the provided source URL: {source_url}
- **dates_times**: Extract start_date (YYYY-MM-DD), start_time (HH:MM AM/PM or 24-hour), end_date, end_time, and timezone. If end date/time are not specified, they can be null.
- **location**: Extract venue name, full address, city, and country if available.
- **description_summary**: Provide a concise summary of the event. If the text is short, this can be the full description.
- **full_description**: Provide the full description if it's substantial and distinct from the summary.
- **cost_usd**: If a price in USD is mentioned, extract it as a float. If free, set to 0.0. If not mentioned, set to null.
- **cost_details**: Any text describing the cost (e.g., "Free", "$50 Early Bird", "Tickets from 20 EUR").
- **website**: Official event website, if different from the source_url.
- **tags/categories**: Relevant keywords or categories.
- **event_social_media_links**: Links to social media for the event itself.
- **organizers**: List of organizations hosting/organizing. Include name and URL if found.
- **speakers**: List of speakers. For each, extract name, title, organization, profile URL (if available), and social media links.
- **sponsors_partners**: List of organizations sponsoring or partnering. Include name and URL if found.
- **raw_visible_text_snippet**: A short, relevant snippet (e.g., first 200 characters) of the raw text for context.
- **extractor_status**: You can leave this null or set to "Refined by LLM".

If a piece of information is not available in the text, set the corresponding JSON field to null (for optional fields) or an empty list (for list fields). Do not make up information.
The output MUST be a single JSON object. Do not include any explanatory text before or after the JSON.

Raw Text:
---
{raw_text[:15000]} 
---
(Note: Text might be truncated for brevity in this prompt, process the full text provided programmatically)

JSON Output:
"""
        return prompt

    async def run_async(
        self, extracted_data: Dict[str, Any]
    ) -> Optional[RefinedEventData]:
        if not self.model:
            self.logger.error(
                f"[{self.name}] LLM model not initialized. Cannot refine data."
            )
            return None

        raw_text = extracted_data.get("visible_text")
        source_url = extracted_data.get("url", "N/A")
        extractor_status = extracted_data.get("extraction_status", "N/A")

        if not raw_text:
            self.logger.warning(
                f"[{self.name}] No raw text provided from extractor for URL {source_url}. Skipping refinement."
            )
            return None

        self.logger.info(
            f"[{self.name}] Starting data refinement for URL: {source_url} (Text length: {len(raw_text)})"
        )

        prompt = self._generate_extraction_prompt(raw_text, source_url)

        try:
            # self.logger.debug(f"[{self.name}] Generated prompt for LLM: {prompt[:500]}...") # Log first 500 chars
            response = await self.model.generate_content_async(
                [Part.from_text(prompt)],  # Content can be a list of Parts
                generation_config=GENERATION_CONFIG,
                # safety_settings=SAFETY_SETTINGS, # Not passing safety settings for now, can be added
            )

            self.logger.debug(f"[{self.name}] Raw LLM response received.")
            # self.logger.debug(f"LLM Response: {response}")

            # Assuming response_mime_type="application/json" works as expected
            # The response.text should be the JSON string.
            if not response.candidates or not response.candidates[0].content.parts:
                self.logger.error(
                    f"[{self.name}] LLM returned no valid candidates or parts in response for {source_url}."
                )
                return None

            json_text = response.candidates[0].content.parts[0].text
            # self.logger.debug(f"[{self.name}] LLM output (JSON text): {json_text[:500]}...")

            # Clean the JSON string: remove potential markdown backticks and "json" prefix
            cleaned_json_text = json_text.strip()
            if cleaned_json_text.startswith("```json"):
                cleaned_json_text = cleaned_json_text[7:]
            elif cleaned_json_text.startswith("```"):
                cleaned_json_text = cleaned_json_text[3:]
            if cleaned_json_text.endswith("```"):
                cleaned_json_text = cleaned_json_text[:-3]

            cleaned_json_text = cleaned_json_text.strip()

            llm_output = json.loads(cleaned_json_text)

            # Add source_url and extractor_status from original data if LLM didn't populate them
            if "source_url" not in llm_output or not llm_output["source_url"]:
                llm_output["source_url"] = source_url
            if (
                "extractor_status" not in llm_output
                or not llm_output["extractor_status"]
            ):
                llm_output["extractor_status"] = extractor_status

            refined_data = RefinedEventData(**llm_output)
            self.logger.info(
                f"[{self.name}] Successfully parsed LLM output into RefinedEventData for {source_url}."
            )
            return refined_data

        except json.JSONDecodeError as e:
            self.logger.error(
                f"[{self.name}] Failed to decode JSON from LLM response for {source_url}: {e}"
            )
            self.logger.error(
                f"[{self.name}] Offending JSON string snippet: {cleaned_json_text[:500]}"
            )
            return None
        except ValidationError as e:
            self.logger.error(
                f"[{self.name}] Pydantic validation error for LLM output for {source_url}: {e}"
            )
            self.logger.error(
                f"[{self.name}] LLM output that failed validation: {llm_output}"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during LLM call or processing for {source_url}: {e}"
            )
            # Log full response for debugging if it's not too large or sensitive
            # if 'response' in locals() and response:
            #    self.logger.debug(f"Full response object: {response}")
            return None
