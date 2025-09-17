"""
Core data structures for Tax Law synthetic data generation.
Based on MuSR framework adapted for tax reasoning cases.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import os


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
        """Convert TaxCase to dictionary for JSON export."""
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
        Save case to JSON file with clean naming (no timestamps).
        
        Args:
            filepath: Optional custom filepath. If None, uses clean organized path
            
        Returns:
            The filepath where the case was saved
        """
        if filepath is None:
            # Create organized folder structure
            base_dir = "data/generated"
            scenario_dir = os.path.join(base_dir, self.scenario_type)
            os.makedirs(scenario_dir, exist_ok=True)
            
            # Simple filename without timestamp
            filename = f"{self.scenario_type}.json"
            filepath = os.path.join(scenario_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filepath
    
    def display(self) -> None:
        """Display the case in a readable format to console."""
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