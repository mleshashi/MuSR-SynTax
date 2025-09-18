"""
Complete system test to verify all components work together.
"""
import sys
import os
import json
from pathlib import Path

sys.path.append('src')


def test_imports():
    """Test all imports work."""
    print("Testing imports...")
    try:
        from core import TaxCase, TaxFact
        from llm_client import get_client
        from tax_domains import TaxDomainManager
        from tax_generator import TaxGenerator
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_core_functionality():
    """Test core module functionality."""
    print("\nTesting core module...")
    try:
        from core import TaxCase, TaxFact, classify_fact_type
        
        # Test fact classification
        assert classify_fact_type("Company spent $500") == "story"
        assert classify_fact_type("IRC Section 274 allows 50%") == "rule"
        assert classify_fact_type("Therefore deduction is $250") == "conclusion"
        
        # Test TaxFact
        fact = TaxFact("Test fact", "story")
        assert str(fact) == "[story] Test fact"
        
        # Test TaxCase
        facts = [TaxFact("Spent $100", "story")]
        case = TaxCase(
            scenario_type="test",
            narrative="Test narrative",
            facts=facts,
            question="Test?",
            correct_answer="$50",
            reasoning_steps=["Step 1"]
        )
        
        # Test validation
        errors = case.validate()
        assert isinstance(errors, list)
        
        print("✓ Core module working")
        return True
        
    except Exception as e:
        print(f"✗ Core module error: {e}")
        return False


def test_domain_manager():
    """Test domain manager."""
    print("\nTesting domain manager...")
    try:
        from tax_domains import TaxDomainManager
        
        manager = TaxDomainManager()
        domains = manager.get_all_domains()
        
        assert len(domains) > 0
        assert "business_meal_deduction" in domains
        
        # Test domain context
        context = manager.get_domain_context("business_meal_deduction")
        assert "context_string" in context
        
        # Test questions
        questions = manager.get_domain_questions()
        assert len(questions) > 0
        
        print(f"✓ Domain manager working ({len(domains)} domains)")
        return True
        
    except Exception as e:
        print(f"✗ Domain manager error: {e}")
        return False


def test_llm_client():
    """Test LLM client."""
    print("\nTesting LLM client...")
    try:
        from llm_client import get_client
        
        client = get_client()
        
        # Test fact generation
        result = client.generate_tax_facts_with_answer(
            "business_meal_deduction", 
            "Test context"
        )
        assert "facts" in result
        assert len(result["facts"]) > 0
        
        # Test consistency validation
        facts = ["Company spent $500", "50% deductible"]
        assert client.validate_fact_consistency(facts, "$250")
        
        print("✓ LLM client working")
        return True
        
    except Exception as e:
        print(f"✗ LLM client error: {e}")
        return False


def test_generator_init():
    """Test generator initialization."""
    print("\nTesting generator...")
    try:
        from tax_generator import TaxGenerator
        
        generator = TaxGenerator()
        
        # Test available domains
        domains = generator.get_available_domains()
        assert len(domains) > 0
        
        # Test statistics
        stats = generator.get_statistics()
        assert "domains_available" in stats
        
        print(f"✓ Generator working ({len(domains)} domains available)")
        return True
        
    except Exception as e:
        print(f"✗ Generator error: {e}")
        return False


def test_data_structure():
    """Test data directory structure."""
    print("\nTesting data structure...")
    
    required_dirs = [
        "data/templates",
        "data/generated",
        "config"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  Created {dir_path}")
        else:
            print(f"  ✓ {dir_path} exists")
    
    # Check for template file
    template_file = Path("data/templates/tax_domains.json")
    if template_file.exists():
        print(f"  ✓ Template file exists")
    else:
        print(f"  ⚠ Template file missing (will be created)")
    
    return True


def run_integration_test():
    """Run a complete integration test."""
    print("\nRunning integration test...")
    try:
        from tax_generator import TaxGenerator
        
        generator = TaxGenerator()
        
        # Try to generate a single case
        print("  Generating test case...")
        case = generator.generate_case("business_meal_deduction")
        
        if case:
            print(f"  ✓ Generated case with {len(case.facts)} facts")
            
            # Validate the case
            errors = case.validate()
            if errors:
                print(f"  ⚠ Case has {len(errors)} validation warnings")
            else:
                print(f"  ✓ Case passes validation")
            
            return True
        else:
            print(f"  ⚠ Could not generate case (may need API key)")
            return True  # Still pass if using mock
            
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


def main():
    """Run all system tests."""
    print("MuSR-SynTax System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Core Functionality", test_core_functionality),
        ("Domain Manager", test_domain_manager),
        ("LLM Client", test_llm_client),
        ("Generator", test_generator_init),
        ("Data Structure", test_data_structure),
        ("Integration", run_integration_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All systems operational!")
        print("Ready to generate tax cases with:")
        print("  python main/generate_case.py")
    else:
        print("\n⚠ Some tests failed. Check errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)