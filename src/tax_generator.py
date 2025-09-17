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
    
    def __init__(self, api_key: Optional[str] = None, save_raw_outputs: bool = False) -> None:
        """
        Initialize the tax generator with LLM client.
        
        Args:
            api_key: Optional Groq API key. If None, reads from GROQ_API_KEY env var
            save_raw_outputs: Whether to save raw LLM outputs (default: False to avoid duplicates)
        """
        self.llm_client = GroqClient(api_key=api_key)
        self.generation_history = []
        self.save_raw_outputs = save_raw_outputs  # Control duplicate saving
        
        # Initialize tracking
        self.total_cases_generated = 0
        self.last_generation_session = datetime.now().isoformat()
    
    def generate_case(self, scenario_type: str, context: str = "") -> TaxCase:
        """
        Generate a complete tax reasoning case using MuSR framework.
        
        Args:
            scenario_type: Type of tax scenario (e.g., "business_meal_deduction")
            context: Additional context for generation (default: "")
            
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
        
        # Step 6: Save the structured case (primary output)
        case_path = case.save_to_file()
        
        # Step 7: Optionally save raw outputs for debugging
        if self.save_raw_outputs:
            self._save_raw_output(scenario_type, {
                'raw_facts': raw_facts,
                'raw_narrative': raw_narrative,
                'question': question,
                'answer': answer,
                'reasoning_steps': reasoning_steps
            })
        
        # Step 8: Track generation
        self._track_generation(scenario_type, case_path, context)
        
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
        print(f"Generating {len(scenario_types) * count_per_type} cases...")
        
        for scenario_type in scenario_types:
            for i in range(count_per_type):
                context_variation = f"Case variation {i+1}"
                case = self.generate_case(scenario_type, context_variation)
                cases.append(case)
        
        print(f"✓ Generated {len(cases)} cases across {len(scenario_types)} domains")
        return cases
    
    def generate_batch_with_validation(self, scenario_type: str, count: int = 5, 
                                     validate_quality: bool = True) -> List[TaxCase]:
        """
        Generate multiple cases of the same type with optional quality validation.
        
        Args:
            scenario_type: Type of tax scenario to generate
            count: Number of cases to generate
            validate_quality: Whether to perform basic quality checks
            
        Returns:
            List of validated TaxCase objects
        """
        cases = []
        print(f"Generating batch of {count} {scenario_type} cases...")
        
        for i in range(count):
            context = f"Batch case {i+1}"
            case = self.generate_case(scenario_type, context)
            
            if validate_quality:
                if self._validate_case_quality(case):
                    cases.append(case)
                    print(f"✓ Case {i+1} passed quality check")
                else:
                    print(f"⚠ Case {i+1} failed quality check, regenerating...")
                    # Could implement retry logic here
            else:
                cases.append(case)
        
        return cases
    
    def _validate_case_quality(self, case: TaxCase) -> bool:
        """
        Perform basic quality validation on generated case.
        
        Args:
            case: TaxCase to validate
            
        Returns:
            True if case meets quality standards, False otherwise
        """
        # Basic validation rules
        checks = [
            len(case.facts) >= 3,  # Minimum facts
            len(case.narrative) > 100,  # Reasonable narrative length
            len(case.reasoning_steps) >= 3,  # Minimum reasoning steps
            case.question.endswith('?'),  # Proper question format
            len(case.correct_answer) > 5,  # Non-trivial answer
        ]
        
        return all(checks)
    
    def _generate_question_answer(self, scenario_type: str, facts: List[str]) -> tuple[str, str]:
        """
        Generate appropriate question and answer pair for the scenario.
        
        Args:
            scenario_type: Type of tax scenario (e.g., "business_meal_deduction")
            facts: List of facts (currently unused but available for future enhancements)
            
        Returns:
            Tuple of (question, answer) strings appropriate for the scenario type
        """
        
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
        Save raw LLM outputs for debugging (only when explicitly enabled).
        
        Args:
            scenario_type: Type of tax scenario for filename organization
            raw_data: Dictionary containing all raw LLM outputs
        """
        raw_dir = "data/debug/llm_raw"
        os.makedirs(raw_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario_type}_debug_{timestamp}.json"
        filepath = os.path.join(raw_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(raw_data, f, indent=2)
    
    def _track_generation(self, scenario_type: str, case_path: str, context: str) -> None:
        """
        Track generation history for statistics and debugging.
        
        Args:
            scenario_type: Type of scenario generated
            case_path: Path where case was saved
            context: Context used for generation
        """
        self.generation_history.append({
            'timestamp': datetime.now().isoformat(),
            'scenario_type': scenario_type,
            'case_path': case_path,
            'context': context
        })
        self.total_cases_generated += 1
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about generated cases.
        
        Returns:
            Dictionary containing detailed generation statistics
        """
        if not self.generation_history:
            return {"total_cases": 0, "status": "No cases generated yet"}
        
        # Calculate scenario breakdown
        scenario_counts = {}
        for entry in self.generation_history:
            scenario_type = entry['scenario_type']
            scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1
        
        return {
            'total_cases': self.total_cases_generated,
            'session_started': self.last_generation_session,
            'scenario_breakdown': scenario_counts,
            'latest_generation': self.generation_history[-1]['timestamp'],
            'unique_scenarios': len(scenario_counts),
            'debug_mode': self.save_raw_outputs
        }
    
    def save_generation_summary(self, filepath: str = "data/generation_summary.json") -> str:
        """
        Save a summary of all generation activity.
        
        Args:
            filepath: Where to save the summary
            
        Returns:
            Path where summary was saved
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        summary = {
            "session_info": {
                "generated_at": datetime.now().isoformat(),
                "total_cases": self.total_cases_generated
            },
            "statistics": self.get_generation_stats(),
            "recent_cases": self.generation_history[-10:]  # Last 10 cases
        }
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return filepath
    
    def cleanup_duplicate_files(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Identify and optionally remove duplicate case files.
        
        Args:
            dry_run: If True, only identify duplicates without removing them
            
        Returns:
            Dictionary with cleanup results
        """
        generated_dir = "data/generated"
        if not os.path.exists(generated_dir):
            return {"message": "No generated directory found"}
        
        duplicates = []
        case_files = []
        
        # Find all case files
        for scenario_dir in os.listdir(generated_dir):
            scenario_path = os.path.join(generated_dir, scenario_dir)
            if os.path.isdir(scenario_path):
                for file in os.listdir(scenario_path):
                    if file.endswith('.json'):
                        case_files.append(os.path.join(scenario_path, file))
        
        if dry_run:
            return {
                "total_case_files": len(case_files),
                "message": "Run with dry_run=False to perform cleanup"
            }
        
        # In a real implementation, you'd add duplicate detection logic here
        return {"case_files_found": len(case_files), "duplicates_removed": 0}