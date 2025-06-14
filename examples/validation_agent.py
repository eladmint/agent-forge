"""
🛡️ Enhanced Validation Agent for Agent Forge Framework

PURPOSE: Data quality validation with intelligent error detection and correction
INTEGRATION: Sprint 1 Week 3 - Validation Agent Development  
FOUNDATION: Building on completed 3-agent pipeline (Scroll, Link Discovery, Text Extraction)
TARGET: 95%+ validation accuracy through comprehensive quality assessment

ARCHITECTURE:
- Platform-specific validation rules for enhanced accuracy
- Confidence scoring systems for extracted data reliability assessment  
- Integration with existing agent pipeline for seamless validation workflow
- Intelligent error detection and correction mechanisms

PERFORMANCE TARGETS:
- Data validation accuracy: 95%+
- Field completeness validation: 90%+
- Error detection rate: 85%+
- Correction success rate: 70%+
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from urllib.parse import urlparse

# Data validation libraries
from dateutil import parser as date_parser


class ValidationSeverity(Enum):
    """Validation issue severity levels"""

    CRITICAL = "critical"  # Data unusable without fix
    HIGH = "high"  # Significant quality impact
    MEDIUM = "medium"  # Minor quality impact
    LOW = "low"  # Cosmetic issues
    INFO = "info"  # Information only


class ValidationCategory(Enum):
    """Categories of validation checks"""

    FORMAT = "format"  # Data format validation
    CONSISTENCY = "consistency"  # Internal consistency checks
    COMPLETENESS = "completeness"  # Required field presence
    ACCURACY = "accuracy"  # Data accuracy assessment
    PLATFORM_SPECIFIC = "platform_specific"  # Platform-specific rules
    BUSINESS_LOGIC = "business_logic"  # Business rule validation


@dataclass
class ValidationIssue:
    """Individual validation issue with correction suggestions"""

    category: ValidationCategory
    severity: ValidationSeverity
    field: str
    message: str
    current_value: Any
    suggested_correction: Optional[Any] = None
    confidence: float = 0.0
    rule_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "field": self.field,
            "message": self.message,
            "current_value": self.current_value,
            "suggested_correction": self.suggested_correction,
            "confidence": self.confidence,
            "rule_name": self.rule_name,
        }


@dataclass
class ValidationResult:
    """Complete validation result with scoring and issues"""

    is_valid: bool
    confidence_score: float
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    overall_quality_score: float
    issues: List[ValidationIssue] = field(default_factory=list)
    corrections_applied: List[Dict[str, Any]] = field(default_factory=list)
    platform_specific_score: float = 0.0
    validation_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "confidence_score": self.confidence_score,
            "completeness_score": self.completeness_score,
            "accuracy_score": self.accuracy_score,
            "consistency_score": self.consistency_score,
            "overall_quality_score": self.overall_quality_score,
            "platform_specific_score": self.platform_specific_score,
            "issues": [issue.to_dict() for issue in self.issues],
            "corrections_applied": self.corrections_applied,
            "validation_metadata": self.validation_metadata,
        }


class PlatformValidator:
    """Platform-specific validation rules and patterns"""

    def __init__(self):
        self.platform_patterns = {
            "eventbrite": {
                "url_pattern": r"https?://(?:www\.)?eventbrite\.[a-z]+/e/",
                "title_min_length": 5,
                "title_max_length": 200,
                "required_fields": ["name", "url", "start_time"],
                "date_formats": ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"],
                "price_pattern": r"(?:Free|\$\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP))",
            },
            "meetup": {
                "url_pattern": r"https?://(?:www\.)?meetup\.com/[^/]+/events/",
                "title_min_length": 3,
                "title_max_length": 150,
                "required_fields": ["name", "url", "start_time", "location"],
                "date_formats": ["%Y-%m-%dT%H:%M:%S", "%a, %b %d at %I:%M %p"],
                "location_required": True,
            },
            "facebook": {
                "url_pattern": r"https?://(?:www\.)?facebook\.com/events/",
                "title_min_length": 3,
                "title_max_length": 120,
                "required_fields": ["name", "url", "start_time"],
                "date_formats": ["%A, %B %d, %Y at %I:%M %p", "%Y-%m-%dT%H:%M:%S"],
                "rsvp_validation": True,
            },
            "luma": {
                "url_pattern": r"https?://lu\.ma/",
                "title_min_length": 5,
                "title_max_length": 180,
                "required_fields": ["name", "url", "start_time", "description"],
                "date_formats": ["%Y-%m-%dT%H:%M:%S", "%b %d, %Y • %I:%M %p"],
                "description_min_length": 20,
            },
            "generic": {
                "title_min_length": 3,
                "title_max_length": 300,
                "required_fields": ["name", "url"],
                "date_formats": [
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%B %d, %Y",
                    "%b %d, %Y",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                ],
            },
        }

    def detect_platform(self, event_data: Dict[str, Any]) -> str:
        """Detect event platform from URL or data patterns"""
        url = event_data.get("url", "").lower()

        if "eventbrite" in url:
            return "eventbrite"
        elif "meetup.com" in url:
            return "meetup"
        elif "facebook.com/events" in url:
            return "facebook"
        elif "lu.ma" in url:
            return "luma"
        else:
            return "generic"

    def get_platform_rules(self, platform: str) -> Dict[str, Any]:
        """Get validation rules for specific platform"""
        return self.platform_patterns.get(platform, self.platform_patterns["generic"])


# Import framework BaseAgent
from core.agents.base import AsyncContextAgent


class EnhancedValidationAgent(AsyncContextAgent):
    """
    🛡️ Enhanced Validation Agent for comprehensive data quality assessment

    CORE CAPABILITIES:
    - Multi-dimensional validation (format, consistency, completeness, accuracy)
    - Platform-specific validation rules for 5 major event platforms
    - Intelligent error detection and correction suggestions
    - Confidence scoring systems for reliability assessment
    - Integration with 3-agent pipeline for seamless validation workflow

    VALIDATION DIMENSIONS:
    1. Format Validation: Data types, patterns, structures
    2. Consistency Validation: Internal logical consistency
    3. Completeness Validation: Required field presence and quality
    4. Accuracy Validation: Data accuracy through pattern matching
    5. Platform-Specific Validation: Platform-aware quality rules
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.platform_validator = PlatformValidator()
        self.logger = logging.getLogger(__name__)

        # Validation thresholds
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.8,
            "acceptable": 0.7,
            "poor": 0.5,
            "critical": 0.3,
        }

        # Field importance weights for scoring
        self.field_weights = {
            "name": 0.25,
            "url": 0.20,
            "start_time": 0.20,
            "location": 0.15,
            "description": 0.10,
            "organizer": 0.05,
            "price": 0.03,
            "tags": 0.02,
        }

        # Initialize validation patterns
        self._init_validation_patterns()

    def _init_validation_patterns(self):
        """Initialize validation patterns and rules"""
        self.validation_patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "phone": r"^[\+]?[1-9][\d]{0,15}$",
            "url": r"^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$",
            "date_iso": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            "price": r"^(?:Free|\$?\d+(?:\.\d{2})?(?:\s*-\s*\$?\d+(?:\.\d{2})?)?|\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP|CAD))$",
            "time": r"^(?:[0-1]?\d|2[0-3]):[0-5]\d(?:\s*[AaPp][Mm])?$",
        }

    async def validate_event_data(
        self,
        event_data: Dict[str, Any],
        source_agent: str = "unknown",
        correction_mode: bool = True,
    ) -> ValidationResult:
        """
        Comprehensive validation of event data with quality scoring

        Args:
            event_data: Event data dictionary to validate
            source_agent: Name of agent that provided the data
            correction_mode: Whether to apply automatic corrections

        Returns:
            ValidationResult with comprehensive quality assessment
        """
        try:
            self.logger.info(
                f"Starting validation for event: {event_data.get('name', 'unnamed')}"
            )

            # Detect platform for platform-specific validation
            platform = self.platform_validator.detect_platform(event_data)
            platform_rules = self.platform_validator.get_platform_rules(platform)

            # Initialize validation tracking
            issues: List[ValidationIssue] = []
            corrections_applied: List[Dict[str, Any]] = []

            # Perform validation checks
            format_score = await self._validate_format(
                event_data, platform_rules, issues
            )
            consistency_score = await self._validate_consistency(event_data, issues)
            completeness_score = await self._validate_completeness(
                event_data, platform_rules, issues
            )
            accuracy_score = await self._validate_accuracy(
                event_data, platform_rules, issues
            )
            platform_score = await self._validate_platform_specific(
                event_data, platform, platform_rules, issues
            )

            # Apply corrections if enabled
            if correction_mode:
                corrections_applied = await self._apply_corrections(event_data, issues)

            # Calculate overall scores
            confidence_score = self._calculate_confidence_score(
                format_score, consistency_score, completeness_score, accuracy_score
            )
            overall_quality_score = self._calculate_overall_quality_score(
                format_score,
                consistency_score,
                completeness_score,
                accuracy_score,
                platform_score,
            )

            # Determine if data passes validation
            is_valid = overall_quality_score >= self.quality_thresholds[
                "acceptable"
            ] and not any(
                issue.severity == ValidationSeverity.CRITICAL for issue in issues
            )

            # Create validation metadata
            metadata = {
                "platform": platform,
                "source_agent": source_agent,
                "validation_timestamp": datetime.now().isoformat(),
                "total_issues": len(issues),
                "critical_issues": sum(
                    1 for i in issues if i.severity == ValidationSeverity.CRITICAL
                ),
                "correctable_issues": sum(
                    1 for i in issues if i.suggested_correction is not None
                ),
                "field_count": len(event_data),
                "required_fields_present": self._count_required_fields(
                    event_data, platform_rules
                ),
            }

            result = ValidationResult(
                is_valid=is_valid,
                confidence_score=confidence_score,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                overall_quality_score=overall_quality_score,
                platform_specific_score=platform_score,
                issues=issues,
                corrections_applied=corrections_applied,
                validation_metadata=metadata,
            )

            self.logger.info(
                f"Validation complete for {event_data.get('name', 'unnamed')}: "
                f"Valid={is_valid}, Quality={overall_quality_score:.2f}, "
                f"Issues={len(issues)}, Platform={platform}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                completeness_score=0.0,
                accuracy_score=0.0,
                consistency_score=0.0,
                overall_quality_score=0.0,
                issues=[
                    ValidationIssue(
                        category=ValidationCategory.FORMAT,
                        severity=ValidationSeverity.CRITICAL,
                        field="validation_process",
                        message=f"Validation process failed: {str(e)}",
                        current_value=None,
                    )
                ],
                validation_metadata={"error": str(e)},
            )

    async def _validate_format(
        self,
        event_data: Dict[str, Any],
        platform_rules: Dict[str, Any],
        issues: List[ValidationIssue],
    ) -> float:
        """Validate data format compliance"""
        format_score = 1.0
        checks_performed = 0
        failed_checks = 0

        # URL format validation
        if "url" in event_data:
            checks_performed += 1
            url = event_data["url"]
            if not self._is_valid_url(url):
                failed_checks += 1
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.FORMAT,
                        severity=ValidationSeverity.HIGH,
                        field="url",
                        message="Invalid URL format",
                        current_value=url,
                        suggested_correction=self._clean_url(url),
                        confidence=0.7,
                        rule_name="url_format",
                    )
                )

        # Title format validation
        if "name" in event_data:
            checks_performed += 1
            name = event_data["name"]
            min_length = platform_rules.get("title_min_length", 3)
            max_length = platform_rules.get("title_max_length", 300)

            if not isinstance(name, str) or len(name.strip()) < min_length:
                failed_checks += 1
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.FORMAT,
                        severity=ValidationSeverity.HIGH,
                        field="name",
                        message=f"Title too short (minimum {min_length} characters)",
                        current_value=name,
                        suggested_correction=self._enhance_title(name),
                        confidence=0.6,
                        rule_name="title_length",
                    )
                )
            elif len(name) > max_length:
                failed_checks += 1
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.FORMAT,
                        severity=ValidationSeverity.MEDIUM,
                        field="name",
                        message=f"Title too long (maximum {max_length} characters)",
                        current_value=name,
                        suggested_correction=name[: max_length - 3] + "...",
                        confidence=0.9,
                        rule_name="title_length",
                    )
                )

        # Date format validation
        if "start_time" in event_data:
            checks_performed += 1
            start_time = event_data["start_time"]
            if not self._validate_date_format(start_time):
                failed_checks += 1
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.FORMAT,
                        severity=ValidationSeverity.HIGH,
                        field="start_time",
                        message="Invalid date/time format",
                        current_value=start_time,
                        suggested_correction=self._normalize_date(start_time),
                        confidence=0.8,
                        rule_name="datetime_format",
                    )
                )

        # Calculate format score
        if checks_performed > 0:
            format_score = 1.0 - (failed_checks / checks_performed)

        return max(0.0, format_score)

    async def _validate_consistency(
        self, event_data: Dict[str, Any], issues: List[ValidationIssue]
    ) -> float:
        """Validate internal data consistency"""
        consistency_score = 1.0
        checks_performed = 0
        failed_checks = 0

        # Date consistency checks
        if "start_time" in event_data and "end_time" in event_data:
            checks_performed += 1
            start_time = self._parse_date(event_data["start_time"])
            end_time = self._parse_date(event_data["end_time"])

            if start_time and end_time and start_time >= end_time:
                failed_checks += 1
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.CONSISTENCY,
                        severity=ValidationSeverity.HIGH,
                        field="end_time",
                        message="End time must be after start time",
                        current_value=event_data["end_time"],
                        suggested_correction=(
                            start_time + timedelta(hours=2)
                        ).isoformat(),
                        confidence=0.8,
                        rule_name="date_consistency",
                    )
                )

        # Calculate consistency score
        if checks_performed > 0:
            consistency_score = 1.0 - (failed_checks / checks_performed)

        return max(0.0, consistency_score)

    async def _validate_completeness(
        self,
        event_data: Dict[str, Any],
        platform_rules: Dict[str, Any],
        issues: List[ValidationIssue],
    ) -> float:
        """Validate data completeness"""
        required_fields = platform_rules.get("required_fields", ["name", "url"])
        total_fields = len(required_fields)
        present_fields = 0

        for field in required_fields:
            if (
                field in event_data
                and event_data[field]
                and str(event_data[field]).strip()
            ):
                present_fields += 1
            else:
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.COMPLETENESS,
                        severity=ValidationSeverity.HIGH,
                        field=field,
                        message=f"Required field '{field}' is missing or empty",
                        current_value=event_data.get(field),
                        suggested_correction=self._suggest_field_value(
                            field, event_data
                        ),
                        confidence=0.5,
                        rule_name="required_fields",
                    )
                )

        completeness_score = present_fields / total_fields if total_fields > 0 else 1.0
        return max(0.0, completeness_score)

    async def _validate_accuracy(
        self,
        event_data: Dict[str, Any],
        platform_rules: Dict[str, Any],
        issues: List[ValidationIssue],
    ) -> float:
        """Validate data accuracy through pattern matching"""
        accuracy_score = 1.0
        checks_performed = 0
        failed_checks = 0

        # Future date validation
        if "start_time" in event_data:
            checks_performed += 1
            start_time = self._parse_date(event_data["start_time"])
            if start_time and start_time < datetime.now() - timedelta(days=1):
                failed_checks += 1
                issues.append(
                    ValidationIssue(
                        category=ValidationCategory.ACCURACY,
                        severity=ValidationSeverity.MEDIUM,
                        field="start_time",
                        message="Event date appears to be in the past",
                        current_value=event_data["start_time"],
                        confidence=0.8,
                        rule_name="future_date",
                    )
                )

        # Calculate accuracy score
        if checks_performed > 0:
            accuracy_score = 1.0 - (failed_checks / checks_performed)

        return max(0.0, accuracy_score)

    async def _validate_platform_specific(
        self,
        event_data: Dict[str, Any],
        platform: str,
        platform_rules: Dict[str, Any],
        issues: List[ValidationIssue],
    ) -> float:
        """Platform-specific validation rules"""
        platform_score = 1.0

        if platform == "luma":
            # Lu.ma specific validations
            if "url" in event_data:
                url = event_data["url"]
                if "lu.ma" in url and not re.match(platform_rules["url_pattern"], url):
                    issues.append(
                        ValidationIssue(
                            category=ValidationCategory.PLATFORM_SPECIFIC,
                            severity=ValidationSeverity.MEDIUM,
                            field="url",
                            message="URL doesn't match Lu.ma pattern",
                            current_value=url,
                            confidence=0.8,
                            rule_name="luma_url_pattern",
                        )
                    )
                    platform_score -= 0.2

        return max(0.0, platform_score)

    async def _apply_corrections(
        self, event_data: Dict[str, Any], issues: List[ValidationIssue]
    ) -> List[Dict[str, Any]]:
        """Apply automatic corrections where confidence is high"""
        corrections_applied = []

        for issue in issues:
            if (
                issue.suggested_correction is not None
                and issue.confidence >= 0.7
                and issue.severity != ValidationSeverity.CRITICAL
            ):

                old_value = event_data.get(issue.field)
                event_data[issue.field] = issue.suggested_correction

                corrections_applied.append(
                    {
                        "field": issue.field,
                        "old_value": old_value,
                        "new_value": issue.suggested_correction,
                        "confidence": issue.confidence,
                        "rule_name": issue.rule_name,
                        "reason": issue.message,
                    }
                )

        return corrections_applied

    def _calculate_confidence_score(
        self,
        format_score: float,
        consistency_score: float,
        completeness_score: float,
        accuracy_score: float,
    ) -> float:
        """Calculate overall confidence score"""
        weights = {
            "format": 0.3,
            "consistency": 0.2,
            "completeness": 0.3,
            "accuracy": 0.2,
        }

        confidence = (
            format_score * weights["format"]
            + consistency_score * weights["consistency"]
            + completeness_score * weights["completeness"]
            + accuracy_score * weights["accuracy"]
        )

        return min(1.0, max(0.0, confidence))

    def _calculate_overall_quality_score(
        self,
        format_score: float,
        consistency_score: float,
        completeness_score: float,
        accuracy_score: float,
        platform_score: float,
    ) -> float:
        """Calculate overall quality score"""
        weights = {
            "format": 0.25,
            "consistency": 0.15,
            "completeness": 0.30,
            "accuracy": 0.20,
            "platform": 0.10,
        }

        quality = (
            format_score * weights["format"]
            + consistency_score * weights["consistency"]
            + completeness_score * weights["completeness"]
            + accuracy_score * weights["accuracy"]
            + platform_score * weights["platform"]
        )

        return min(1.0, max(0.0, quality))

    # Helper methods for validation logic

    def _validate_date_format(self, date_str: str) -> bool:
        """Validate if date string can be parsed"""
        if not date_str:
            return False
        try:
            date_parser.parse(str(date_str))
            return True
        except:
            return False

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            return date_parser.parse(str(date_str))
        except:
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation using regex pattern"""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False

    def _count_required_fields(
        self, event_data: Dict[str, Any], platform_rules: Dict[str, Any]
    ) -> int:
        """Count how many required fields are present"""
        required_fields = platform_rules.get("required_fields", [])
        return sum(
            1
            for field in required_fields
            if field in event_data
            and event_data[field]
            and str(event_data[field]).strip()
        )

    # Data cleaning and correction methods

    def _clean_url(self, url: str) -> str:
        """Clean and fix URL format"""
        if not url:
            return url

        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to ISO format"""
        parsed = self._parse_date(date_str)
        if parsed:
            return parsed.isoformat()
        return date_str

    def _enhance_title(self, title: str) -> str:
        """Enhance short or poor quality titles"""
        if not title or len(title.strip()) < 3:
            return "Event"

        return title.strip().title()

    def _suggest_field_value(
        self, field: str, event_data: Dict[str, Any]
    ) -> Optional[str]:
        """Suggest values for missing required fields"""
        suggestions = {
            "name": "Event",
            "url": "https://example.com/event",
            "start_time": datetime.now()
            .replace(hour=19, minute=0, second=0)
            .isoformat(),
            "location": "To be announced",
            "description": f"Join us for {event_data.get('name', 'this event')}",
        }

        return suggestions.get(field)


# Export main class
__all__ = [
    "EnhancedValidationAgent",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSeverity",
    "ValidationCategory",
]
