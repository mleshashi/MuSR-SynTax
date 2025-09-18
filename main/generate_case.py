"""
Implementation of MuSR-SynTax system with enhanced validation.
Fully dynamic - all domains loaded from JSON templates.
"""
import sys
import os
from pathlib import Path
import argparse

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tax_generator import TaxGenerator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MuSR-SynTax: Synthetic Tax Law Data Generator"
    )
    parser.add_argument(
        "--domain",
        type=str,
        help="Generate specific domain only"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if cases exist"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing cases"
    )
    parser.add_argument(
        "--fix-invalid",
        action="store_true",
        help="Regenerate invalid cases"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only"
    )
    return parser.parse_args()


def main():
    """Main function with enhanced options."""
    args = parse_arguments()
    
    print("MuSR-SynTax: Synthetic Tax Law Data Generator")
    print("Enhanced Version with Validation")
    print("=" * 50)
    
    # Check API key
    api_key_status = "✓ Found" if os.getenv("GROQ_API_KEY") else "⚠ Using mock client"
    print(f"API Key: {api_key_status}")
    
    try:
        # Initialize generator
        print("\nInitializing system...")
        generator = TaxGenerator()
        
        # Show available domains
        available_domains = generator.get_available_domains()
        print(f"✓ Available domains: {', '.join(available_domains)}")
        
        # Handle different modes
        if args.stats:
            # Show statistics only
            stats = generator.get_statistics()
            print("\n" + "=" * 50)
            print("CURRENT STATISTICS")
            print("=" * 50)
            for key, value in stats.items():
                print(f"{key:20s}: {value}")
            return True
        
        elif args.validate:
            # Validate existing cases
            print("\nValidating existing cases...")
            validation_results = generator.validate_all_generated()
            
            if validation_results:
                print(f"\n✗ Found {len(validation_results)} cases with errors:")
                for scenario, errors in validation_results.items():
                    print(f"  {scenario}:")
                    for error in errors[:2]:  # Show first 2 errors
                        print(f"    - {error}")
            else:
                print("✓ All cases valid!")
            return len(validation_results) == 0
        
        elif args.fix_invalid:
            # Fix invalid cases
            print("\nRegenerating invalid cases...")
            regenerated = generator.regenerate_invalid_cases()
            print(f"✓ Regenerated {len(regenerated)} cases")
            return True
        
        elif args.domain:
            # Generate specific domain
            if args.domain not in available_domains:
                print(f"Error: Domain '{args.domain}' not available")
                print(f"Available: {available_domains}")
                return False
            
            case = generator.generate_case(args.domain, force_regenerate=args.force)
            if case:
                print("\n" + "-" * 30)
                print("GENERATED CASE:")
                print("-" * 30)
                case.display()
            return case is not None
        
        else:
            # Generate all domains
            print(f"\nGenerating all tax cases...")
            cases = generator.generate_all_domains(force_regenerate=args.force)
            
            # Display results
            print(f"\n" + "=" * 50)
            print("GENERATION COMPLETE")
            print("=" * 50)
            print(f"✓ Generated {len(cases)} valid cases")
            
            for case in cases:
                filepath = f"data/generated/{case.scenario_type}/{case.scenario_type}.json"
                errors = case.validate()
                status = "✓" if not errors else f"⚠ ({len(errors)} warnings)"
                print(f"  {status} {case.scenario_type} → {filepath}")
            
            # Show sample case
            if cases:
                print(f"\n" + "-" * 30)
                print("SAMPLE CASE:")
                print("-" * 30)
                cases[-1].display()
            
            return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)