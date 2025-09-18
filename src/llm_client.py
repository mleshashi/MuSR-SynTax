"""
LLM client for Groq API integration.
Handles communication with Groq models for tax case generation.
"""
import os
from typing import Optional, List
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqClient:
    def generate_dynamic_answer(self, scenario_type: str, facts: list, narrative: str, question: str) -> str:
        """
        Generate the answer dynamically using LLM based on the actual case data.
        The answer should be only the direct, calculated result (number, percentage, or short phrase), with no explanation or reasoning.
        """
        system_prompt = (
            "You are a tax law expert. Given the scenario, calculate the final deductible amount or credit "
            "based ONLY on the provided facts, required reasoning pattern, and tax rules. "
            "Do NOT rely on the narrative except to understand context, and do NOT assume any facts that are not explicitly given. "
            "Always apply all statutory limits and adjustments relevant to the domain (e.g., business use percentage, AGI limitations, Section 179, bonus depreciation, MACRS conventions, meal deduction limitations, R&D credit rules, etc.). "
            "Follow the reasoning pattern for the domain step by step internally, but output ONLY the final deductible amount or credit as a single number or dollar amount. "
            "If multiple components contribute to the deduction or credit, combine them into a single total. "
            "Do NOT include explanations, steps, or any extra text. "
            "If the deduction or credit is zero, output '0'."
        )

        facts_text = "\n".join([f"- {fact}" for fact in facts])
        user_prompt = f"Scenario: {scenario_type}\n\nNarrative:\n{narrative}\n\nFacts:\n{facts_text}\n\nQuestion: {question}\n\nAnswer:"
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=50)
        return response.strip()
    """Simple client for Groq API with tax-specific methods."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (if not provided, reads from GROQ_API_KEY env var)
            model: Model to use (if not provided, reads from GROQ_MODEL env var)
            
        Returns:
            None
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama3-8b-8192")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set in environment or provided directly")
        
        self.client = Groq(api_key=self.api_key)
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using Groq API.
        
        Args:
            prompt: The input prompt to generate text from
            max_tokens: Maximum number of tokens to generate (default: 1000)
            temperature: Sampling temperature between 0.0-1.0 (default: 0.7)
            
        Returns:
            Generated text response from the LLM, or error message if API call fails
        """
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, 
                                  max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text with system and user prompts.
        
        Args:
            system_prompt: System instruction that defines the AI's role and behavior
            user_prompt: User's specific request or question
            max_tokens: Maximum number of tokens to generate (default: 1000)
            temperature: Sampling temperature between 0.0-1.0 (default: 0.7)
            
        Returns:
            Generated text response from the LLM, or error message if API call fails
        """
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_tax_facts(self, scenario_type: str, context: str = "") -> List[str]:
        """
        Generate clean tax facts for a specific scenario.
        
        Args:
            scenario_type: Type of tax scenario (e.g., "business_meal_deduction")
            context: Additional context information for generation (default: "")
            
        Returns:
            List of exactly 5 cleaned tax facts as strings, fallback facts if generation fails
        """
        system_prompt = """You are a tax law expert. Generate realistic, accurate tax facts.
        Return ONLY the facts, one per line. No numbering, no explanations, no formatting.
        Each fact should be 1-2 sentences maximum."""
        
        user_prompt = f"""Generate exactly 5 tax facts for a {scenario_type} scenario.
        Context: {context}
        
        Example format:
        John spent $500 on client lunch at a business restaurant
        Business meals are 50% deductible if ordinary and necessary
        Client meetings are ordinary business practice for sales
        Under IRC Section 274, business meals have deduction limits
        The expense qualifies for 50% deduction
        
        Generate similar facts - clean, concise, no formatting."""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=400)
        
        # Clean and parse response
        facts = []
        for line in response.split('\n'):
            line = line.strip()
            # Skip empty lines and common unwanted patterns
            if line and not line.lower().startswith(('here are', 'tax facts', 'facts for')):
                # Remove numbering and formatting
                clean_line = line.lstrip('1234567890.- ').replace('**', '').replace('*', '')
                # Remove category labels
                if ':' in clean_line and any(keyword in clean_line.lower() 
                                           for keyword in ['story fact', 'rule fact', 'conclusion fact']):
                    clean_line = clean_line.split(':', 1)[1].strip()
                
                if clean_line:  # Only add non-empty lines
                    facts.append(clean_line)
        
        return facts[:5]  # Return exactly 5 facts
    
    def generate_tax_narrative(self, scenario_type: str, facts: List[str]) -> str:
        """Generate a narrative story from tax facts."""
        system_prompt = """You are a skilled writer. Create a realistic tax scenario narrative.
        Write 2-3 paragraphs that naturally incorporate the given facts."""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Write a realistic narrative for a {scenario_type} that includes these facts:

{facts_text}

Create a professional, clear story that feels natural."""
        
        return self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=600)
    
    def generate_reasoning_steps(self, scenario_type: str, facts: List[str], 
                               question: str, answer: str) -> List[str]:
        """Generate step-by-step reasoning for a tax case."""
        system_prompt = """You are a tax expert. Create clear, logical reasoning steps.
        Return only the steps, one per line, no numbering."""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Given these facts about {scenario_type}:

{facts_text}

Question: {question}
Answer: {answer}

Provide 4 clear reasoning steps that connect the facts to this answer."""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=400)
        
        # Parse into clean steps
        steps = []
        for line in response.split('\n'):
            line = line.strip().lstrip('1234567890.- ')
            if line and not line.lower().startswith(('steps:', 'reasoning:')):
                steps.append(line)
        
        return steps[:4]  # Return exactly 4 steps


# Example usage and testing
if __name__ == "__main__":
    try:
        client = GroqClient()
        print("Testing Groq client for case study...")
        
        # Test 1: Clean facts generation
        facts = client.generate_tax_facts("business_meal_deduction", "Sales manager client lunch")
        print(f"\nGenerated facts:")
        for i, fact in enumerate(facts, 1):
            print(f"{i}. {fact}")
        
        # Test 2: Narrative generation
        if facts:
            narrative = client.generate_tax_narrative("business_meal_deduction", facts)
            print(f"\nGenerated narrative:")
            print(narrative[:300] + "..." if len(narrative) > 300 else narrative)
        
        # Test 3: Reasoning steps
        if facts:
            steps = client.generate_reasoning_steps(
                "business_meal_deduction", 
                facts, 
                "How much is deductible?", 
                "$250 (50% of $500)"
            )
            print(f"\nGenerated reasoning steps:")
            for i, step in enumerate(steps, 1):
                print(f"{i}. {step}")
        
        print("\n✓ Groq client working and ready for case study!")
        
    except ValueError as e:
        print(f"Setup required: {e}")
        print("Please set GROQ_API_KEY in your .env file")
    except Exception as e:
        print(f"Error: {e}")