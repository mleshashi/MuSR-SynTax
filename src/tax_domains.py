"""
Fully dynamic tax domain manager - all domains loaded from JSON template.
Add new domains by editing tax_domains.json only!
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import json
import os


@dataclass
class TaxDomainTemplate:
    """Template defining a specific tax reasoning domain."""
    domain_name: str
    description: str
    typical_questions: List[str]
    reasoning_pattern: List[str]
    required_facts: List[str]
    tax_rules: List[str]


class TaxDomainManager:
    """Fully dynamic domain manager - loads all domains from JSON template."""
    
    def __init__(self) -> None:
        """Initialize domain manager from JSON template file."""
        self.template_file = "data/templates/tax_domains.json"
        self.domains = {}
        
        # Load domains from JSON or create default template
        if os.path.exists(self.template_file):
            self._load_domains_from_json()
        else:
            self._create_default_template()
            self._load_domains_from_json()
    
    def _create_default_template(self):
        """Create the default JSON template with all 5 domains."""
        os.makedirs(os.path.dirname(self.template_file), exist_ok=True)
        
        # Complete template with all domain information
        default_template = {
            "metadata": {
                "description": "Tax domain templates for MuSR-SynTax case generation",
                "note": "All domains are defined here. Add new domains by adding to this JSON file.",
                "version": "1.0"
            },
            "domains": {
                "business_meal_deduction": {
                    "domain_name": "business_meal_deduction",
                    "description": "Business meal expenses and their deductibility under IRC Section 274",
                    "typical_questions": [
                        "How much of the meal expense is deductible?",
                        "What percentage of business meals can be deducted?",
                        "Is this meal expense qualifying for deduction?"
                    ],
                    "reasoning_pattern": [
                        "Identify the expense amount and business purpose",
                        "Verify the meal meets 'ordinary and necessary' criteria",
                        "Apply IRC Section 274 deduction percentage (50%)",
                        "Calculate the deductible amount"
                    ],
                    "required_facts": [
                        "expense_amount",
                        "business_purpose", 
                        "participants_present",
                        "meal_type_and_location"
                    ],
                    "tax_rules": [
                        "IRC Section 274 - Entertainment expenses",
                        "50% limitation on business meals",
                        "Ordinary and necessary business expense test"
                    ]
                },
                
                "home_office_deduction": {
                    "domain_name": "home_office_deduction",
                    "description": "Home office expenses for business use of home under IRC Section 280A",
                    "typical_questions": [
                        "What percentage of home expenses can be deducted?",
                        "Is the home office deduction allowed?",
                        "How much can be claimed for home office expenses?"
                    ],
                    "reasoning_pattern": [
                        "Verify exclusive business use of space",
                        "Calculate business percentage of home",
                        "Identify qualifying home expenses",
                        "Apply business percentage to expenses"
                    ],
                    "required_facts": [
                        "office_square_footage",
                        "total_home_square_footage",
                        "exclusive_business_use",
                        "qualifying_expenses"
                    ],
                    "tax_rules": [
                        "IRC Section 280A - Business use of home",
                        "Exclusive use test",
                        "Regular use test"
                    ]
                },
                
                "travel_expense_deduction": {
                    "domain_name": "travel_expense_deduction", 
                    "description": "Business travel expenses and their deductibility under IRC Section 162",
                    "typical_questions": [
                        "Which travel expenses are deductible?",
                        "Is this trip primarily for business?",
                        "How much travel expense can be deducted?"
                    ],
                    "reasoning_pattern": [
                        "Determine if travel is away from tax home",
                        "Verify business purpose of travel",
                        "Identify ordinary and necessary expenses",
                        "Calculate deductible amounts"
                    ],
                    "required_facts": [
                        "travel_destination",
                        "business_purpose",
                        "duration_of_trip",
                        "expense_breakdown"
                    ],
                    "tax_rules": [
                        "IRC Section 162 - Business expenses",
                        "Away from home test",
                        "Temporary vs. indefinite assignment rules"
                    ]
                },
                
                "charitable_donation_deduction": {
                    "domain_name": "charitable_donation_deduction",
                    "description": "Charitable contribution deductions under IRC Section 170", 
                    "typical_questions": [
                        "How much charitable deduction is allowed?",
                        "Is this organization qualified for deductions?",
                        "What are the donation limits?"
                    ],
                    "reasoning_pattern": [
                        "Verify qualified charitable organization",
                        "Determine contribution amount and type",
                        "Apply AGI limitation percentages",
                        "Calculate allowable deduction"
                    ],
                    "required_facts": [
                        "organization_status",
                        "donation_amount",
                        "donation_type",
                        "taxpayer_agi"
                    ],
                    "tax_rules": [
                        "IRC Section 170 - Charitable contributions",
                        "50% AGI limitation for cash donations",
                        "30% AGI limitation for capital gain property"
                    ]
                },
                
                "vehicle_expense_deduction": {
                    "domain_name": "vehicle_expense_deduction",
                    "description": "Business vehicle expense deductions under IRC Section 162",
                    "typical_questions": [
                        "What vehicle expenses are deductible?",
                        "Should I use standard mileage or actual expense method?"
                    ],
                    "reasoning_pattern": [
                        "Determine business vs. personal use percentage",
                        "Choose between standard mileage and actual expense method", 
                        "Calculate allowable business deduction",
                        "Apply record-keeping requirements"
                    ],
                    "required_facts": [
                        "total_miles_driven",
                        "business_miles", 
                        "vehicle_expenses",
                        "method_preference"
                    ],
                    "tax_rules": [
                        "IRC Section 162 - Business expenses",
                        "Standard mileage rate (IRS Notice)",
                        "Actual expense method rules"
                    ]
                }
            }
        }
        
        with open(self.template_file, 'w') as f:
            json.dump(default_template, f, indent=2)
        
        print(f"✓ Created complete template: {self.template_file}")
    
    def _load_domains_from_json(self):
        """Load all domains dynamically from JSON template."""
        try:
            with open(self.template_file, 'r') as f:
                template_data = json.load(f)
            
            self.domains = {}
            
            for domain_name, domain_data in template_data["domains"].items():
                domain = TaxDomainTemplate(
                    domain_name=domain_data["domain_name"],
                    description=domain_data["description"],
                    typical_questions=domain_data["typical_questions"],
                    reasoning_pattern=domain_data["reasoning_pattern"],
                    required_facts=domain_data["required_facts"],
                    tax_rules=domain_data["tax_rules"]
                )
                self.domains[domain_name] = domain
            
            print(f"✓ Loaded {len(self.domains)} domains from {self.template_file}")
            
        except Exception as e:
            print(f"Error loading template: {e}")
            self.domains = {}
    
    def reload_domains(self):
        """Reload domains from JSON (useful after manual edits)."""
        print("Reloading domains from template...")
        self._load_domains_from_json()
    
    def get_domain(self, domain_name: str) -> TaxDomainTemplate:
        """Get a specific tax domain template by name."""
        if domain_name not in self.domains:
            raise ValueError(f"Domain '{domain_name}' not found. Available: {list(self.domains.keys())}")
        return self.domains[domain_name]
    
    def get_all_domains(self) -> Dict[str, TaxDomainTemplate]:
        """Get all available tax domain templates."""
        return self.domains.copy()
    
    def get_domain_context(self, domain_name: str) -> str:
        """Get contextual information for LLM generation."""
        domain = self.get_domain(domain_name)
        
        context = f"""Domain: {domain.description}

Key reasoning steps:
{chr(10).join([f"- {step}" for step in domain.reasoning_pattern])}

Required facts to include:
{chr(10).join([f"- {fact}" for fact in domain.required_facts])}

Relevant tax rules:
{chr(10).join([f"- {rule}" for rule in domain.tax_rules])}
"""
        return context
    
    def get_domain_questions_answers(self) -> Dict[str, tuple[str, str]]:
        """
        Get question/answer mappings for all domains dynamically from JSON.
        
        Returns:
            Dictionary mapping domain names to (question, answer) tuples
        """
        qa_mappings = {}
        
        for domain_name, domain in self.domains.items():
            # Use first question as primary question
            question = domain.typical_questions[0] if domain.typical_questions else "What is the tax treatment?"
            
            # Generate context-appropriate answer based on domain rules from JSON
            answer = self._generate_domain_answer(domain)
            
            qa_mappings[domain_name] = (question, answer)
        
        return qa_mappings
    
    def _generate_domain_answer(self, domain: TaxDomainTemplate) -> str:
        """Generate appropriate answer based on domain characteristics from JSON."""
        domain_name = domain.domain_name
        
        # Pattern-based answer generation from domain rules in JSON
        if "50%" in str(domain.tax_rules) or "274" in str(domain.tax_rules):
            return "50% of the meal cost (subject to IRC Section 274)"
        elif "280A" in str(domain.tax_rules) or "home" in domain_name:
            return "Business use percentage of total home area"
        elif "162" in str(domain.tax_rules) and "travel" in domain_name:
            return "Ordinary and necessary business travel costs"
        elif "170" in str(domain.tax_rules) or "charitable" in domain_name:
            return "Up to AGI limits under IRC Section 170"
        elif "vehicle" in domain_name or "mileage" in str(domain.tax_rules):
            return "Business use percentage of total vehicle costs"
        else:
            # Fallback based on first tax rule from JSON
            first_rule = domain.tax_rules[0] if domain.tax_rules else "relevant tax rules"
            return f"Apply {first_rule.split(' - ')[0] if ' - ' in first_rule else first_rule}"