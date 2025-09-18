# MuSR-SynTax: Synthetic Tax Law Reasoning Data Generator

## Overview
MuSR-SynTax is a Python module for generating synthetic tax law reasoning cases using generative AI. Inspired by the MuSR paper ("Testing the Limits of Chain-of-thought with Multistep Soft Reasoning"), it enables the creation, evaluation, and extension of complex tax law scenarios for GenAI research and benchmarking.

## Features
- Fully dynamic domain and case generation from JSON templates
- Modular, extensible architecture (add new domains or LLMs easily)
- Clear data structures for facts, cases, and domains
- LLM-agnostic client (swap Groq, OpenAI, etc.)
- Built-in validation and reasoning pattern enforcement

## Quickstart
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up your LLM API key:**
   - Create a `.env` file with `GROQ_API_KEY=your_key_here`
3. **Generate cases:**
   ```bash
   python main/generate_case.py
   ```
4. **Add new domains:**
   - Edit `data/templates/tax_domains.json` (see examples inside)

## Repository Structure
- `src/core.py`           — Data structures for facts and cases
- `src/tax_domains.py`    — Domain template management
- `src/llm_client.py`     — LLM interaction and prompt engineering
- `src/tax_generator.py`  — Orchestrates case generation
- `data/templates/`       — Domain templates (JSON)
- `data/generated/`       — Output cases
- `tests/`                — Unit and integration tests

## Extending the System
- **Add a new domain:**
  1. Add a new entry to `tax_domains.json` with required fields.
  2. (Optional) Add new fact templates or reasoning patterns.
- **Switch LLM provider:**
  - Implement a new client in `src/llm_client.py` and update usage in `tax_generator.py`.
- **Customize prompts or validation:**
  - Edit prompt templates in `llm_client.py` or add new validation logic in `core.py`.

## Contributing
See `CONTRIBUTING.md` for guidelines on adding domains, LLMs, or evaluation logic.

## License
MIT License

---
For more details, see the MuSR paper and the code comments/docstrings throughout the repository.
