"""
Simple test to verify the complete system works.
Run this from the project root directory.
"""
import sys
import os
sys.path.append('src')

def test_core():
    """Test core module."""
    print("Testing core module...")
    try:
        from core import TaxCase, TaxFact
        
        facts = [TaxFact("Test expense $100", "story")]
        case = TaxCase(
            scenario_type="test",
            narrative="Test case",
            facts=facts,
            question="Test question?",
            correct_answer="Test answer",
            reasoning_steps=["Test reasoning"]
        )
        
        print("✓ Core module working")
        return True
    except Exception as e:
        print(f"✗ Core module error: {e}")
        return False

def test_llm_client():
    """Test LLM client."""
    print("Testing LLM client...")
    try:
        from llm_client import GroqClient
        print("✓ LLM client imports successfully")
        return True
    except Exception as e:
        print(f"✗ LLM client error: {e}")
        return False

def test_domains():
    """Test tax domains."""
    print("Testing tax domains...")
    try:
        from tax_domains import TaxDomainManager
        
        manager = TaxDomainManager()
        domains = manager.get_all_domains()
        
        print(f"✓ Tax domains working ({len(domains)} domains loaded)")
        return True
    except Exception as e:
        print(f"✗ Tax domains error: {e}")
        return False

def test_generator():
    """Test tax generator.""" 
    print("Testing tax generator...")
    try:
        from tax_generator import TaxGenerator
        print("✓ Tax generator imports successfully")
        return True
    except Exception as e:
        print(f"✗ Tax generator error: {e}")
        return False

def main():
    """Run all tests."""
    print("MuSR-SynTax System Test")
    print("=" * 40)
    
    tests = [
        test_core,
        test_llm_client, 
        test_domains,
        test_generator
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    print("=" * 40)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All systems working! Ready to run examples.")
    else:
        print("✗ Some systems have issues. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()