"""
Fully dynamic tax case generator - all domain information from JSON templates.
Add new domains by editing tax_domains.json only!
"""
import os
from typing import List, Dict, Any, Optional

from core import TaxCase, TaxFact, classify_fact_type
from llm_client import GroqClient
from tax_domains import TaxDomainManager


class TaxGenerator:
    """
    Fully dynamic generator - all domain info comes from JSON templates.
    Add new domains by editing tax_domains.json only!
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize dynamic tax generator."""
        self.llm_client = GroqClient(api_key=api_key)
        self.domain_manager = TaxDomainManager()
        self.generated_scenarios = set()
        # Get all primary questions dynamically from templates
        self.domain_questions = self.domain_manager.get_domain_questions()
        print(f"✓ Dynamic generator initialized with {len(self.domain_questions)} domains from templates")
    
    def generate_case(self, scenario_type: str, context: str = "") -> TaxCase:
        """
        Generate a complete tax reasoning case using dynamic templates.
        All domain information comes from tax_domains.json!
        """
        # Check if domain exists in templates
        if scenario_type not in self.domain_manager.get_all_domains():
            available_domains = list(self.domain_manager.get_all_domains().keys())
            raise ValueError(f"Domain '{scenario_type}' not found in templates. Available: {available_domains}")
        
        # Check if already generated (in memory or on disk)
        case_file_path = f"data/generated/{scenario_type}/{scenario_type}.json"
        if scenario_type in self.generated_scenarios or os.path.exists(case_file_path):
            print(f"Case for {scenario_type} already exists, skipping duplicate generation")
            loaded_case = self._load_existing_case(scenario_type)
            if loaded_case is not None:
                self.generated_scenarios.add(scenario_type)
                return loaded_case
            else:
                print(f"Warning: Expected case file for {scenario_type} but could not load. Regenerating...")
        
        print(f"Generating {scenario_type} case using dynamic templates...")
        
        # Get domain context dynamically from templates
        domain_context = self.domain_manager.get_domain_context(scenario_type)
        
        # Generate all components using template information
        raw_facts = self.llm_client.generate_tax_facts(scenario_type, domain_context + "\n" + context)
        raw_narrative = self.llm_client.generate_tax_narrative(scenario_type, raw_facts[:3])
        
        # Get question dynamically from templates
        question = self._get_dynamic_question(scenario_type)

        # Generate answer dynamically using LLM based on facts, narrative, and question
        answer = self.llm_client.generate_dynamic_answer(scenario_type, raw_facts, raw_narrative, question)

        # Generate reasoning steps using template context
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

        # Save case
        case_path = case.save_to_file()
        self.generated_scenarios.add(scenario_type)

        print(f"✓ Case generated using dynamic template and saved to {case_path}")
        return case
    
    def _get_dynamic_question(self, scenario_type: str) -> str:
        """
        Get question dynamically from loaded templates.
        """
        if scenario_type in self.domain_questions:
            return self.domain_questions[scenario_type]
        else:
            # Fallback - should not happen if domain exists in templates
            return "What is the tax treatment?"
    
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
    
    def generate_all_domains(self) -> List[TaxCase]:
        """
        Generate cases for all domains found in templates.
        Completely dynamic - no hardcoded domain list!
        """
        # Get all domains dynamically from templates
        available_domains = list(self.domain_manager.get_all_domains().keys())
        
        print(f"Generating cases for all {len(available_domains)} domains from templates...")
        
        cases = []
        for domain in available_domains:
            case = self.generate_case(domain)
            if case:
                cases.append(case)
        
        return cases
    
    def reload_templates_and_regenerate(self):
        """
        Reload templates from JSON and update question mappings.
        Useful after manually editing tax_domains.json
        """
        print("Reloading templates and updating generator...")
        
        # Reload domains from JSON
        self.domain_manager.reload_domains()
        
        # Update question/answer mappings dynamically
        self.question_templates = self.domain_manager.get_domain_questions_answers()
        
        print(f"✓ Reloaded {len(self.question_templates)} domains from updated templates")
    
    def get_available_domains(self) -> List[str]:
        """Get list of all domains available in templates."""
        return list(self.domain_manager.get_all_domains().keys())
    
    def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """Get complete information about a domain from templates."""
        domain = self.domain_manager.get_domain(domain_name)
        question, answer = self._get_dynamic_question_answer(domain_name)
        
        return {
            "domain_name": domain.domain_name,
            "description": domain.description,
            "typical_questions": domain.typical_questions,
            "primary_question": question,
            "expected_answer": answer,
            "reasoning_pattern": domain.reasoning_pattern,
            "required_facts": domain.required_facts,
            "tax_rules": domain.tax_rules
        }
    
    def get_generated_scenarios(self) -> List[str]:
        """Get list of scenarios that have been generated."""
        return list(self.generated_scenarios)