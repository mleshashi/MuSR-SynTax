"""
Tax domain templates defining different tax reasoning scenarios.
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
    """Manages different tax domain templates for case generation."""
    
    def __init__(self) -> None:
        """Initialize domain manager and save templates."""
        self.domains = {}
        self._initialize_default_domains()
        self._save_templates()
    
    def _initialize_default_domains(self):
        """Initialize the built-in tax domains."""
        
        domains_data = {
            'business_meal_deduction': TaxDomainTemplate(
                domain_name="business_meal_deduction",
                description="Business meal expenses and their deductibility under IRC Section 274",
                typical_questions=["How much of the meal expense is deductible?"],
                reasoning_pattern=[
                    "Identify the expense amount and business purpose",
                    "Verify the meal meets 'ordinary and necessary' criteria",
                    "Apply IRC Section 274 deduction percentage (50%)",
                    "Calculate the deductible amount"
                ],
                required_facts=["expense_amount", "business_purpose", "participants_present", "meal_type_and_location"],
                tax_rules=["IRC Section 274 - Entertainment expenses", "50% limitation on business meals"]
            ),
            
            'home_office_deduction': TaxDomainTemplate(
                domain_name="home_office_deduction",
                description="Home office expenses for business use of home under IRC Section 280A",
                typical_questions=["What percentage of home expenses can be deducted?"],
                reasoning_pattern=[
                    "Verify exclusive business use of space",
                    "Calculate business percentage of home",
                    "Apply business percentage to expenses"
                ],
                required_facts=["office_square_footage", "total_home_square_footage", "exclusive_business_use"],
                tax_rules=["IRC Section 280A - Business use of home", "Exclusive use test"]
            ),
            
            'travel_expense_deduction': TaxDomainTemplate(
                domain_name="travel_expense_deduction",
                description="Business travel expenses and their deductibility under IRC Section 162",
                typical_questions=["Which travel expenses are deductible?"],
                reasoning_pattern=[
                    "Determine if travel is away from tax home",
                    "Verify business purpose of travel",
                    "Calculate deductible amounts"
                ],
                required_facts=["travel_destination", "business_purpose", "expense_breakdown"],
                tax_rules=["IRC Section 162 - Business expenses", "Away from home test"]
            ),
            
            'charitable_donation_deduction': TaxDomainTemplate(
                domain_name="charitable_donation_deduction",
                description="Charitable contribution deductions under IRC Section 170",
                typical_questions=["How much charitable deduction is allowed?"],
                reasoning_pattern=[
                    "Verify qualified charitable organization",
                    "Apply AGI limitation percentages",
                    "Calculate allowable deduction"
                ],
                required_facts=["organization_status", "donation_amount", "taxpayer_agi"],
                tax_rules=["IRC Section 170 - Charitable contributions", "50% AGI limitation"]
            ),
            
            'vehicle_expense_deduction': TaxDomainTemplate(
                domain_name="vehicle_expense_deduction",
                description="Business vehicle expense deductions under IRC Section 162",
                typical_questions=["What vehicle expenses are deductible?"],
                reasoning_pattern=[
                    "Determine business vs. personal use percentage",
                    "Choose deduction method",
                    "Calculate allowable business deduction"
                ],
                required_facts=["business_miles", "total_miles", "vehicle_expenses"],
                tax_rules=["IRC Section 162 - Business expenses", "Standard mileage rate"]
            )
        }
        
        self.domains = domains_data
    
    def _save_templates(self):
        """Save domain templates to file."""
        os.makedirs("data/templates", exist_ok=True)
        
        templates_data = {
            name: {
                'domain_name': domain.domain_name,
                'description': domain.description,
                'typical_questions': domain.typical_questions,
                'reasoning_pattern': domain.reasoning_pattern,
                'required_facts': domain.required_facts,
                'tax_rules': domain.tax_rules
            }
            for name, domain in self.domains.items()
        }
        
        with open("data/templates/tax_domains.json", 'w') as f:
            json.dump(templates_data, f, indent=2)
    
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

Relevant tax rules:
{chr(10).join([f"- {rule}" for rule in domain.tax_rules])}
"""
        return context