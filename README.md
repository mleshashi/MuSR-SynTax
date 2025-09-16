# MuSR-SynTax: Synthetic Tax Law Data Generator

A Python module for generating synthetic tax law reasoning cases based on the MuSR (Multistep Soft Reasoning) framework.

## Features

- Generate complex tax law scenarios with step-by-step reasoning
- Support for multiple tax domains (deductions, liability, compliance)
- Flexible LLM integration (OpenAI, Anthropic)
- Easy-to-use API with clear data structures

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Generate your first case:
```python
from src.core import TaxCase
from src.tax_generator import TaxGenerator

generator = TaxGenerator()
case = generator.generate_case("business_deduction")
case.display()
```

## Repository Structure

```
MuSR-SynTax/
├── src/                    # Main source code
├── examples/               # Usage examples
├── data/                   # Templates and generated data
├── tests/                  # Test suite
└── config/                 # Configuration files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
