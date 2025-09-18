"""
Fully dynamic tax case generator with validation and consistency checks.
All domain information from JSON templates.
"""
import os
import json
import yaml
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from core import TaxCase, TaxFact, classify_fact_type
from llm_client import GroqClient, MockGroqClient, get_client
from tax_domains import TaxDomainManager


class TaxGenerator:
    """
    Enhanced generator with validation and consistency checking.
    All domain info comes from JSON templates.
    """
    
    def __init__(self, api_key: Optional[str] = None, config_file: Optional[str] = None) -> None:
        """
        Initialize tax generator with configuration support.
        
        Args:
            api_key: Optional API key for LLM
            config_file: Optional path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Initialize LLM client
        self.llm_client = get_client(api_key)
        
        # Initialize domain manager
        template_file = self.config.get('paths', {}).get('domain_templates')
        self.domain_manager = TaxDomainManager(template_file)
        
        # Track generated scenarios
        self.generated_scenarios = set()
        
        # Get questions from templates
        self.domain_questions = self.domain_manager.get_domain_questions()
        
        # Statistics tracking
        self.stats = {
            "generated": 0,
            "validation_passed": 0,
            "validation_failed": 0,
            "regenerations": 0
        }
        
        print(f"✓ Generator initialized with {len(self.domain_questions)} domains")
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_file = config_file or "config/default_config.yaml"
        
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f)
                print(f"✓ Loaded configuration from {config_file}")
                return config
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        # Default configuration
        return {
            "generation": {
                "max_attempts": 3,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "validation": {
                "require_consistency": True,
                "min_facts": 4,
                "max_facts": 7
            },
            "paths": {
                "domain_templates": "data/templates/tax_domains.json",
                "generated_cases": "data/generated"
            }
        }
    
    def generate_case(self, scenario_type: str, force_regenerate: bool = False) -> Optional[TaxCase]:
        """
        Generate a complete tax case with validation.
        
        Args:
            scenario_type: Type of tax scenario to generate
            force_regenerate: Force regeneration even if exists
            
        Returns:
            Generated TaxCase or None if generation fails
        """
        # Check if domain exists
        if scenario_type not in self.domain_manager.get_all_domains():
            available = list(self.domain_manager.get_all_domains().keys())
            print(f"Error: Domain '{scenario_type}' not found. Available: {available}")
            return None
        
        # Check if already generated
        if not force_regenerate and scenario_type in self.generated_scenarios:
            print(f"Case for {scenario_type} already generated")
            return self._load_existing_case(scenario_type)
        
        print(f"\nGenerating {scenario_type} case...")
        
        # Get domain context
        domain_context = self.domain_manager.get_domain_context(scenario_type)
        
        max_attempts = self.config.get('generation', {}).get('max_attempts', 3)
        
        for attempt in range(max_attempts):
            try:
                # Generate with embedded answer for consistency
                fact_result = self.llm_client.generate_tax_facts_with_answer(
                    scenario_type, 
                    domain_context["context_string"]
                )
                
                raw_facts = fact_result["facts"]
                embedded_answer = fact_result.get("embedded_answer")
                
                # Validate fact count
                min_facts = self.config.get('validation', {}).get('min_facts', 4)
                if len(raw_facts) < min_facts:
                    print(f"  Attempt {attempt + 1}: Too few facts ({len(raw_facts)}), regenerating...")
                    continue
                
                # Generate narrative
                raw_narrative = self.llm_client.generate_tax_narrative(scenario_type, raw_facts[:3])
                
                # Get question from templates
                question = self.domain_questions.get(scenario_type, "What is the tax treatment?")
                
                # Generate or use embedded answer
                if embedded_answer and self.llm_client.validate_fact_consistency(raw_facts, embedded_answer):
                    answer = embedded_answer
                else:
                    answer = self.llm_client.generate_dynamic_answer(
                        scenario_type, raw_facts, raw_narrative, question
                    )
                
                # Validate consistency
                if not self.llm_client.validate_fact_consistency(raw_facts, answer):
                    print(f"  Attempt {attempt + 1}: Answer inconsistent with facts, regenerating...")
                    self.stats["regenerations"] += 1
                    continue
                
                # Generate reasoning steps
                reasoning_steps = self.llm_client.generate_reasoning_steps(
                    scenario_type, raw_facts, question, answer
                )
                
                # Create structured case
                case = TaxCase.from_llm_output(
                    scenario_type=scenario_type,
                    llm_facts=raw_facts,
                    narrative=raw_narrative,
                    question=question,
                    answer=answer,
                    reasoning_steps=reasoning_steps,
                    metadata={
                        "generation_timestamp": datetime.now().isoformat(),
                        "attempts": attempt + 1,
                        "model": getattr(self.llm_client, 'model', 'unknown')
                    }
                )
                
                # Validate the complete case
                errors = case.validate()
                if errors:
                    print(f"  Validation errors: {errors}")
                    if self.config.get('validation', {}).get('require_consistency', True):
                        self.stats["validation_failed"] += 1
                        continue
                else:
                    self.stats["validation_passed"] += 1
                
                # Save the case
                filepath = case.save_to_file()
                self.generated_scenarios.add(scenario_type)
                self.stats["generated"] += 1
                
                print(f"✓ Case generated and saved to {filepath}")
                return case
                
            except Exception as e:
                print(f"  Attempt {attempt + 1} failed: {e}")
                continue
        
        print(f"✗ Failed to generate valid case after {max_attempts} attempts")
        return None
    
    def _load_existing_case(self, scenario_type: str) -> Optional[TaxCase]:
        """Load an existing case from file."""
        base_dir = self.config.get('paths', {}).get('generated_cases', 'data/generated')
        filepath = os.path.join(base_dir, scenario_type, f"{scenario_type}.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                return TaxCase.from_dict(data)
            except Exception as e:
                print(f"Error loading case: {e}")
        
        return None
    
    def generate_all_domains(self, force_regenerate: bool = False) -> List[TaxCase]:
        """
        Generate cases for all domains in templates.
        
        Args:
            force_regenerate: Force regeneration of all cases
            
        Returns:
            List of generated TaxCase objects
        """
        available_domains = list(self.domain_manager.get_all_domains().keys())
        
        print(f"\nGenerating cases for {len(available_domains)} domains...")
        print("=" * 50)
        
        cases = []
        for i, domain in enumerate(available_domains, 1):
            print(f"\n[{i}/{len(available_domains)}] Processing {domain}")
            case = self.generate_case(domain, force_regenerate)
            if case:
                cases.append(case)
        
        # Print statistics
        self._print_statistics()
        
        return cases
    
    def validate_all_generated(self) -> Dict[str, List[str]]:
        """
        Validate all generated cases.
        
        Returns:
            Dictionary mapping scenario types to validation errors
        """
        base_dir = self.config.get('paths', {}).get('generated_cases', 'data/generated')
        validation_results = {}
        
        for scenario_dir in os.listdir(base_dir):
            scenario_path = os.path.join(base_dir, scenario_dir)
            if os.path.isdir(scenario_path):
                json_file = os.path.join(scenario_path, f"{scenario_dir}.json")
                if os.path.exists(json_file):
                    try:
                        case = self._load_existing_case(scenario_dir)
                        if case:
                            errors = case.validate()
                            if errors:
                                validation_results[scenario_dir] = errors
                    except Exception as e:
                        validation_results[scenario_dir] = [f"Load error: {e}"]
        
        return validation_results
    
    def regenerate_invalid_cases(self) -> List[TaxCase]:
        """Regenerate cases that fail validation."""
        validation_results = self.validate_all_generated()
        regenerated = []
        
        if validation_results:
            print(f"\nRegenerating {len(validation_results)} invalid cases...")
            for scenario_type in validation_results:
                print(f"  Regenerating {scenario_type}...")
                case = self.generate_case(scenario_type, force_regenerate=True)
                if case:
                    regenerated.append(case)
        
        return regenerated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            **self.stats,
            "domains_available": len(self.domain_manager.get_all_domains()),
            "domains_generated": len(self.generated_scenarios),
            "success_rate": (self.stats["validation_passed"] / 
                           max(1, self.stats["validation_passed"] + self.stats["validation_failed"])) * 100
        }
    
    def _print_statistics(self):
        """Print generation statistics."""
        stats = self.get_statistics()
        print("\n" + "=" * 50)
        print("GENERATION STATISTICS")
        print("=" * 50)
        print(f"Domains available:    {stats['domains_available']}")
        print(f"Cases generated:      {stats['domains_generated']}")
        print(f"Validation passed:    {stats['validation_passed']}")
        print(f"Validation failed:    {stats['validation_failed']}")
        print(f"Regenerations:        {stats['regenerations']}")
        print(f"Success rate:         {stats['success_rate']:.1f}%")
    
    def reload_templates(self):
        """Reload domain templates from JSON."""
        print("\nReloading domain templates...")
        self.domain_manager.reload_domains()
        self.domain_questions = self.domain_manager.get_domain_questions()
        print(f"✓ Reloaded {len(self.domain_questions)} domains")
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domains."""
        return list(self.domain_manager.get_all_domains().keys())
    
    def get_domain_info(self, domain_name: str) -> Dict[str, Any]:
        """Get complete information about a domain."""
        return self.domain_manager.get_domain_context(domain_name)