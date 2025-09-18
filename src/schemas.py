"""
Centralized data schemas for MuSR-SynTax.
Defines all core data structures for facts, cases, and domains.
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TaxFact:
    """A single fact in a tax reasoning case."""
    content: str
    fact_type: str  # "story", "rule", or "conclusion"

@dataclass
class TaxCase:
    """A complete generated tax reasoning case."""
    scenario_type: str
    narrative: str
    facts: List[TaxFact]
    question: str
    correct_answer: str
    reasoning_steps: List[str]

@dataclass
class TaxDomainTemplate:
    """Template defining a specific tax reasoning domain."""
    domain_name: str
    description: str
    typical_questions: List[str]
    reasoning_pattern: List[str]
    required_facts: List[str]
    tax_rules: List[str]
    answer_pattern: Optional[str] = None
    fact_templates: Optional[List[str]] = None
