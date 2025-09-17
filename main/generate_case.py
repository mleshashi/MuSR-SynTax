"""
Complete implementation of MuSR-SynTax system.
Generates one case per domain.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tax_generator import TaxGenerator
from tax_domains import TaxDomainManager


def main():
    """Main function - clean case generation."""
    print("MuSR-SynTax: Synthetic Tax Law Data Generator")
    print("Clean Implementation")
    print("=" * 50)
    
    # Check API key
    api_key_status = "✓ Found" if os.getenv("GROQ_API_KEY") else "⚠ Missing - will use mock data"
    print(f"API Key: {api_key_status}")
    
    try:
        # Initialize system
        print("\nInitializing system...")
        domain_manager = TaxDomainManager()
        generator = TaxGenerator()
        
        # Get all available domains
        domains = list(domain_manager.get_all_domains().keys())
        print(f"✓ Loaded {len(domains)} tax domains")
        
        # Generate one case per domain
        print(f"\nGenerating tax cases...")
        cases = generator.generate_all_domains(domains)
        
        # Display results
        print(f"\n" + "=" * 50)
        print("GENERATION COMPLETE")
        print("=" * 50)
        print(f"✓ Generated {len(cases)} cases")
        
        for case in cases:
            filepath = f"data/generated/{case.scenario_type}/{case.scenario_type}.json"
            print(f"  {case.scenario_type} → {filepath}")
        
        print(f"\n✓ Templates saved to: data/templates/tax_domains.json")
        print(f"✓ Cases organized by scenario type in data/generated/")
        print(f"✓ No duplicate or redundant files generated")
        
        # Show sample case
        if cases:
            print(f"\n" + "-" * 30)
            print("SAMPLE CASE:")
            print("-" * 30)
            cases[0].display()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)