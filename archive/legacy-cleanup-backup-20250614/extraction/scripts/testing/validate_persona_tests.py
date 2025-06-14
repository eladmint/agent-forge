#!/usr/bin/env python3
"""
Persona Test Validator and Quality Monitor
Validates persona test quality and monitors test performance over time.
Ensures generated tests are meaningful and maintain quality standards.

Usage:
    python validate_persona_tests.py --validate-all
    python validate_persona_tests.py --monitor-quality
    python validate_persona_tests.py --persona conference-navigator
"""

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


@dataclass
class TestQualityMetrics:
    """Metrics for evaluating test quality."""

    query_complexity_score: float
    response_relevance_score: float
    keyword_coverage_score: float
    language_diversity_score: float
    category_coverage_score: float
    overall_quality_score: float


@dataclass
class PersonaTestAnalysis:
    """Analysis results for a persona's test suite."""

    persona_name: str
    total_queries: int
    categories_covered: List[str]
    languages_covered: List[str]
    avg_query_length: float
    complexity_distribution: Dict[str, int]
    quality_metrics: TestQualityMetrics
    recommendations: List[str]


class PersonaTestValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.persona_dir = self.project_root / "docs" / "ux" / "user-personas"
        self.test_dir = self.project_root / "tests" / "integration"
        self.results_dir = self.project_root / "tests" / "persona_test_results"
        self.validation_dir = self.project_root / "tests" / "persona_validation"

        # Quality thresholds
        self.quality_thresholds = {
            "min_queries_per_persona": 15,
            "min_categories_per_persona": 4,
            "min_avg_query_length": 20,
            "max_avg_query_length": 200,
            "min_keyword_coverage": 0.7,
            "min_complexity_diversity": 3,
            "min_overall_quality": 0.75,
        }

        # Ensure directories exist
        self.validation_dir.mkdir(exist_ok=True)

    def analyze_query_complexity(self, query: str) -> Tuple[str, float]:
        """Analyze the complexity level of a query."""
        # Count different complexity indicators
        word_count = len(query.split())
        question_indicators = len(
            re.findall(r"\b(what|how|when|where|why|which|who)\b", query.lower())
        )
        technical_terms = len(
            re.findall(
                r"\b(blockchain|defi|nft|web3|crypto|ethereum|solana|conference|workshop|networking)\b",
                query.lower(),
            )
        )
        specific_requests = len(
            re.findall(
                r"\b(recommend|suggest|find|search|help|compare|analyze)\b",
                query.lower(),
            )
        )

        # Calculate complexity score
        complexity_score = (
            min(word_count / 20, 1.0) * 0.3  # Word count factor
            + min(question_indicators / 2, 1.0) * 0.2  # Question complexity
            + min(technical_terms / 3, 1.0) * 0.3  # Technical depth
            + min(specific_requests / 2, 1.0) * 0.2  # Action specificity
        )

        # Categorize complexity
        if complexity_score >= 0.8:
            return "high", complexity_score
        elif complexity_score >= 0.5:
            return "medium", complexity_score
        else:
            return "low", complexity_score

    def validate_persona_queries(self, persona_name: str) -> PersonaTestAnalysis:
        """Validate queries for a specific persona."""
        # Load persona documentation
        persona_file = self.persona_dir / f"{persona_name}.md"
        if not persona_file.exists():
            raise FileNotFoundError(f"Persona file not found: {persona_file}")

        # Extract queries using the parser
        sys.path.append(str(self.test_dir))
        from persona_query_parser import PersonaQueryExtractor

        parser = PersonaQueryExtractor()
        test_suite = parser.extract_queries_from_file(persona_file)

        # Convert PersonaTestSuite to simple query list for compatibility
        queries = []
        for query_obj in (
            test_suite.core_queries
            + test_suite.advanced_queries
            + test_suite.interaction_queries
            + test_suite.error_queries
            + test_suite.multi_language_queries
        ):
            queries.append(
                {
                    "query": query_obj.query,
                    "category": query_obj.category,
                    "language": query_obj.language,
                    "expected_keywords": [query_obj.expected_behavior],
                    "test_type": query_obj.test_type,
                    "priority": query_obj.priority,
                }
            )

        if not queries:
            return PersonaTestAnalysis(
                persona_name=persona_name,
                total_queries=0,
                categories_covered=[],
                languages_covered=[],
                avg_query_length=0,
                complexity_distribution={},
                quality_metrics=TestQualityMetrics(0, 0, 0, 0, 0, 0),
                recommendations=[
                    "No queries found - persona documentation may need improvement"
                ],
            )

        # Analyze queries
        categories = set()
        languages = set()
        query_lengths = []
        complexity_counts = {"low": 0, "medium": 0, "high": 0}
        complexity_scores = []

        for query_data in queries:
            query = query_data.get("query", "")
            category = query_data.get("category", "general")
            language = query_data.get("language", "en")

            categories.add(category)
            languages.add(language)
            query_lengths.append(len(query))

            complexity_level, complexity_score = self.analyze_query_complexity(query)
            complexity_counts[complexity_level] += 1
            complexity_scores.append(complexity_score)

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(
            queries, complexity_scores, categories, languages
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            persona_name, len(queries), categories, complexity_counts, quality_metrics
        )

        return PersonaTestAnalysis(
            persona_name=persona_name,
            total_queries=len(queries),
            categories_covered=list(categories),
            languages_covered=list(languages),
            avg_query_length=statistics.mean(query_lengths) if query_lengths else 0,
            complexity_distribution=complexity_counts,
            quality_metrics=quality_metrics,
            recommendations=recommendations,
        )

    def _calculate_quality_metrics(
        self,
        queries: List[Dict],
        complexity_scores: List[float],
        categories: set,
        languages: set,
    ) -> TestQualityMetrics:
        """Calculate comprehensive quality metrics."""

        # Query complexity score (average complexity)
        query_complexity_score = (
            statistics.mean(complexity_scores) if complexity_scores else 0
        )

        # Response relevance score (based on keyword coverage)
        total_keywords = sum(len(q.get("expected_keywords", [])) for q in queries)
        avg_keywords_per_query = total_keywords / len(queries) if queries else 0
        response_relevance_score = min(
            avg_keywords_per_query / 5, 1.0
        )  # Normalized to 5 keywords

        # Keyword coverage score
        unique_keywords = set()
        for query_data in queries:
            keywords = query_data.get("expected_keywords", [])
            unique_keywords.update(kw.lower() for kw in keywords)
        keyword_coverage_score = min(
            len(unique_keywords) / 20, 1.0
        )  # Normalized to 20 unique keywords

        # Language diversity score
        language_diversity_score = min(len(languages) / 4, 1.0)  # Up to 4 languages

        # Category coverage score
        expected_categories = [
            "discovery",
            "navigation",
            "registration",
            "networking",
            "technical",
            "strategic",
        ]
        category_coverage_score = len(
            categories.intersection(expected_categories)
        ) / len(expected_categories)

        # Overall quality score (weighted average)
        overall_quality_score = (
            query_complexity_score * 0.25
            + response_relevance_score * 0.25
            + keyword_coverage_score * 0.20
            + language_diversity_score * 0.15
            + category_coverage_score * 0.15
        )

        return TestQualityMetrics(
            query_complexity_score=query_complexity_score,
            response_relevance_score=response_relevance_score,
            keyword_coverage_score=keyword_coverage_score,
            language_diversity_score=language_diversity_score,
            category_coverage_score=category_coverage_score,
            overall_quality_score=overall_quality_score,
        )

    def _generate_recommendations(
        self,
        persona_name: str,
        total_queries: int,
        categories: set,
        complexity_counts: Dict,
        quality_metrics: TestQualityMetrics,
    ) -> List[str]:
        """Generate actionable recommendations for improving test quality."""
        recommendations = []

        # Check query quantity
        if total_queries < self.quality_thresholds["min_queries_per_persona"]:
            recommendations.append(
                f"Add more queries - only {total_queries} found, "
                f"recommend at least {self.quality_thresholds['min_queries_per_persona']}"
            )

        # Check category coverage
        if len(categories) < self.quality_thresholds["min_categories_per_persona"]:
            recommendations.append(
                f"Improve category diversity - only {len(categories)} categories covered, "
                f"recommend at least {self.quality_thresholds['min_categories_per_persona']}"
            )

        # Check complexity distribution
        if complexity_counts["high"] == 0:
            recommendations.append(
                "Add more complex, multi-step queries to test advanced functionality"
            )

        if complexity_counts["low"] > total_queries * 0.6:
            recommendations.append(
                "Reduce simple queries - too many low-complexity queries detected"
            )

        # Check specific quality metrics
        if (
            quality_metrics.keyword_coverage_score
            < self.quality_thresholds["min_keyword_coverage"]
        ):
            recommendations.append(
                "Improve keyword coverage - add more expected keywords to queries"
            )

        if quality_metrics.language_diversity_score < 0.5:
            recommendations.append(
                "Add multi-language queries to test internationalization features"
            )

        if (
            quality_metrics.overall_quality_score
            < self.quality_thresholds["min_overall_quality"]
        ):
            recommendations.append(
                f"Overall quality score ({quality_metrics.overall_quality_score:.2f}) "
                f"below threshold ({self.quality_thresholds['min_overall_quality']})"
            )

        # Persona-specific recommendations
        if persona_name == "web3-professional" and "strategic" not in categories:
            recommendations.append(
                "Add strategic business queries for Web3 professional persona"
            )

        if persona_name == "technical-builder" and "technical" not in categories:
            recommendations.append(
                "Add technical implementation queries for builder persona"
            )

        if not recommendations:
            recommendations.append(
                "Query suite meets quality standards - no improvements needed"
            )

        return recommendations

    def validate_all_personas(self) -> Dict[str, PersonaTestAnalysis]:
        """Validate all discovered personas."""
        personas = []
        if self.persona_dir.exists():
            for file in self.persona_dir.glob("*.md"):
                if file.name != "README.md":
                    personas.append(file.stem)

        results = {}
        for persona in sorted(personas):
            try:
                print(f"🔍 Validating {persona}...")
                analysis = self.validate_persona_queries(persona)
                results[persona] = analysis

                quality_score = analysis.quality_metrics.overall_quality_score
                if quality_score >= 0.8:
                    status = "✅ Excellent"
                elif quality_score >= 0.6:
                    status = "⚠️  Good"
                else:
                    status = "❌ Needs improvement"

                print(
                    f"   {status} - Quality: {quality_score:.2f}, Queries: {analysis.total_queries}"
                )

            except Exception as e:
                print(f"❌ Error validating {persona}: {e}")

        return results

    def monitor_test_performance(self, days_back: int = 7) -> Dict[str, any]:
        """Monitor test performance over time."""
        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Find recent test result files
        recent_results = []
        for result_file in self.results_dir.glob("*_results_*.json"):
            try:
                # Extract timestamp from filename
                timestamp_str = (
                    result_file.stem.split("_")[-2]
                    + "_"
                    + result_file.stem.split("_")[-1]
                )
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                if file_date >= cutoff_date:
                    with open(result_file) as f:
                        data = json.load(f)
                        data["file_date"] = file_date
                        recent_results.append(data)

            except Exception as e:
                print(f"Warning: Could not process {result_file}: {e}")

        # Analyze trends
        performance_analysis = {
            "monitoring_period": f"Last {days_back} days",
            "total_test_runs": len(recent_results),
            "personas_tested": len(
                set(r.get("persona", "unknown") for r in recent_results)
            ),
            "success_trends": {},
            "performance_issues": [],
            "recommendations": [],
        }

        # Group by persona and analyze trends
        persona_trends = {}
        for result in recent_results:
            persona = result.get("persona", "unknown")
            if persona not in persona_trends:
                persona_trends[persona] = []
            persona_trends[persona].append(result)

        for persona, runs in persona_trends.items():
            runs.sort(key=lambda x: x["file_date"])

            success_rates = []
            for run in runs:
                total_tests = len(run.get("results", []))
                passed_tests = sum(
                    1 for r in run.get("results", []) if r.get("status") == "passed"
                )
                success_rate = (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                )
                success_rates.append(success_rate)

            performance_analysis["success_trends"][persona] = {
                "runs": len(runs),
                "avg_success_rate": (
                    statistics.mean(success_rates) if success_rates else 0
                ),
                "trend": (
                    "improving"
                    if len(success_rates) > 1 and success_rates[-1] > success_rates[0]
                    else "stable"
                ),
            }

            # Identify issues
            if len(success_rates) > 0 and statistics.mean(success_rates) < 80:
                performance_analysis["performance_issues"].append(
                    f"{persona}: Low success rate ({statistics.mean(success_rates):.1f}%)"
                )

        return performance_analysis

    def generate_validation_report(
        self,
        validation_results: Dict[str, PersonaTestAnalysis],
        performance_analysis: Dict[str, any],
    ) -> str:
        """Generate comprehensive validation report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report_content = f"""# Persona Test Validation Report
Generated: {datetime.now().isoformat()}

## Executive Summary
- **Total Personas Validated:** {len(validation_results)}
- **Average Quality Score:** {statistics.mean([a.quality_metrics.overall_quality_score for a in validation_results.values()]):.2f}
- **Monitoring Period:** {performance_analysis.get('monitoring_period', 'N/A')}

## Quality Analysis by Persona

"""

        # Sort personas by quality score
        sorted_personas = sorted(
            validation_results.items(),
            key=lambda x: x[1].quality_metrics.overall_quality_score,
            reverse=True,
        )

        for persona_name, analysis in sorted_personas:
            quality = analysis.quality_metrics.overall_quality_score
            status = "🟢" if quality >= 0.8 else "🟡" if quality >= 0.6 else "🔴"

            report_content += f"""### {status} {persona_name.replace('-', ' ').title()}
**Quality Score:** {quality:.2f} | **Queries:** {analysis.total_queries} | **Categories:** {len(analysis.categories_covered)}

**Metrics:**
- Complexity: {analysis.quality_metrics.query_complexity_score:.2f}
- Relevance: {analysis.quality_metrics.response_relevance_score:.2f}
- Coverage: {analysis.quality_metrics.keyword_coverage_score:.2f}
- Languages: {len(analysis.languages_covered)} ({', '.join(analysis.languages_covered)})

**Complexity Distribution:** High: {analysis.complexity_distribution.get('high', 0)}, Medium: {analysis.complexity_distribution.get('medium', 0)}, Low: {analysis.complexity_distribution.get('low', 0)}

**Recommendations:**
"""
            for rec in analysis.recommendations:
                report_content += f"- {rec}\n"
            report_content += "\n"

        # Performance trends
        report_content += """## Performance Trends

"""
        success_trends = performance_analysis.get("success_trends", {})
        for persona, trend_data in success_trends.items():
            report_content += f"**{persona}:** {trend_data['avg_success_rate']:.1f}% success rate ({trend_data['trend']})\n"

        # Issues and overall recommendations
        issues = performance_analysis.get("performance_issues", [])
        if issues:
            report_content += "\n## Performance Issues\n"
            for issue in issues:
                report_content += f"- {issue}\n"

        report_content += """
## Overall Recommendations

### High Priority
- Focus on personas with quality scores below 0.75
- Address performance issues with success rates below 80%
- Improve category coverage for comprehensive testing

### Medium Priority
- Add more complex, multi-step queries for advanced scenarios
- Enhance keyword coverage for better response validation
- Increase language diversity for international user testing

### Monitoring
- Run validation weekly to track quality improvements
- Monitor test performance trends for regression detection
- Update validation thresholds as the system matures
"""

        # Save report
        report_file = self.validation_dir / f"validation_report_{timestamp}.md"
        with open(report_file, "w") as f:
            f.write(report_content)

        print(f"📊 Validation report saved: {report_file}")
        return report_content


def main():
    parser = argparse.ArgumentParser(description="Validate persona test quality")
    parser.add_argument(
        "--validate-all", action="store_true", help="Validate all personas"
    )
    parser.add_argument(
        "--monitor-quality", action="store_true", help="Monitor test performance"
    )
    parser.add_argument("--persona", help="Validate specific persona")
    parser.add_argument(
        "--days", type=int, default=7, help="Days to look back for monitoring"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate full validation report"
    )

    args = parser.parse_args()
    validator = PersonaTestValidator()

    validation_results = {}
    performance_analysis = {}

    if args.validate_all or args.report:
        print("🔍 Validating all personas...")
        validation_results = validator.validate_all_personas()

        # Print summary
        total_personas = len(validation_results)
        avg_quality = statistics.mean(
            [
                a.quality_metrics.overall_quality_score
                for a in validation_results.values()
            ]
        )
        print(
            f"\n📊 Validation Summary: {total_personas} personas, avg quality: {avg_quality:.2f}"
        )

    elif args.persona:
        print(f"🔍 Validating persona: {args.persona}")
        analysis = validator.validate_persona_queries(args.persona)
        validation_results[args.persona] = analysis

        print(f"Quality Score: {analysis.quality_metrics.overall_quality_score:.2f}")
        print(f"Queries: {analysis.total_queries}")
        print("Recommendations:")
        for rec in analysis.recommendations:
            print(f"  - {rec}")

    if args.monitor_quality or args.report:
        print(f"📈 Monitoring test performance (last {args.days} days)...")
        performance_analysis = validator.monitor_test_performance(args.days)

        print(f"Test runs: {performance_analysis['total_test_runs']}")
        print(f"Personas tested: {performance_analysis['personas_tested']}")

        if performance_analysis.get("performance_issues"):
            print("Issues found:")
            for issue in performance_analysis["performance_issues"]:
                print(f"  - {issue}")

    if args.report and (validation_results or performance_analysis):
        print("📄 Generating comprehensive validation report...")
        report = validator.generate_validation_report(
            validation_results, performance_analysis
        )


if __name__ == "__main__":
    main()
