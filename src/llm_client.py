"""
LLM client for Groq API integration.
Handles communication with Groq models for tax case generation.
"""
import os
import re
from typing import Optional, List, Dict, Any
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GroqClient:
    """Client for Groq API with improved tax case generation methods."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
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
            temperature: Sampling temperature
            
        Returns:
            Generated text or error message
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
            system_prompt: System instruction
            user_prompt: User request
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Generated text or error message
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
    
    def generate_tax_facts_with_answer(self, scenario_type: str, context: str = "") -> Dict[str, Any]:
        """
        Generate tax facts that contain both the setup and embedded answer.
        
        Returns:
            Dictionary with 'facts' list and 'embedded_answer' string
        """
        system_prompt = """You are a tax expert creating self-contained tax scenarios.
        
        Generate facts that tell a complete story INCLUDING the answer.
        The facts should contain:
        1. Initial situation with specific amounts
        2. Applicable tax rules or percentages
        3. The calculated result or deduction amount
        
        Output clean facts, one per line. No formatting or numbering."""
        
        user_prompt = f"""Generate 5 tax facts for {scenario_type}.
        
        Pattern to follow:
        - Initial amount or situation (with specific numbers)
        - Applicable tax rule or percentage
        - The calculated deduction or result
        - Supporting context facts
        
        Example for business meals:
        The company spent $400 on a client dinner
        Business meals are 50% deductible under IRC Section 274
        The company can deduct $200 for this meal expense
        The dinner was with potential clients discussing a new contract
        The expense meets ordinary and necessary business requirements
        
        Now generate similar self-contained facts for: {scenario_type}
        Context: {context}"""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=400)
        
        # Parse response
        facts = []
        embedded_answer = None
        
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.lower().startswith(('here', 'facts:', 'note:')):
                clean_line = line.lstrip('1234567890.- ').strip()
                if clean_line:
                    facts.append(clean_line)
                    
                    # Try to identify the answer fact
                    if any(kw in clean_line.lower() for kw in ['can deduct', 'deduction is', 
                                                                'allowed', 'qualifies for']):
                        # Extract numerical answer
                        nums = re.findall(r'\$?([\d,]+(?:\.\d+)?)', clean_line)
                        if nums and not embedded_answer:
                            embedded_answer = f"${nums[-1]}"
        
        return {
            "facts": facts[:5],
            "embedded_answer": embedded_answer
        }
    
    def generate_dynamic_answer(self, scenario_type: str, facts: List[str], 
                              narrative: str, question: str) -> str:
        """
        Generate answer using pattern matching from facts.
        No domain expertise required - derives from facts themselves.
        """
        system_prompt = """You are analyzing tax facts to answer a question.
        
        CRITICAL INSTRUCTIONS:
        1. Look for numerical values in the facts (amounts, percentages, square footage)
        2. Look for calculation rules IN THE FACTS (e.g., "50% deductible", "$5 per sq ft")
        3. Apply ONLY the rules found in the facts to the numbers found in the facts
        4. Output ONLY the calculated result
        
        DO NOT use external tax knowledge. Use ONLY what's stated in the facts.
        
        Examples:
        - Facts say "$500 spent" + "50% deductible" → Answer: $250
        - Facts say "250 sq ft office" + "2000 sq ft home" → Answer: 12.5%
        - Facts say "$200 can be deducted" → Answer: $200
        - Facts say "qualifies for $1,500 credit" → Answer: $1,500"""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Facts provided:
{facts_text}

Question: {question}

Based ONLY on these facts, what is the answer? 
If the answer is already stated in the facts, use that.
If calculation is needed, show only the final result.
Output only the number/amount/percentage."""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=50)
        
        # Clean the response
        response = response.strip()
        # Remove explanatory text if present
        if ':' in response:
            response = response.split(':')[-1].strip()
        
        return response
    
    def generate_tax_narrative(self, scenario_type: str, facts: List[str]) -> str:
        """Generate a narrative story from tax facts."""
        system_prompt = """You are a skilled writer creating realistic tax scenarios.
        Write a coherent narrative that naturally incorporates the given facts.
        Make it feel like a real situation, not a textbook example."""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Write a 2-3 paragraph narrative for {scenario_type}.
        
        Incorporate these facts naturally:
{facts_text}

        Make it realistic and professional. Use names and specific details."""
        
        return self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=600)
    
    def generate_reasoning_steps(self, scenario_type: str, facts: List[str], 
                               question: str, answer: str) -> List[str]:
        """Generate step-by-step reasoning that connects facts to answer."""
        system_prompt = """You are a tax expert explaining calculations step-by-step.
        Create clear reasoning that shows how the facts lead to the answer.
        Use the actual numbers and rules from the facts.
        Output only the steps, one per line."""
        
        facts_text = "\n".join([f"- {fact}" for fact in facts])
        
        user_prompt = f"""Given these facts:
{facts_text}

Question: {question}
Answer: {answer}

Provide 4 clear steps showing how these specific facts lead to this answer.
Use the actual numbers from the facts in your reasoning."""
        
        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=400)
        
        # Parse into clean steps
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if line and not line.lower().startswith(('step', 'reasoning:')):
                # Remove numbering
                clean_line = re.sub(r'^[\d\.\-\)]+\s*', '', line)
                if clean_line:
                    steps.append(clean_line)
        
        return steps[:4]
    
    def validate_fact_consistency(self, facts: List[str], answer: str) -> bool:
        """
        Check if the answer can be derived from the facts.
        
        Args:
            facts: List of fact strings
            answer: The answer to validate
            
        Returns:
            True if answer is consistent with facts
        """
        # Extract all numbers from facts
        fact_numbers = []
        for fact in facts:
            numbers = re.findall(r'\$?([\d,]+(?:\.\d+)?)', fact)
            fact_numbers.extend([float(n.replace(',', '')) for n in numbers if n])
        
        if not fact_numbers:
            return True  # Can't validate without numbers
        
        # Extract number from answer
        answer_match = re.search(r'\$?([\d,]+(?:\.\d+)?)', answer)
        if not answer_match:
            return True  # Non-numeric answer
        
        answer_num = float(answer_match.group(1).replace(',', ''))
        
        # Check if answer appears in facts
        if answer_num in fact_numbers:
            return True
        
        # Check common calculations
        for num in fact_numbers:
            # Common deduction percentages
            for percentage in [0.5, 0.3, 0.6, 1.0]:
                if abs(num * percentage - answer_num) < 1:
                    return True
            
            # Check division (for percentages)
            for denom in fact_numbers:
                if denom > 0:
                    result = (num / denom) * 100
                    if abs(result - answer_num) < 0.1:
                        return True
        
        return False


# Fallback mock client for testing without API key
class MockGroqClient:
    """Mock client for testing without API access."""
    
    def __init__(self, *args, **kwargs):
        print("Using mock client (no API key provided)")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        return "Mock response for: " + prompt[:50]
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        return "Mock response"
    
    def generate_tax_facts_with_answer(self, scenario_type: str, context: str = "") -> Dict[str, Any]:
        return {
            "facts": [
                f"Company spent $500 on {scenario_type}",
                "50% of expense is deductible",
                "Company can deduct $250",
                "Expense was ordinary and necessary",
                "Documentation was properly maintained"
            ],
            "embedded_answer": "$250"
        }
    
    def generate_dynamic_answer(self, scenario_type: str, facts: List[str], 
                              narrative: str, question: str) -> str:
        return "$250"
    
    def generate_tax_narrative(self, scenario_type: str, facts: List[str]) -> str:
        return f"A company engaged in {scenario_type}. " + " ".join(facts[:2])
    
    def generate_reasoning_steps(self, scenario_type: str, facts: List[str], 
                               question: str, answer: str) -> List[str]:
        return [
            "Identified the expense amount from facts",
            "Applied the deduction percentage",
            "Calculated the final deduction",
            f"Result is {answer}"
        ]
    
    def validate_fact_consistency(self, facts: List[str], answer: str) -> bool:
        return True


def get_client(api_key: Optional[str] = None) -> Any:
    """
    Get appropriate client based on API key availability.
    
    Returns:
        GroqClient if API key available, MockGroqClient otherwise
    """
    api_key = api_key or os.getenv("GROQ_API_KEY")
    if api_key:
        return GroqClient(api_key)
    else:
        return MockGroqClient()