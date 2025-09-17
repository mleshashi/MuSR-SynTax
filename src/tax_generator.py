"""
Tax case generator that integrates LLM client with core data structures.
This demonstrates the complete MuSR framework for tax law reasoning.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from core import TaxCase, TaxFact, classify_fact_type
from llm_client import GroqClient


class TaxGenerator:
    """
    Main generator class that creates complete tax reasoning cases.
    Implements MuSR framework: Template → Reasoning → Story Generation
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the tax generator with LLM client.
        
        Args:
            api_key: Optional Groq API key. If None, reads from GROQ_API_KEY env var
            
        Returns:
            None
        """
        self.llm_client = GroqClient(api_key=api_key)
        self.generation_history = []
    
    def generate_case(self, scenario_type: str, context: str = "", 
                     save_raw_llm_output: bool = True) -> TaxCase:
        """
        Generate a complete tax reasoning case using MuSR framework.
        
        Args:
            scenario_type: Type of tax scenario (e.g., "business_meal_deduction")
            context: Additional context for generation (default: "")
            save_raw_llm_output: Whether to save raw LLM outputs for debugging (default: True)
            
        Returns:
            Complete TaxCase object with structured facts, narrative, and reasoning
        """
        print(f"Generating {scenario_type} case...")
        
        # Step 1: Generate facts using LLM
        raw_facts = self.llm_client.generate_tax_facts(scenario_type, context)
        
        # Step 2: Generate narrative using LLM
        raw_narrative = self.llm_client.generate_tax_narrative(scenario_type, raw_facts[:3])
        
        # Step 3: Generate question and answer
        question, answer = self._generate_question_answer(scenario_type, raw_facts)
        
        # Step 4: Generate reasoning steps
        reasoning_steps = self.llm_client.generate_reasoning_steps(
            scenario_type, raw_facts, question, answer
        )
        
        # Step 5: Structure into TaxCase
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
        
        # Step 6: Save everything
        case_path = case.save_to_file()
        
        if save_raw_llm_output:
            self._save_raw_output(scenario_type, {
                'raw_facts': raw_facts,
                'raw_narrative': raw_narrative,
                'question': question,
                'answer': answer,
                'reasoning_steps': reasoning_steps
            })
        
        # Track generation
        self.generation_history.append({
            'timestamp': datetime.now().isoformat(),
            'scenario_type': scenario_type,
            'case_path': case_path,
            'context': context
        })
        
        print(f"✓ Case generated and saved to {case_path}")
        return case
    
    def generate_multiple_cases(self, scenario_types: List[str], 
                              count_per_type: int = 2) -> List[TaxCase]:
        """
        Generate multiple cases across different tax domains to demonstrate extensibility.
        
        Args:
            scenario_types: List of tax scenario types to generate cases for
            count_per_type: Number of cases to generate per scenario type (default: 2)
            
        Returns:
            List of generated TaxCase objects across all specified domains
        """
        cases = []
        for scenario_type in scenario_types:
            for i in range(count_per_type):
                context = f"Variation {i+1}"
                case = self.generate_case(scenario_type, context)
                cases.append(case)
        
        return cases
    
    def _generate_question_answer(self, scenario_type: str, facts: List[str]) -> tuple[str, str]:
        """
        Generate appropriate question and answer pair for the scenario.
        
        Args:
            scenario_type: Type of tax scenario (e.g., "business_meal_deduction")
            facts: List of facts (currently unused but available for future enhancements)
            
        Returns:
            Tuple of (question, answer) strings appropriate for the scenario type
        """
        
        # Improved mapping with realistic answers
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
        
        template = question_templates.get(scenario_type, 
                                        ('What is the tax treatment?', 'Apply relevant tax rules'))
        
        return template[0], template[1]
    
    def _save_raw_output(self, scenario_type: str, raw_data: Dict[str, Any]) -> None:
        """
        Save raw LLM outputs for debugging and system improvement.
        
        Args:
            scenario_type: Type of tax scenario for filename organization
            raw_data: Dictionary containing all raw LLM outputs (facts, narrative, etc.)
            
        Returns:
            None - saves data to timestamped JSON file in llm_raw directory
        """
        raw_dir = "data/generated/llm_raw"
        os.makedirs(raw_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario_type}_raw_{timestamp}.json"
        filepath = os.path.join(raw_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(raw_data, f, indent=2)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about generated cases.
        
        Returns:
            Dictionary containing total cases, scenario breakdown, and latest generation timestamp
        """
        if not self.generation_history:
            return {"total_cases": 0}
        
        scenario_counts = {}
        for entry in self.generation_history:
            scenario_type = entry['scenario_type']
            scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1
        
        return {
            'total_cases': len(self.generation_history),
            'scenario_breakdown': scenario_counts,
            'latest_generation': self.generation_history[-1]['timestamp']
        }


# Example usage for testing
if __name__ == "__main__":
    try:
        # Initialize generator
        generator = TaxGenerator()
        
        # Test 1: Single case generation
        print("=== Single Case Generation ===")
        case = generator.generate_case("business_meal_deduction", "Sales manager client meeting")
        case.display()
        
        # Test 2: Multiple case generation (shows extensibility)
        print("\n=== Multiple Case Generation ===")
        scenarios = ["business_meal_deduction", "home_office_deduction"]
        cases = generator.generate_multiple_cases(scenarios, count_per_type=1)
        
        print(f"Generated {len(cases)} cases across different domains")
        
        # Test 3: Show statistics
        print("\n=== Generation Statistics ===")
        stats = generator.get_generation_stats()
        print(json.dumps(stats, indent=2))
        
        print("\n✓ TaxGenerator working correctly!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure GROQ_API_KEY is set in your .env file")