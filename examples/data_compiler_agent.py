"""Agent responsible for compiling and de-duplicating event data - Framework-free implementation."""

import logging
from typing import Any, Dict, List, Optional, Set

# Import data models used by this agent
from core.agents.models import (
    OrganizationModel,
    RefinedEventData,
    SpeakerDetailModel,
)

# Import framework BaseAgent
from core.agents.base import AsyncContextAgent


class DataCompilerAgent(AsyncContextAgent):
    """Compiles and de-duplicates speaker and organization data.

    This agent takes a list of `RefinedEventData` objects (presumably extracted
    from multiple events or sources) and processes them to create consolidated lists
    of unique speakers and unique organization names.

    De-duplication for speakers is based on a signature combining the speaker's
    name and their organization (both lowercased and stripped).
    Organization names are de-duplicated as strings.

    Attributes:
        logger: An optional logger instance for logging agent activities.
        name: Name of the agent.
    """

    def __init__(
        self,
        name: str = "DataCompilerAgent",
        logger: Optional[logging.Logger] = None,
    ):
        """Initializes the framework-free DataCompilerAgent.

        Args:
            name: The name of the agent.
            logger: An optional logger instance. If None, a default
                    logger for this class is created.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.logger.info(
            "[%s] initialized framework-free DataCompilerAgent.", self.name
        )

    async def run_async(
        self, event_data_list: List[RefinedEventData]
    ) -> Dict[str, List[Any]]:
        """Processes a list of RefinedEventData to compile unique speakers and organizations.

        Args:
            event_data_list: A list of `RefinedEventData` Pydantic models,
                             each representing data extracted from an event.

        Returns:
            A dictionary containing two keys:
            - "unique_speakers": A list of dictionaries, where each dictionary
              represents a unique speaker (de-duplicated by name and organization).
              Speaker details are obtained via `SpeakerDetailModel.model_dump()`.
            - "unique_organizations": A sorted list of unique organization names (strings).

        Raises:
            This method aims to handle errors internally by skipping problematic
            event entries and logging warnings/errors. It should generally not
            raise exceptions for individual data processing issues but will return
            compiled data from valid entries.
        """
        self.logger.info(
            "[%s] Starting compilation for %d refined event entries.",
            self.name,
            len(event_data_list),
        )

        all_speakers_objects: List[SpeakerDetailModel] = (
            []
        )  # Stores all valid SpeakerDetailModel instances found
        all_organization_names: Set[str] = (
            set()
        )  # Stores unique organization names (strings)

        # Iterate through each event's data in the input list
        for i, event in enumerate(event_data_list):
            try:
                # Validate the type of the event entry
                if not isinstance(event, RefinedEventData):
                    self.logger.warning(
                        "[%s] Skipping invalid data entry at index %d: type %s, expected RefinedEventData. Content: %s",
                        self.name,
                        i,
                        type(event),
                        str(event)[:200],  # Log type and snippet of content
                    )
                    continue  # Skip to the next event entry

                event_name_for_logging = (
                    event.event_name or f"Unknown Event (index {i})"
                )

                # --- Process Speakers from the current event ---
                if (
                    event.speakers
                ):  # Check if there are any speakers listed for the event
                    for speaker_detail in event.speakers:
                        # Validate speaker data: must be SpeakerDetailModel and have a name
                        if (
                            isinstance(speaker_detail, SpeakerDetailModel)
                            and speaker_detail.name  # Ensure speaker has a name
                        ):
                            all_speakers_objects.append(speaker_detail)
                        else:
                            self.logger.warning(
                                "[%s] Skipping invalid speaker entry in event '%s': Missing name or invalid type. Data: %s",
                                self.name,
                                event_name_for_logging,
                                str(speaker_detail)[:200],
                            )

                # --- Process Organizations from the current event ---
                # Organizations can come from 'event.organizers', 'event.sponsors_partners',
                # or 'speaker_detail.organization'.

                # 1. From event.organizers (List[OrganizationModel])
                if event.organizers:
                    for org_model in event.organizers:
                        if (
                            isinstance(org_model, OrganizationModel)
                            and org_model.name  # Ensure organization has a name
                            and org_model.name.strip()  # Ensure name is not just whitespace
                        ):
                            all_organization_names.add(org_model.name.strip())
                        else:
                            self.logger.warning(
                                "[%s] Skipping invalid organizer entry in event '%s': Missing name or invalid type. Data: %s",
                                self.name,
                                event_name_for_logging,
                                str(org_model)[:200],
                            )

                # 2. From event.sponsors_partners (List[OrganizationModel])
                if event.sponsors_partners:
                    for org_model in event.sponsors_partners:
                        if (
                            isinstance(org_model, OrganizationModel)
                            and org_model.name
                            and org_model.name.strip()
                        ):
                            all_organization_names.add(org_model.name.strip())
                        else:
                            self.logger.warning(
                                "[%s] Skipping invalid sponsor/partner entry in event '%s': Missing name or invalid type. Data: %s",
                                self.name,
                                event_name_for_logging,
                                str(org_model)[:200],
                            )

                # 3. From speaker_detail.organization (string attribute within SpeakerDetailModel)
                if event.speakers:  # Re-check speakers list for their organizations
                    for speaker_detail in event.speakers:
                        # Ensure speaker_detail itself is a valid model instance and has an organization attribute
                        if (
                            isinstance(speaker_detail, SpeakerDetailModel)
                            and speaker_detail.organization
                        ):
                            org_name_from_speaker = speaker_detail.organization.strip()
                            # Add if the organization name is meaningful (not empty and not a placeholder like "N/A")
                            if (
                                org_name_from_speaker
                                and org_name_from_speaker.lower() != "n/a"
                            ):
                                all_organization_names.add(org_name_from_speaker)

            except (
                Exception
            ) as e:  # Catch any unexpected error during the processing of a single event
                # Log the error with event identifier and stack trace, then continue with the next event.
                event_identifier = (
                    event.event_name
                    if isinstance(event, RefinedEventData) and event.event_name
                    else f"entry at index {i}"
                )
                self.logger.error(
                    "[%s] Unexpected error processing %s: %s",
                    self.name,
                    event_identifier,
                    e,
                    exc_info=True,  # Include stack trace for unexpected errors
                )
                continue  # Skip to the next event

        # --- De-duplicate Speakers (based on a signature of name + organization) ---
        # This helps differentiate speakers who might have the same name but belong to different organizations.
        unique_speakers: List[SpeakerDetailModel] = []
        seen_speaker_signatures: Set[str] = set()

        for speaker_obj in all_speakers_objects:
            # Create a unique signature: lowercased name and lowercased organization.
            # Default organization to an empty string if it's None to prevent errors.
            name_lower = speaker_obj.name.strip().lower()
            org_lower = (speaker_obj.organization or "").strip().lower()

            signature = f"{name_lower}@{org_lower}"  # Composite key for de-duplication

            if signature not in seen_speaker_signatures:
                seen_speaker_signatures.add(signature)
                unique_speakers.append(speaker_obj)
            else:
                # Optional: Log when a duplicate speaker signature is encountered. Can be verbose.
                self.logger.debug(
                    "[%s] Duplicate speaker signature encountered and skipped: %s",
                    self.name,
                    signature,
                )
                # Future enhancement: Could merge details from duplicate entries (e.g., combine social links).
                # For now, the first encountered instance with a unique signature is kept.

        # --- Finalize and Sort Organizations ---
        # Filter out any potentially empty strings that might have been added, then sort case-insensitively.
        sorted_organizations = sorted(
            list(
                org_name
                for org_name in all_organization_names
                if org_name and org_name.strip()
            ),
            key=str.lower,  # Case-insensitive sort for organization names
        )

        self.logger.info(
            "[%s] Compilation finished. Found %d unique speakers (by name+org) and %d unique organization names.",
            self.name,
            len(unique_speakers),
            len(sorted_organizations),
        )

        # Convert SpeakerDetailModel Pydantic objects to dictionaries for the output.
        # This is done to maintain compatibility with consumers that might expect dicts.
        # Ideally, downstream components would also use the Pydantic models for type safety.
        unique_speakers_dicts = [
            s.model_dump(exclude_none=True)
            for s in unique_speakers  # `exclude_none=True` omits fields that are None
        ]

        # Return the compiled and de-duplicated lists.
        return {
            "unique_speakers": unique_speakers_dicts,  # List of speaker dictionaries
            "unique_organizations": sorted_organizations,  # List of organization name strings
        }
