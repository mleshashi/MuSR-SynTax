"""
LLM client for Groq API integration.
Handles communication with Groq models for tax case generation.
"""
import os
from typing import Optional, Dict, Any, List
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqClient:
    """Simple client for Groq API with tax-specific methods."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (if not provided, reads from GROQ_API_KEY env var)
            model: Model to use (if not provided, reads from GROQ_MODEL env var)
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
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"Error: {str(e)}"
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, 
                                  max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text with system and user prompts.
        
        Args:
            system_prompt: System instruction
            user_prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": user_prompt
                    }
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"Error: {str(e)}"
    
    def generate_tax_facts(self, scenario_type: str, context: str = "") -> List[str]:
        """
        Generate tax facts for a specific scenario.
        
        Args:
            scenario_type: Type of tax scenario
            context: Additional context for the scenario
            
        Returns:
            List of generated tax facts
        """
        system_prompt = """You are a tax law expert. Generate realistic, accurate tax facts for the given scenario. 
        Return each fact on a new line. Focus on:
        - Story facts (what happened)
        - Rule facts (relevant tax law)
        - Conclusion facts (logical outcomes)"""
        
        user_prompt = f"""Generate 5-7 tax facts for a {scenario_type} scenario.
        Context: {context}
        
        Make the facts realistic and legally sound."""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=500)
        
        # Parse response into list of facts
        facts = [fact.strip() for fact in response.split('\n') if fact.strip()]
        return facts
    
    def generate_tax_narrative(self, scenario_type: str, facts: List[str]) -> str:
        """
        Generate a narrative story from tax facts.
        
        Args:
            scenario_type: Type of tax scenario
            facts: List of facts to incorporate
            
        Returns:
            Generated narrative
        """
        system_prompt = """You are a skilled writer who creates realistic tax scenarios. 
        Write a clear, professional narrative that incorporates the given facts naturally."""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Write a realistic narrative for a {scenario_type} tax scenario that includes these facts:

{facts_text}

Create a 2-3 paragraph story that feels natural and professional."""
        
        return self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=800)
    
    def generate_reasoning_steps(self, scenario_type: str, facts: List[str], 
                               question: str, answer: str) -> List[str]:
        """
        Generate step-by-step reasoning for a tax case.
        
        Args:
            scenario_type: Type of tax scenario
            facts: Relevant facts
            question: The question being asked
            answer: The correct answer
            
        Returns:
            List of reasoning steps
        """
        system_prompt = """You are a tax expert who explains reasoning clearly. 
        Create logical, step-by-step reasoning that connects the facts to the conclusion."""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Given these facts about a {scenario_type}:

{facts_text}

Question: {question}
Answer: {answer}

Provide 3-5 clear reasoning steps that logically connect the facts to reach this answer."""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=600)
        
        # Parse response into list of steps
        steps = [step.strip() for step in response.split('\n') if step.strip()]
        return steps


# Example usage and testing
if __name__ == "__main__":
    # Test the client (requires GROQ_API_KEY in environment)
    try:
        client = GroqClient()
        
        print("Testing Groq client...")
        
        # Test 1: Simple text generation
        response = client.generate_text(
            "Generate a simple tax deduction scenario in one sentence.",
            max_tokens=100,
            temperature=0.5
        )
        print(f"\nTest 1 - Simple generation:")
        print(response)
        
        # Test 2: Tax facts generation
        facts = client.generate_tax_facts("business_meal_deduction", "A sales manager's client lunch")
        print(f"\nTest 2 - Generated tax facts:")
        for i, fact in enumerate(facts, 1):
            print(f"{i}. {fact}")
        
        # Test 3: Narrative generation
        if facts:
            narrative = client.generate_tax_narrative("business_meal_deduction", facts[:3])
            print(f"\nTest 3 - Generated narrative:")
            print(narrative)
        
        print("\n✓ Groq client working correctly!")
        
    except ValueError as e:
        print(f"Setup required: {e}")
        print("Please set GROQ_API_KEY in your .env file")
    except Exception as e:
        print(f"Error testing client: {e}")