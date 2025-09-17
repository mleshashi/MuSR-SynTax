"""
Complete example demonstrating the MuSR-SynTax system.
This shows how all components work together to generate tax reasoning cases.
Clean version that avoids duplicate file generation.
"""
import sys
import os
import json
from pathlib import Path

# Add src to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tax_generator import TaxGenerator
from tax_domains import TaxDomainManager
from core import TaxCase


def setup_system():
    """Initialize the system and ensure templates are saved."""
    print("=" * 60)
    print("SYSTEM SETUP")
    print("=" * 60)
    
    # Initialize domain manager (this will auto-save templates)
    domain_manager = TaxDomainManager(auto_save_templates=True)
    
    # Initialize generator (no raw outputs by default)
    generator = TaxGenerator(save_raw_outputs=False)
    
    # Verify templates were saved
    template_path = "data/templates/tax_domains.json"
    if os.path.exists(template_path):
        print(f"✓ Domain templates saved to {template_path}")
    else:
        print(f"⚠ Template file not found at {template_path}")
    
    domains = domain_manager.get_all_domains()
    print(f"✓ Loaded {len(domains)} tax domains")
    for domain_name in domains.keys():
        print(f"  - {domain_name}")
    
    return generator, domain_manager


def demonstrate_single_case_generation(generator, domain_manager):
    """Demonstrate generating a single tax reasoning case."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Single Case Generation")
    print("=" * 60)
    
    try:
        # Generate a case using domain context
        domain_name = "business_meal_deduction"
        context = domain_manager.get_domain_context(domain_name)
        
        print(f"Generating case for: {domain_name}")
        
        case = generator.generate_case(domain_name, context)
        
        # Display the generated case
        case.display()
        
        return case
        
    except Exception as e:
        print(f"Error in single case generation: {e}")
        return None


def demonstrate_multiple_domains(generator):
    """Demonstrate generating cases across different tax domains."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Multiple Tax Domains (Clean Generation)")
    print("=" * 60)
    
    try:
        # Generate one case per domain to avoid duplicates
        domains_to_test = [
            "home_office_deduction", 
            "travel_expense_deduction",
            "vehicle_expense_deduction"
        ]
        
        cases = []
        for domain in domains_to_test:
            case = generator.generate_case(domain, f"Demonstration case for {domain}")
            cases.append(case)
        
        print(f"Generated {len(cases)} cases across {len(domains_to_test)} domains")
        
        # Show brief summary of each case
        for i, case in enumerate(cases, 1):
            print(f"\nCase {i}: {case.scenario_type}")
            print(f"  Question: {case.question}")
            print(f"  Answer: {case.correct_answer}")
            print(f"  Facts: {len(case.facts)} total")
        
        return cases
        
    except Exception as e:
        print(f"Error in multiple domain generation: {e}")
        return []


def demonstrate_batch_generation(generator):
    """Demonstrate batch generation with quality validation."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: Batch Generation with Validation")
    print("=" * 60)
    
    try:
        # Generate a small batch with quality validation
        cases = generator.generate_batch_with_validation(
            scenario_type="charitable_donation_deduction",
            count=2,
            validate_quality=True
        )
        
        print(f"Generated {len(cases)} validated cases")
        
        return cases
        
    except Exception as e:
        print(f"Error in batch generation: {e}")
        return []


def demonstrate_extensibility(domain_manager, generator):
    """Demonstrate how easy it is to add new tax domains."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION: System Extensibility")
    print("=" * 60)
    
    try:
        from tax_domains import TaxDomainTemplate
        
        # Create a new custom domain
        custom_domain = TaxDomainTemplate(
            domain_name="equipment_depreciation",
            description="Business equipment depreciation under IRC Section 168",
            typical_questions=[
                "What is the depreciation deduction?",
                "Should I use straight-line or accelerated depreciation?"
            ],
            reasoning_pattern=[
                "Determine asset class and recovery period",
                "Apply appropriate depreciation method",
                "Calculate annual deduction amount",
                "Consider bonus depreciation if applicable"
            ],
            required_facts=[
                "asset_cost",
                "asset_type", 
                "placed_in_service_date",
                "depreciation_method"
            ],
            tax_rules=[
                "IRC Section 168 - MACRS",
                "IRC Section 179 - Expensing election",
                "Bonus depreciation rules"
            ]
        )
        
        # Add the custom domain (this will auto-update templates file)
        domain_manager.add_custom_domain(custom_domain)
        print(f"✓ Added new domain: {custom_domain.domain_name}")
        
        # Generate a case using the new domain
        context = domain_manager.get_domain_context("equipment_depreciation")
        case = generator.generate_case("equipment_depreciation", context)
        
        print(f"\nGenerated case using new domain:")
        print(f"Scenario: {case.scenario_type}")
        print(f"Question: {case.question}")
        
        return case
        
    except Exception as e:
        print(f"Error in extensibility demonstration: {e}")
        return None


def save_example_output(case: TaxCase):
    """Save a sample case as example output for the repository."""
    if case:
        example_path = "examples/sample_output.json"
        os.makedirs(os.path.dirname(example_path), exist_ok=True)
        
        with open(example_path, 'w') as f:
            json.dump(case.to_dict(), f, indent=2)
        
        print(f"✓ Example output saved to: {example_path}")


def show_system_summary(generator):
    """Show comprehensive system statistics."""
    print("\n" + "=" * 60)
    print("SYSTEM SUMMARY")
    print("=" * 60)
    
    # Show generation statistics
    stats = generator.get_generation_stats()
    print("Generation Statistics:")
    for key, value in stats.items():
        if key == 'scenario_breakdown':
            print(f"  {key}:")
            for scenario, count in value.items():
                print(f"    {scenario}: {count} cases")
        else:
            print(f"  {key}: {value}")
    
    # Save generation summary
    summary_path = generator.save_generation_summary()
    print(f"\n✓ Generation summary saved to: {summary_path}")
    
    # Check file organization
    print(f"\nFile Organization:")
    base_dir = "data"
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            level = root.replace(base_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:3]:  # Show max 3 files per directory
                print(f"{subindent}{file}")
            if len(files) > 3:
                print(f"{subindent}... and {len(files) - 3} more files")


def cleanup_old_files():
    """Clean up any duplicate or unnecessary files from previous runs."""
    print("\n" + "=" * 60)
    print("CLEANUP: Removing Duplicate Files")
    print("=" * 60)
    
    # Remove old llm_raw directory if it exists
    old_raw_dir = "data/generated/llm_raw"
    if os.path.exists(old_raw_dir):
        import shutil
        shutil.rmtree(old_raw_dir)
        print(f"✓ Removed old raw output directory: {old_raw_dir}")
    
    # Count current files
    generated_dir = "data/generated"
    if os.path.exists(generated_dir):
        total_files = 0
        for root, dirs, files in os.walk(generated_dir):
            total_files += len([f for f in files if f.endswith('.json')])
        print(f"✓ Current case files: {total_files}")
    
    return True


def main():
    """Main demonstration function with clean file management."""
    print("MuSR-SynTax: Synthetic Tax Law Data Generator")
    print("Clean Implementation - No Duplicate Files")
    
    # Check for API key
    api_key_status = "✓ Found" if os.getenv("GROQ_API_KEY") else "⚠ Missing - will use mock data"
    print(f"API Key Status: {api_key_status}")
    
    try:
        # Step 1: Clean up any old duplicate files
        cleanup_old_files()
        
        # Step 2: Setup system (saves templates automatically)
        generator, domain_manager = setup_system()
        
        # Step 3: Single case generation
        case = demonstrate_single_case_generation(generator, domain_manager)
        
        # Step 4: Save first case as example output
        if case:
            save_example_output(case)
        
        # Step 5: Multiple domains (clean, no duplicates)
        demonstrate_multiple_domains(generator)
        
        # Step 6: Batch generation with validation
        demonstrate_batch_generation(generator)
        
        # Step 7: Extensibility demonstration
        demonstrate_extensibility(domain_manager, generator)
        
        # Step 8: Show final system summary
        show_system_summary(generator)
        
        print(f"\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("✓ Clean file organization (no duplicates)")
        print("✓ Templates saved to data/templates/")
        print("✓ Cases saved to data/generated/[scenario_type]/")
        print("✓ Example output in examples/")
        print("✓ Generation summary in data/")
        print("✓ System ready for production use")
        
    except Exception as e:
        print(f"Demonstration error: {e}")
        print("Check API key setup and network connection")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)