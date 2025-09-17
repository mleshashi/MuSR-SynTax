"""
Core data structures for Tax Law synthetic data generation.
Based on MuSR framework adapted for tax reasoning cases.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime


def classify_fact_type(fact: str) -> str:
    """
    Simple classifier to determine fact type from content.
    
    Args:
        fact: The fact text content to classify
        
    Returns:
        Classification as "story", "rule", or "conclusion"
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
    
    def __str__(self) -> str:
        """
        String representation of the tax fact.
        
        Returns:
            Formatted string showing fact type and content in format "[type] content"
        """
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
                       reasoning_steps: List[str]) -> 'TaxCase':
        """
        Create TaxCase from LLM-generated content with automatic fact classification.
        
        Args:
            scenario_type: Type of tax scenario (e.g., "business_meal_deduction")
            llm_facts: Raw facts from LLM as list of strings
            narrative: Generated narrative story
            question: The tax question being asked
            answer: The correct answer
            reasoning_steps: List of reasoning steps as strings
            
        Returns:
            Complete TaxCase instance with classified facts
        """
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
        """
        Convert TaxCase to dictionary for JSON export.
        
        Returns:
            Dictionary representation with all case data including facts as dicts
        """
        return {
            "scenario_type": self.scenario_type,
            "narrative": self.narrative,
            "facts": [{"content": f.content, "type": f.fact_type} for f in self.facts],
            "question": self.question,
            "correct_answer": self.correct_answer,
            "reasoning_steps": self.reasoning_steps
        }
    
    def save_to_file(self, filepath: Optional[str] = None) -> str:
        """
        Save case to JSON file in organized folder structure.
        
        Args:
            filepath: Optional custom filepath. If None, generates organized path with timestamp
            
        Returns:
            The filepath where the case was saved
        """
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
    
    def display(self) -> None:
        """
        Display the case in a readable format to console.
        
        Returns:
            None - prints formatted case information to console
        """
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
    # Example 1: Manual creation
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
    
    case.display()
    saved_path = case.save_to_file()
    print(f"\n✓ Case saved to {saved_path}")
    
    # Example 2: From LLM output (demonstrates conversion)
    print(f"\n=== Testing LLM Integration ===")
    
    llm_facts = [
        "Sarah works from home as a freelance graphic designer",
        "Home office deduction requires exclusive business use",
        "The home office space is 200 sq ft of a 2000 sq ft home",
        "Business percentage is 10% of total home expenses",
        "Sarah can deduct 10% of qualifying home expenses"
    ]
    
    case_from_llm = TaxCase.from_llm_output(
        scenario_type="home_office_deduction",
        llm_facts=llm_facts,
        narrative="Sarah is a freelance graphic designer who uses a dedicated room in her home exclusively for business. She wants to claim the home office deduction.",
        question="What percentage of home expenses can Sarah deduct?",
        answer="10% (200 sq ft ÷ 2000 sq ft)",
        reasoning_steps=[
            "Home office is used exclusively for business",
            "Office space is 200 sq ft of 2000 sq ft total",
            "Business percentage = 200 ÷ 2000 = 10%",
            "Therefore, 10% of qualifying expenses are deductible"
        ]
    )
    
    case_from_llm.display()
    saved_path2 = case_from_llm.save_to_file()
    print(f"\n✓ Second case saved to {saved_path2}")
    
    print(f"\n✓ Core module ready for case study!")