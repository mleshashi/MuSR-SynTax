# Contributing to MuSR-SynTax

Thank you for your interest in improving MuSR-SynTax! This guide will help you contribute effectively.

## How to Contribute

### 1. Add a New Tax Domain
- Edit `data/templates/tax_domains.json`.
- Add a new entry with:
  - `domain_name`, `description`, `typical_questions`, `reasoning_pattern`, `required_facts`, `tax_rules`.
  - (Optional) `answer_pattern`, `fact_templates`.
- Run `python main/generate_case.py` to test your new domain.

### 2. Add or Update LLM Providers
- Implement a new client in `src/llm_client.py`.
- Update `src/tax_generator.py` to use your client.
- Document any new environment variables in the README.

### 3. Improve Prompts or Validation
- Edit prompt templates in `src/llm_client.py`.
- Add or update validation logic in `src/core.py` or `src/schemas.py`.

### 4. Add Tests
- Place new tests in `tests/`.
- Cover new domains, LLM output parsing, and edge cases.

### 5. Code Style
- Use `black` for formatting and `flake8` for linting.
- Type annotations are encouraged.

## Pull Request Checklist
- [ ] All tests pass
- [ ] New/updated code is documented
- [ ] README and/or schema files updated if needed
- [ ] No unrelated changes in the PR

## Questions?
Open an issue or discussion on GitHub!
