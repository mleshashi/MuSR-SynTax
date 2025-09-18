"""
Core data structures for Tax Law synthetic data generation.
Based on MuSR framework adapted for tax reasoning cases.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
import os
import re


def classify_fact_type(fact: str) -> str:
    """
    Improved classifier to determine fact type from content.
    
    Args:
        fact: The fact text content to classify
        
    Returns:
        Classification as "story", "rule", or "conclusion"
    """
    fact_lower = fact.lower()
    
    # Conclusion indicators (check first - highest priority)
    conclusion_keywords = ['therefore', 'thus', 'hence', 'qualifies for', 
                          'is deductible', 'can deduct', 'deduction allowed',
                          'is allowed', 'can claim', 'resulting in']
    if any(keyword in fact_lower for keyword in conclusion_keywords):
        return "conclusion"
    
    # Rule indicators (tax code references and regulations)
    rule_keywords = ['irc section', 'under section', 'code sec', 'regulation',
                    '% limitation', 'per diem', 'standard mileage rate',
                    'must be', 'required', 'tax law', 'tax code']
    if any(keyword in fact_lower for keyword in rule_keywords):
        return "rule"
    
    # Default to story (factual situations)
    return "story"


@dataclass
class TaxFact:
    """A single fact in our tax reasoning case."""
    content: str
    fact_type: str  # "story", "rule", or "conclusion"
    
    def __str__(self) -> str:
        return f"[{self.fact_type}] {self.content}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "type": self.fact_type
        }


@dataclass
class TaxCase:
    """A complete generated tax reasoning case."""
    scenario_type: str          # e.g., "business_deduction"
    narrative: str              # The story/situation
    facts: List[TaxFact]       # All facts in logical order
    question: str              # What we're asking
    correct_answer: str        # The right answer
    reasoning_steps: List[str] # Step-by-step logic
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    
    @classmethod
    def from_llm_output(cls, scenario_type: str, llm_facts: List[str], 
                       narrative: str, question: str, answer: str, 
                       reasoning_steps: List[str], metadata: Optional[Dict] = None) -> 'TaxCase':
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
            reasoning_steps=reasoning_steps,
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TaxCase to dictionary for JSON export."""
        result = {
            "scenario_type": self.scenario_type,
            "narrative": self.narrative,
            "facts": [f.to_dict() for f in self.facts],
            "question": self.question,
            "correct_answer": self.correct_answer,
            "reasoning_steps": self.reasoning_steps
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaxCase':
        """Create TaxCase from dictionary."""
        facts = [TaxFact(content=f["content"], fact_type=f["type"]) 
                for f in data["facts"]]
        
        return cls(
            scenario_type=data["scenario_type"],
            narrative=data["narrative"],
            facts=facts,
            question=data["question"],
            correct_answer=data["correct_answer"],
            reasoning_steps=data["reasoning_steps"],
            metadata=data.get("metadata", {})
        )
    
    def validate(self) -> List[str]:
        """
        Validate the case for consistency and completeness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for required fields
        if not self.scenario_type:
            errors.append("Missing scenario type")
        if not self.narrative:
            errors.append("Missing narrative")
        if not self.facts:
            errors.append("No facts provided")
        if not self.question:
            errors.append("Missing question")
        if not self.correct_answer:
            errors.append("Missing answer")
        if not self.reasoning_steps:
            errors.append("No reasoning steps provided")
        
        # Check fact diversity
        fact_types = {f.fact_type for f in self.facts}
        if len(fact_types) < 2:
            errors.append(f"Insufficient fact diversity: only {fact_types}")
        
        # Check answer consistency
        if not self._check_answer_in_reasoning():
            errors.append("Answer not referenced in reasoning steps")
        
        # Check numerical consistency
        if not self._check_numerical_consistency():
            errors.append("Numerical values inconsistent between facts and answer")
        
        return errors
    
    def _check_answer_in_reasoning(self) -> bool:
        """Check if answer is referenced in reasoning."""
        # Extract core number from answer
        answer_nums = re.findall(r'[\d,]+(?:\.\d+)?', self.correct_answer)
        if not answer_nums:
            return True  # Can't validate non-numeric answers
        
        reasoning_text = ' '.join(self.reasoning_steps).lower()
        return any(num in reasoning_text for num in answer_nums)
    
    def _check_numerical_consistency(self) -> bool:
        """Check if answer can be derived from facts."""
        # Extract all numbers from facts
        fact_numbers = []
        for fact in self.facts:
            numbers = re.findall(r'\$?([\d,]+(?:\.\d+)?)', fact.content)
            fact_numbers.extend([float(n.replace(',', '')) for n in numbers if n])
        
        if not fact_numbers:
            return True
        
        # Extract number from answer
        answer_match = re.search(r'\$?([\d,]+(?:\.\d+)?)', self.correct_answer)
        if not answer_match:
            return True
        
        answer_num = float(answer_match.group(1).replace(',', ''))
        
        # Check if answer appears directly or can be derived
        if answer_num in fact_numbers:
            return True
        
        # Check common calculations
        for num in fact_numbers:
            # 50% calculation (meals)
            if abs(num * 0.5 - answer_num) < 1:
                return True
            # 30% calculation
            if abs(num * 0.3 - answer_num) < 1:
                return True
            # Percentage calculations
            for denom in fact_numbers:
                if denom > 0:
                    percentage = (num / denom) * 100
                    if abs(percentage - answer_num) < 0.1:
                        return True
        
        return False
    
    def save_to_file(self, filepath: Optional[str] = None) -> str:
        """
        Save case to JSON file with validation.
        
        Args:
            filepath: Optional custom filepath. If None, uses organized path
            
        Returns:
            The filepath where the case was saved
        """
        # Validate before saving
        errors = self.validate()
        if errors:
            print(f"Warning: Case has validation errors: {errors}")
        
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
        print(f"\nNarrative:\n{self.narrative[:500]}..." if len(self.narrative) > 500 else f"\nNarrative:\n{self.narrative}")
        
        print(f"\nKey Facts ({len(self.facts)} total):")
        # Group facts by type
        by_type = {'story': [], 'rule': [], 'conclusion': []}
        for fact in self.facts:
            by_type[fact.fact_type].append(fact)
        
        for fact_type, facts in by_type.items():
            if facts:
                print(f"  {fact_type.title()} Facts:")
                for fact in facts[:2]:  # Show first 2 of each type
                    print(f"    • {fact.content[:100]}..." if len(fact.content) > 100 else f"    • {fact.content}")
        
        print(f"\nQuestion: {self.question}")
        print(f"Answer: {self.correct_answer}")
        
        print(f"\nReasoning Steps:")
        for i, step in enumerate(self.reasoning_steps[:3], 1):  # Show first 3 steps
            print(f"  {i}. {step[:150]}..." if len(step) > 150 else f"  {i}. {step}")
        
        if len(self.reasoning_steps) > 3:
            print(f"  ... ({len(self.reasoning_steps) - 3} more steps)")
        
        # Show validation status
        errors = self.validate()
        if errors:
            print(f"\n⚠ Validation Errors: {', '.join(errors)}")
        else:
            print(f"\n✓ Case validation passed")