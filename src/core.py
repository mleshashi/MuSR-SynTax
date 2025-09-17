"""
Core data structures for Tax Law synthetic data generation.
Based on MuSR framework adapted for tax reasoning cases.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import json


def classify_fact_type(fact: str) -> str:
    """
    Simple classifier to determine fact type from content.
    
    Args:
        fact: The fact text to classify
        
    Returns:
        "story", "rule", or "conclusion"
    """
    fact_lower = fact.lower()
    
    # Rule indicators
    rule_keywords = ['deductible', 'section', 'irc', 'code', 'law', 'regulation', 
                    'must be', 'required', 'percent', '%', 'under']
    if any(keyword in fact_lower for keyword in rule_keywords):
        return "rule"
    
    # Conclusion indicators  
    conclusion_keywords = ['qualifies', 'therefore', 'result', 'conclusion', 
                          'deduction allowed', 'not deductible']
    if any(keyword in fact_lower for keyword in conclusion_keywords):
        return "conclusion"
    
    # Default to story (what happened)
    return "story"


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
    
    @classmethod
    def from_llm_output(cls, scenario_type: str, llm_facts: List[str], 
                       narrative: str, question: str, answer: str, 
                       reasoning_steps: List[str]):
        """
        Create TaxCase from LLM-generated content.
        Automatically classifies facts into types.
        
        Args:
            scenario_type: Type of tax scenario
            llm_facts: Raw facts from LLM
            narrative: Generated narrative
            question: The question
            answer: The answer
            reasoning_steps: Reasoning steps
        """
        # Simple heuristic to classify facts
        classified_facts = []
        for fact in llm_facts:
            fact_type = classify_fact_type(fact)
            classified_facts.append(TaxFact(content=fact, fact_type=fact_type))
        
        return cls(
            scenario_type=scenario_type,
            narrative=narrative,
            facts=classified_facts,
            question=question,
            correct_answer=answer,
            reasoning_steps=reasoning_steps
        )
    
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
    
    def save_to_file(self, filepath: str = None):
        """Save case to JSON file in organized folder structure."""
        import os
        from datetime import datetime
        
        if filepath is None:
            # Create organized folder structure
            base_dir = "data/generated"
            scenario_dir = os.path.join(base_dir, self.scenario_type)
            os.makedirs(scenario_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.scenario_type}_{timestamp}.json"
            filepath = os.path.join(scenario_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filepath
    
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
    
    # Test saving to organized folder
    saved_path = case.save_to_file()
    print(f"\n✓ Case saved to {saved_path}")
    
    # Test the conversion utility
    print(f"\n=== Testing LLM Integration ===")
    
    llm_facts = [
        "John spent $500 on client lunch",
        "Business meals are 50% deductible under IRC Section 274", 
        "The expense qualifies for deduction"
    ]
    
    case_from_llm = TaxCase.from_llm_output(
        scenario_type="business_meal_deduction",
        llm_facts=llm_facts,
        narrative="John took a client to lunch to discuss business.",
        question="How much is deductible?",
        answer="$250",
        reasoning_steps=["Meal was for business", "50% deductible", "$500 × 50% = $250"]
    )
    
    print(f"LLM Facts converted to:")
    for fact in case_from_llm.facts:
        print(f"  • {fact}")
    
    print(f"\n✓ Conversion utility working!")