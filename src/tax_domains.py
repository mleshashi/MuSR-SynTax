"""
Tax domain templates defining different tax reasoning scenarios.
Each domain specifies the logical structure for generating cases.
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
    reasoning_pattern: List[str]  # Logical steps pattern
    required_facts: List[str]     # Types of facts needed
    tax_rules: List[str]          # Relevant tax code sections
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain_name': self.domain_name,
            'description': self.description,
            'typical_questions': self.typical_questions,
            'reasoning_pattern': self.reasoning_pattern,
            'required_facts': self.required_facts,
            'tax_rules': self.tax_rules
        }


class TaxDomainManager:
    """Manages different tax domain templates for case generation."""
    
    def __init__(self):
        self.domains = {}
        self._initialize_default_domains()
    
    def _initialize_default_domains(self):
        """Initialize the built-in tax domains."""
        
        # Business Meal Deduction Domain
        business_meals = TaxDomainTemplate(
            domain_name="business_meal_deduction",
            description="Business meal expenses and their deductibility under IRC Section 274",
            typical_questions=[
                "How much of the meal expense is deductible?",
                "What percentage of business meals can be deducted?",
                "Is this meal expense qualifying for deduction?"
            ],
            reasoning_pattern=[
                "Identify the expense amount and business purpose",
                "Verify the meal meets 'ordinary and necessary' criteria",
                "Apply IRC Section 274 deduction percentage (50%)",
                "Calculate the deductible amount"
            ],
            required_facts=[
                "expense_amount",
                "business_purpose", 
                "participants_present",
                "meal_type_and_location"
            ],
            tax_rules=[
                "IRC Section 274 - Entertainment expenses",
                "50% limitation on business meals",
                "Ordinary and necessary business expense test"
            ]
        )
        
        # Home Office Deduction Domain
        home_office = TaxDomainTemplate(
            domain_name="home_office_deduction",
            description="Home office expenses for business use of home under IRC Section 280A",
            typical_questions=[
                "What percentage of home expenses can be deducted?",
                "Is the home office deduction allowed?",
                "How much can be claimed for home office expenses?"
            ],
            reasoning_pattern=[
                "Verify exclusive business use of space",
                "Calculate business percentage of home",
                "Identify qualifying home expenses",
                "Apply business percentage to expenses"
            ],
            required_facts=[
                "office_square_footage",
                "total_home_square_footage",
                "exclusive_business_use",
                "qualifying_expenses"
            ],
            tax_rules=[
                "IRC Section 280A - Business use of home",
                "Exclusive use test",
                "Regular use test",
                "Principal place of business test"
            ]
        )
        
        # Travel Expense Domain
        travel_expenses = TaxDomainTemplate(
            domain_name="travel_expense_deduction",
            description="Business travel expenses and their deductibility under IRC Section 162",
            typical_questions=[
                "Which travel expenses are deductible?",
                "Is this trip primarily for business?",
                "How much travel expense can be deducted?"
            ],
            reasoning_pattern=[
                "Determine if travel is away from tax home",
                "Verify business purpose of travel",
                "Identify ordinary and necessary expenses",
                "Calculate deductible amounts"
            ],
            required_facts=[
                "travel_destination",
                "business_purpose",
                "duration_of_trip",
                "expense_breakdown"
            ],
            tax_rules=[
                "IRC Section 162 - Business expenses",
                "Away from home test",
                "Temporary vs. indefinite assignment rules"
            ]
        )
        
        # Charitable Donation Domain
        charitable_donations = TaxDomainTemplate(
            domain_name="charitable_donation_deduction",
            description="Charitable contribution deductions under IRC Section 170",
            typical_questions=[
                "How much charitable deduction is allowed?",
                "Is this organization qualified for deductions?",
                "What are the donation limits?"
            ],
            reasoning_pattern=[
                "Verify qualified charitable organization",
                "Determine contribution amount and type",
                "Apply AGI limitation percentages",
                "Calculate allowable deduction"
            ],
            required_facts=[
                "organization_status",
                "donation_amount",
                "donation_type",
                "taxpayer_agi"
            ],
            tax_rules=[
                "IRC Section 170 - Charitable contributions",
                "50% AGI limitation for cash donations",
                "30% AGI limitation for capital gain property"
            ]
        )
        
        # Register all domains
        self.domains = {
            'business_meal_deduction': business_meals,
            'home_office_deduction': home_office,
            'travel_expense_deduction': travel_expenses,
            'charitable_donation_deduction': charitable_donations
        }
    
    def get_domain(self, domain_name: str) -> TaxDomainTemplate:
        """Get a specific tax domain template."""
        if domain_name not in self.domains:
            raise ValueError(f"Domain '{domain_name}' not found. Available: {list(self.domains.keys())}")
        return self.domains[domain_name]
    
    def get_all_domains(self) -> Dict[str, TaxDomainTemplate]:
        """Get all available tax domain templates."""
        return self.domains.copy()
    
    def add_custom_domain(self, domain: TaxDomainTemplate):
        """Add a custom tax domain template."""
        self.domains[domain.domain_name] = domain
    
    def save_domains_to_file(self, filepath: str = "data/templates/tax_domains.json"):
        """Save all domain templates to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        domains_data = {
            name: domain.to_dict() 
            for name, domain in self.domains.items()
        }
        
        with open(filepath, 'w') as f:
            json.dump(domains_data, f, indent=2)
        
        return filepath
    
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
    
    def get_suggested_question(self, domain_name: str) -> str:
        """Get a typical question for the domain."""
        domain = self.get_domain(domain_name)
        return domain.typical_questions[0] if domain.typical_questions else "What is the tax treatment?"


# Example usage and testing
if __name__ == "__main__":
    # Initialize domain manager
    manager = TaxDomainManager()
    
    print("=== Available Tax Domains ===")
    for name, domain in manager.get_all_domains().items():
        print(f"\n{name}:")
        print(f"  Description: {domain.description}")
        print(f"  Questions: {len(domain.typical_questions)}")
        print(f"  Reasoning steps: {len(domain.reasoning_pattern)}")
    
    # Test domain context generation
    print(f"\n=== Domain Context Example ===")
    context = manager.get_domain_context("business_meal_deduction")
    print(context)
    
    # Save domains to file
    saved_path = manager.save_domains_to_file()
    print(f"\n✓ Domain templates saved to {saved_path}")
    
    # Test adding custom domain
    print(f"\n=== Custom Domain Example ===")
    custom_domain = TaxDomainTemplate(
        domain_name="equipment_depreciation",
        description="Business equipment depreciation under IRC Section 168",
        typical_questions=["What is the depreciation deduction?"],
        reasoning_pattern=[
            "Determine asset class and recovery period",
            "Apply depreciation method",
            "Calculate annual deduction"
        ],
        required_facts=["asset_cost", "asset_type", "placed_in_service_date"],
        tax_rules=["IRC Section 168 - MACRS"]
    )
    
    manager.add_custom_domain(custom_domain)
    print(f"Added custom domain: {custom_domain.domain_name}")
    print(f"Total domains: {len(manager.get_all_domains())}")
    
    print(f"\n✓ Tax domains system working correctly!")