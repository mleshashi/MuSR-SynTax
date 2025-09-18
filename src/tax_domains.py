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
        
        # Updated template to match the latest tax_domains.json
        default_template = {
            "metadata": {
                "description": "Tax domain templates for MuSR-SynTax case generation with concrete amounts",
                "note": "All domains include specific numerical facts for better reasoning quality",
                "version": "2.0"
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
                        "Identify the specific expense amount and business purpose",
                        "Verify the meal meets 'ordinary and necessary' criteria",
                        "Apply IRC Section 274 deduction percentage (50%)",
                        "Calculate the exact deductible amount in dollars"
                    ],
                    "required_facts": [
                        "meal_expense_amount ($50-$500 range)",
                        "number_of_attendees (2-12 people)",
                        "business_purpose_description",
                        "meeting_location_type (restaurant, office, hotel)",
                        "client_vs_employee_ratio"
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
                        "What is the dollar amount of the home office deduction?"
                    ],
                    "reasoning_pattern": [
                        "Verify exclusive business use of designated space",
                        "Calculate business percentage: office sq ft \u00f7 total home sq ft",
                        "Identify total qualifying home expenses for the year",
                        "Apply business percentage to get deductible amount"
                    ],
                    "required_facts": [
                        "home_office_square_footage (100-400 sq ft)",
                        "total_home_square_footage (1000-3000 sq ft)",
                        "annual_home_expenses ($12000-$30000)",
                        "exclusive_business_use_confirmation (yes/no)",
                        "months_of_business_use (1-12 months)"
                    ],
                    "tax_rules": [
                        "IRC Section 280A - Business use of home",
                        "Exclusive use test",
                        "Regular use test",
                        "Simplified method: $5 per sq ft up to 300 sq ft"
                    ]
                },
                "travel_expense_deduction": {
                    "domain_name": "travel_expense_deduction",
                    "description": "Business travel expenses and their deductibility under IRC Section 162",
                    "typical_questions": [
                        "Which travel expenses are deductible?",
                        "What is the total deductible travel amount?"
                    ],
                    "reasoning_pattern": [
                        "Determine if travel is away from tax home overnight",
                        "Verify primary business purpose of the trip",
                        "Identify ordinary and necessary expense categories",
                        "Calculate total deductible amount by category"
                    ],
                    "required_facts": [
                        "trip_duration_days (1-7 days)",
                        "total_airfare_cost ($200-$1500)",
                        "hotel_cost_per_night ($80-$300)",
                        "meals_per_day_cost ($30-$100)",
                        "business_days_vs_personal_days",
                        "conference_registration_fee ($0-$800)"
                    ],
                    "tax_rules": [
                        "IRC Section 162 - Business expenses",
                        "Away from home test (overnight rule)",
                        "50% limitation on meal expenses during travel"
                    ]
                },
                "charitable_donation_deduction": {
                    "domain_name": "charitable_donation_deduction",
                    "description": "Charitable contribution deductions under IRC Section 170",
                    "typical_questions": [
                        "How much charitable deduction is allowed?",
                        "What are the AGI limitations for this donation?"
                    ],
                    "reasoning_pattern": [
                        "Verify organization is qualified 501(c)(3) charity",
                        "Determine contribution type (cash vs property)",
                        "Calculate AGI limitation (50% for cash, 30% for property)",
                        "Apply limitation to determine deductible amount"
                    ],
                    "required_facts": [
                        "donation_amount ($500-$10000)",
                        "taxpayer_agi ($30000-$150000)",
                        "donation_type (cash, property, appreciated_stock)",
                        "charity_qualification_status (501c3, private_foundation)",
                        "property_fair_market_value ($1000-$5000 if applicable)"
                    ],
                    "tax_rules": [
                        "IRC Section 170 - Charitable contributions",
                        "50% AGI limitation for cash donations to public charities",
                        "30% AGI limitation for capital gain property",
                        "5-year carryforward for excess contributions"
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
                        "Calculate business use percentage from mileage log",
                        "Compare standard mileage vs actual expense methods",
                        "Choose method that provides larger deduction",
                        "Calculate final deductible amount"
                    ],
                    "required_facts": [
                        "total_miles_driven_year (10000-30000 miles)",
                        "business_miles_driven (3000-20000 miles)",
                        "actual_vehicle_expenses ($3000-$8000)",
                        "standard_mileage_rate_cents (65.5 cents for 2023)",
                        "vehicle_purchase_price ($15000-$40000)",
                        "depreciation_method (if actual expense)"
                    ],
                    "tax_rules": [
                        "IRC Section 162 - Business expenses",
                        "Standard mileage rate (IRS Notice 2023-03)",
                        "Actual expense method with depreciation limits",
                        "Business use percentage requirement"
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
    
    def get_domain_questions(self) -> Dict[str, str]:
        """
        Get primary question for all domains dynamically from JSON.
        Returns:
            Dictionary mapping domain names to primary question string
        """
        questions = {}
        for domain_name, domain in self.domains.items():
            question = domain.typical_questions[0] if domain.typical_questions else "What is the tax treatment?"
            questions[domain_name] = question
        return questions