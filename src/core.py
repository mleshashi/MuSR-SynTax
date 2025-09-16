"""
Data structures for Tax Law synthetic data generation.
Based on MuSR framework adapted for tax reasoning cases.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class TaxFact:
    """A single fact in our tax reasoning case."""
    content: str
    fact_type: str  # "story", "rule", or "conclusion"
    
    def __str__(self):
        return f"[{self.fact_type}] {self.content}"


@dataclass
class TaxCase:
    """A complete generated tax reasoning case."""
    scenario_type: str          # e.g., "business_deduction"
    narrative: str              # The story/situation
    facts: List[TaxFact]       # All facts in logical order
    question: str              # What we're asking
    correct_answer: str        # The right answer
    reasoning_steps: List[str] # Step-by-step logic
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "scenario_type": self.scenario_type,
            "narrative": self.narrative,
            "facts": [{"content": f.content, "type": f.fact_type} for f in self.facts],
            "question": self.question,
            "correct_answer": self.correct_answer,
            "reasoning_steps": self.reasoning_steps
        }
    
    def save_to_file(self, filepath: str):
        """Save case to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def display(self):
        """Display the case in a readable format."""
        print(f"\n=== {self.scenario_type.replace('_', ' ').title()} Case ===")
        print(f"\nNarrative:\n{self.narrative}")
        
        print(f"\nKey Facts:")
        for fact in self.facts:
            print(f"  • {fact}")
        
        print(f"\nQuestion: {self.question}")
        print(f"Answer: {self.correct_answer}")
        
        print(f"\nReasoning:")
        for i, step in enumerate(self.reasoning_steps, 1):
            print(f"  {i}. {step}")


# Example usage for testing
if __name__ == "__main__":
    # Create a simple tax case
    facts = [
        TaxFact("John spent $500 on client lunch", "story"),
        TaxFact("Business meals are 50% deductible if ordinary and necessary", "rule"),
        TaxFact("Client meetings are ordinary business practice", "rule"),
        TaxFact("The expense qualifies for deduction", "conclusion")
    ]
    
    case = TaxCase(
        scenario_type="business_meal_deduction",
        narrative="John is a sales manager who took a potential client to lunch to discuss a new contract. He paid $500 for the meal at a business restaurant.",
        facts=facts,
        question="How much of John's meal expense is deductible?",
        correct_answer="$250 (50% of $500)",
        reasoning_steps=[
            "The meal was with a client for business purposes",
            "Business meals are ordinary and necessary for sales work", 
            "Under IRC Section 274, business meals are 50% deductible",
            "Therefore: $500 × 50% = $250 deductible"
        ]
    )
    
    # Test the display
    case.display()
    
    # Test saving to file
    case.save_to_file("test_case.json")
    print(f"\n✓ Case saved to test_case.json")