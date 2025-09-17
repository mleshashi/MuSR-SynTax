"""
Tax case generator that integrates LLM client with core data structures.

"""
import os
from typing import List, Dict, Any, Optional

from core import TaxCase, TaxFact, classify_fact_type
from llm_client import GroqClient


class TaxGenerator:
    """
    Main generator class that creates complete tax reasoning cases.
    Implements MuSR framework: Template → Reasoning → Story Generation
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the tax generator with LLM client."""
        self.llm_client = GroqClient(api_key=api_key)
        self.generated_scenarios = set()  # Track generated scenarios to prevent duplicates
    
    def generate_case(self, scenario_type: str, context: str = "") -> TaxCase:
        """
        Generate a complete tax reasoning case using MuSR framework.
        Only generates if not already generated to prevent duplicates.
        """
        # Check if already generated
        if scenario_type in self.generated_scenarios:
            print(f"Case for {scenario_type} already exists, skipping duplicate generation")
            return self._load_existing_case(scenario_type)
        
        print(f"Generating {scenario_type} case...")
        
        # Generate all components
        raw_facts = self.llm_client.generate_tax_facts(scenario_type, context)
        raw_narrative = self.llm_client.generate_tax_narrative(scenario_type, raw_facts[:3])
        question, answer = self._generate_question_answer(scenario_type)
        reasoning_steps = self.llm_client.generate_reasoning_steps(
            scenario_type, raw_facts, question, answer
        )
        
        # Create structured case
        structured_facts = []
        for fact_text in raw_facts:
            fact_type = classify_fact_type(fact_text)
            structured_facts.append(TaxFact(content=fact_text, fact_type=fact_type))
        
        case = TaxCase(
            scenario_type=scenario_type,
            narrative=raw_narrative,
            facts=structured_facts,
            question=question,
            correct_answer=answer,
            reasoning_steps=reasoning_steps
        )
        
        # Save case (overwrites any existing file)
        case_path = case.save_to_file()
        self.generated_scenarios.add(scenario_type)
        
        print(f"✓ Case generated and saved to {case_path}")
        return case
    
    def _load_existing_case(self, scenario_type: str) -> Optional[TaxCase]:
        """Load existing case if it exists."""
        filepath = f"data/generated/{scenario_type}/{scenario_type}.json"
        
        if os.path.exists(filepath):
            try:
                import json
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct TaxCase from saved data
                facts = [TaxFact(content=f["content"], fact_type=f["type"]) for f in data["facts"]]
                
                return TaxCase(
                    scenario_type=data["scenario_type"],
                    narrative=data["narrative"],
                    facts=facts,
                    question=data["question"],
                    correct_answer=data["correct_answer"],
                    reasoning_steps=data["reasoning_steps"]
                )
            except Exception as e:
                print(f"Error loading existing case: {e}")
        
        return None
    
    def generate_all_domains(self, domain_list: List[str]) -> List[TaxCase]:
        """
        Generate cases for all specified domains (one per domain).
        """
        cases = []
        for domain in domain_list:
            case = self.generate_case(domain)
            if case:
                cases.append(case)
        
        return cases
    
    def _generate_question_answer(self, scenario_type: str) -> tuple[str, str]:
        """Generate appropriate question and answer pair for the scenario."""
        
        question_templates = {
            'business_meal_deduction': (
                'How much of the meal expense is deductible?', 
                '50% of the meal cost (subject to IRC Section 274)'
            ),
            'home_office_deduction': (
                'What percentage of home expenses can be deducted?', 
                'Business use percentage of total home area'
            ),
            'travel_expense_deduction': (
                'Which travel expenses are deductible?', 
                'Ordinary and necessary business travel costs'
            ),
            'charitable_donation_deduction': (
                'How much charitable deduction is allowed?', 
                'Up to AGI limits under IRC Section 170'
            ),
            'vehicle_expense_deduction': (
                'What vehicle expenses are deductible?',
                'Business use percentage of total vehicle costs'
            )
        }
        
        return question_templates.get(scenario_type, 
                                    ('What is the tax treatment?', 'Apply relevant tax rules'))
    
    def get_generated_scenarios(self) -> List[str]:
        """Get list of scenarios that have been generated."""
        return list(self.generated_scenarios)