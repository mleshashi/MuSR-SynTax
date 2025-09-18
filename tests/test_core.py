import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import pytest
from src.core import TaxFact, TaxCase, classify_fact_type

def test_classify_fact_type_story():
    fact = "The taxpayer spent $500 on a business meal."
    assert classify_fact_type(fact) == "story"

def test_classify_fact_type_rule():
    fact = "Business meals are 50% deductible under IRC Section 274."
    assert classify_fact_type(fact) == "rule"

def test_classify_fact_type_conclusion():
    fact = "Therefore, the deduction allowed is $250."
    assert classify_fact_type(fact) == "conclusion"

def test_tax_fact_str():
    fact = TaxFact(content="Test content", fact_type="rule")
    assert str(fact) == "[rule] Test content"

def test_tax_case_init():
    facts = [TaxFact(content="A", fact_type="story"), TaxFact(content="B", fact_type="rule")]
    case = TaxCase(
        scenario_type="business_meal_deduction",
        narrative="A business meal was held.",
        facts=facts,
        question="How much is deductible?",
        correct_answer="$250",
        reasoning_steps=["Identify amount", "Apply 50% rule"]
    )
    assert case.scenario_type == "business_meal_deduction"
    assert case.narrative.startswith("A business meal")
    assert case.facts[0].fact_type == "story"
    assert case.correct_answer == "$250"
