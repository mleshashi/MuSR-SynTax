"""
Fully dynamic tax domain manager - all domains loaded from JSON template.
Add new domains by editing tax_domains.json only!
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
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
    answer_pattern: Optional[str] = None
    fact_templates: Optional[List[str]] = None


class TaxDomainManager:
    """Fully dynamic domain manager - loads all domains from JSON template."""
    
    def __init__(self, template_file: Optional[str] = None) -> None:
        """
        Initialize domain manager from JSON template file.
        
        Args:
            template_file: Path to template file (default: data/templates/tax_domains.json)
        """
        self.template_file = template_file or "data/templates/tax_domains.json"
        self.domains = {}
        self.metadata = {}
        
        # Load domains from JSON or create default template
        if os.path.exists(self.template_file):
            self._load_domains_from_json()
        else:
            self._create_default_template()
            self._load_domains_from_json()
    
    def _create_default_template(self):
        """Create the enhanced default JSON template."""
        os.makedirs(os.path.dirname(self.template_file), exist_ok=True)
        
        default_template = {
            "metadata": {
                "description": "Tax domain templates for MuSR-SynTax case generation",
                "version": "3.0",
                "note": "Templates include answer patterns for self-consistent generation"
            },
            "domains": {
                "business_meal_deduction": {
                    "domain_name": "business_meal_deduction",
                    "description": "Business meal expenses and their deductibility under IRC Section 274",
                    "typical_questions": [
                        "How much of the meal expense is deductible?",
                        "What is the deductible amount?",
                        "Calculate the business meal deduction."
                    ],
                    "answer_pattern": "[meal_amount] × [deduction_percentage]",
                    "fact_templates": [
                        "Company/person spent [amount] on [meal type]",
                        "Business meals are [percentage]% deductible",
                        "The deductible amount is [calculated_amount]"
                    ],
                    "reasoning_pattern": [
                        "Identify the meal expense amount",
                        "Verify business purpose",
                        "Apply deduction percentage",
                        "Calculate deductible amount"
                    ],
                    "required_facts": [
                        "meal_expense_amount",
                        "business_purpose",
                        "deduction_percentage",
                        "calculated_deduction"
                    ],
                    "tax_rules": [
                        "IRC Section 274 - 50% limitation",
                        "Ordinary and necessary test"
                    ]
                },
                "home_office_deduction": {
                    "domain_name": "home_office_deduction",
                    "description": "Home office expenses for business use of home",
                    "typical_questions": [
                        "What percentage of home expenses can be deducted?",
                        "What is the home office deduction amount?"
                    ],
                    "answer_pattern": "[office_sq_ft] ÷ [total_sq_ft] × 100%",
                    "fact_templates": [
                        "Home office is [office_sq_ft] square feet",
                        "Total home is [total_sq_ft] square feet",
                        "Business use percentage is [calculated_percentage]%"
                    ],
                    "reasoning_pattern": [
                        "Verify exclusive business use",
                        "Calculate business percentage",
                        "Apply to home expenses"
                    ],
                    "required_facts": [
                        "office_square_footage",
                        "total_home_square_footage",
                        "business_use_percentage"
                    ],
                    "tax_rules": [
                        "IRC Section 280A",
                        "Exclusive use test",
                        "Simplified method: $5/sq ft"
                    ]
                },
                "travel_expense_deduction": {
                    "domain_name": "travel_expense_deduction",
                    "description": "Business travel expenses and deductibility",
                    "typical_questions": [
                        "What is the total deductible travel expense?",
                        "Which expenses are deductible?"
                    ],
                    "answer_pattern": "Sum of qualifying expenses",
                    "fact_templates": [
                        "Trip lasted [days] for business",
                        "Hotel costs were [amount]",
                        "Meals during travel totaled [amount]",
                        "Total deductible is [calculated_amount]"
                    ],
                    "reasoning_pattern": [
                        "Verify business purpose",
                        "Check overnight rule",
                        "Sum qualifying expenses"
                    ],
                    "required_facts": [
                        "trip_duration",
                        "lodging_costs",
                        "meal_costs",
                        "total_deductible"
                    ],
                    "tax_rules": [
                        "IRC Section 162",
                        "Away from home test",
                        "50% meal limitation"
                    ]
                },
                "charitable_donation_deduction": {
                    "domain_name": "charitable_donation_deduction",
                    "description": "Charitable contribution deductions",
                    "typical_questions": [
                        "How much charitable deduction is allowed?",
                        "What is the deductible donation amount?"
                    ],
                    "answer_pattern": "Min([donation], [AGI_limit])",
                    "fact_templates": [
                        "Taxpayer donated [amount] to charity",
                        "AGI is [agi_amount]",
                        "AGI limit allows [limit_amount]",
                        "Deductible amount is [calculated_deduction]"
                    ],
                    "reasoning_pattern": [
                        "Verify 501(c)(3) status",
                        "Calculate AGI limitation",
                        "Apply limitation"
                    ],
                    "required_facts": [
                        "donation_amount",
                        "taxpayer_agi",
                        "agi_limitation",
                        "deductible_amount"
                    ],
                    "tax_rules": [
                        "IRC Section 170",
                        "60% AGI limit for cash",
                        "30% AGI limit for property"
                    ]
                },
                "vehicle_expense_deduction": {
                    "domain_name": "vehicle_expense_deduction",
                    "description": "Business vehicle expense deductions",
                    "typical_questions": [
                        "What vehicle expenses are deductible?",
                        "Calculate the vehicle deduction."
                    ],
                    "answer_pattern": "[business_miles] × [mileage_rate]",
                    "fact_templates": [
                        "Vehicle driven [total_miles] miles total",
                        "Business use was [business_percentage]%",
                        "Standard mileage rate is [rate]",
                        "Deduction is [calculated_amount]"
                    ],
                    "reasoning_pattern": [
                        "Calculate business miles",
                        "Apply standard mileage rate",
                        "Or calculate actual expenses"
                    ],
                    "required_facts": [
                        "total_miles",
                        "business_percentage",
                        "mileage_rate",
                        "deduction_amount"
                    ],
                    "tax_rules": [
                        "IRC Section 162",
                        "2023 rate: 65.5 cents/mile",
                        "Actual expense method"
                    ]
                },
                "equipment_depreciation": {
                    "domain_name": "equipment_depreciation",
                    "description": "Business equipment depreciation",
                    "typical_questions": [
                        "What is the annual depreciation deduction?",
                        "Calculate first-year depreciation."
                    ],
                    "answer_pattern": "[cost] × [depreciation_rate] × [business_use_%]",
                    "fact_templates": [
                        "Equipment cost [amount]",
                        "Asset is [year]-year property",
                        "Business use is [percentage]%",
                        "First year depreciation is [calculated_amount]"
                    ],
                    "reasoning_pattern": [
                        "Determine MACRS class",
                        "Apply depreciation rate",
                        "Adjust for business use"
                    ],
                    "required_facts": [
                        "equipment_cost",
                        "depreciation_class",
                        "business_use_percentage",
                        "depreciation_amount"
                    ],
                    "tax_rules": [
                        "IRC Section 168 - MACRS",
                        "Section 179 election",
                        "Bonus depreciation"
                    ]
                }
            }
        }
        
        with open(self.template_file, 'w') as f:
            json.dump(default_template, f, indent=2)
        
        print(f"✓ Created enhanced template: {self.template_file}")
    
    def _load_domains_from_json(self):
        """Load all domains dynamically from JSON template."""
        try:
            with open(self.template_file, 'r') as f:
                template_data = json.load(f)
            
            self.metadata = template_data.get("metadata", {})
            self.domains = {}
            
            for domain_name, domain_data in template_data.get("domains", {}).items():
                domain = TaxDomainTemplate(
                    domain_name=domain_data.get("domain_name", domain_name),
                    description=domain_data.get("description", ""),
                    typical_questions=domain_data.get("typical_questions", []),
                    reasoning_pattern=domain_data.get("reasoning_pattern", []),
                    required_facts=domain_data.get("required_facts", []),
                    tax_rules=domain_data.get("tax_rules", []),
                    answer_pattern=domain_data.get("answer_pattern"),
                    fact_templates=domain_data.get("fact_templates", [])
                )
                self.domains[domain_name] = domain
            
            print(f"✓ Loaded {len(self.domains)} domains from {self.template_file}")
            
        except Exception as e:
            print(f"Error loading template: {e}")
            self.domains = {}
            self.metadata = {}
    
    def reload_domains(self):
        """Reload domains from JSON (useful after manual edits)."""
        print("Reloading domains from template...")
        self._load_domains_from_json()
    
    def get_domain(self, domain_name: str) -> TaxDomainTemplate:
        """Get a specific tax domain template by name."""
        if domain_name not in self.domains:
            available = list(self.domains.keys())
            raise ValueError(f"Domain '{domain_name}' not found. Available: {available}")
        return self.domains[domain_name]
    
    def get_all_domains(self) -> Dict[str, TaxDomainTemplate]:
        """Get all available tax domain templates."""
        return self.domains.copy()
    
    def get_domain_context(self, domain_name: str) -> Dict[str, Any]:
        """Get complete context for LLM generation."""
        domain = self.get_domain(domain_name)
        
        context = {
            "description": domain.description,
            "reasoning_pattern": domain.reasoning_pattern,
            "required_facts": domain.required_facts,
            "tax_rules": domain.tax_rules,
            "answer_pattern": domain.answer_pattern,
            "fact_templates": domain.fact_templates or [],
            "questions": domain.typical_questions
        }
        
        # Convert to string for prompts
        context_str = f"""Domain: {domain.description}

Answer Pattern: {domain.answer_pattern or 'Calculate based on facts'}

Fact Templates:
{chr(10).join([f"- {tmpl}" for tmpl in (domain.fact_templates or [])])}

Required Facts:
{chr(10).join([f"- {fact}" for fact in domain.required_facts])}

Tax Rules:
{chr(10).join([f"- {rule}" for rule in domain.tax_rules])}

Reasoning Steps:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(domain.reasoning_pattern)])}"""
        
        context["context_string"] = context_str
        return context
    
    def get_domain_questions(self) -> Dict[str, str]:
        """Get primary question for all domains."""
        questions = {}
        for domain_name, domain in self.domains.items():
            question = domain.typical_questions[0] if domain.typical_questions else "What is the tax treatment?"
            questions[domain_name] = question
        return questions
    
    def validate_domain(self, domain_name: str) -> List[str]:
        """Validate a domain template for completeness."""
        errors = []
        
        try:
            domain = self.get_domain(domain_name)
            
            if not domain.description:
                errors.append(f"{domain_name}: Missing description")
            if not domain.typical_questions:
                errors.append(f"{domain_name}: No questions defined")
            if not domain.reasoning_pattern:
                errors.append(f"{domain_name}: No reasoning pattern")
            if not domain.required_facts:
                errors.append(f"{domain_name}: No required facts")
            if not domain.tax_rules:
                errors.append(f"{domain_name}: No tax rules")
                
        except ValueError as e:
            errors.append(str(e))
        
        return errors
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get template metadata."""
        return self.metadata.copy()