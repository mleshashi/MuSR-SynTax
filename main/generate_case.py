"""
Implementation of MuSR-SynTax system.
Fully dynamic - all domains loaded from JSON templates.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tax_generator import TaxGenerator
from tax_domains import TaxDomainManager


def main():
    """Main function - fully dynamic case generation."""
    print("MuSR-SynTax: Synthetic Tax Law Data Generator")
    print("Fully Dynamic Implementation")
    print("=" * 50)
    
    # Check API key
    api_key_status = "✓ Found" if os.getenv("GROQ_API_KEY") else "⚠ Missing - will use mock data"
    print(f"API Key: {api_key_status}")
    
    try:
        # Initialize system - everything loads from JSON
        print("\nInitializing system...")
        generator = TaxGenerator()
        
        # Show available domains (loaded from JSON)
        available_domains = generator.get_available_domains()
        print(f"✓ Available domains: {available_domains}")
        
        # Generate cases for all domains found in templates
        print(f"\nGenerating tax cases...")
        cases = generator.generate_all_domains()  # No arguments needed - fully dynamic!
        
        # Display results
        print(f"\n" + "=" * 50)
        print("GENERATION COMPLETE")
        print("=" * 50)
        print(f"✓ Generated {len(cases)} cases from JSON templates")
        
        for case in cases:
            filepath = f"data/generated/{case.scenario_type}/{case.scenario_type}.json"
            print(f"  {case.scenario_type} → {filepath}")
        
        print(f"\n✓ All domain templates loaded from: data/templates/tax_domains.json")
        print(f"✓ Cases organized by scenario type in data/generated/")
        print(f"✓ Add new domains by editing the JSON template only")
        
        # Show sample case
        if cases:
            print(f"\n" + "-" * 30)
            print("SAMPLE CASE:")
            print("-" * 30)
            cases[0].display()
        
        # Show how to add new domains
        print(f"\n" + "=" * 50)
        print("TO ADD NEW DOMAINS:")
        print("=" * 50)
        print("1. Edit data/templates/tax_domains.json")
        print("2. Add your domain following the existing pattern")
        print("3. Run this script again")
        print("4. New cases generated automatically!")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)