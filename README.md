# Python Code Review Exercise

## Overview
This exercise contains a working Python script (`user_processor.py`) that processes user data from a CSV file and generates reports. However, the code contains multiple anti-patterns and bad practices that need to be identified and fixed.

## Instructions
1. Review the `user_processor.py` file
2. Identify as many anti-patterns and code quality issues as possible
3. Refactor the code to follow Python best practices
4. **Run the test suite to ensure your refactored code works correctly**
5. Document the changes you made and why

## Running the Tests

A comprehensive test suite is provided in `test_user_processor.py`. These tests define the expected behavior and **MUST NOT be modified** (except for one intentionally broken test - see below).

### Setup

Choose your preferred setup method:

#### Option 1: Legacy pip (system python / requirements.txt)

```bash
# Install dependencies (if any are needed)
pip install -r requirements.txt

# Run all tests
python -m unittest test_user_processor -v

# Run with coverage
python -m coverage run -m unittest test_user_processor
python -m coverage report -m
```

#### Option 2: Modern uv (we're not barbarians)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. Install it first:

```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

Then set up and run tests:

```bash
# Install dependencies (creates .venv automatically)
uv sync --all-extras

# Run all tests
uv run python -m unittest test_user_processor -v

# Run with coverage
uv run coverage run -m unittest test_user_processor
uv run coverage report -m
```

### Understanding the Test Structure

The test suite imports the expected API that your refactored code should implement:

```python
from user_processor import (
    read_users_from_csv,
    calculate_user_score,
    process_users,
    generate_report,
    export_json,
    ScoringConfig,
    UserDataError
)
```

**Skeleton functions provided:**
- At the bottom of `user_processor.py`, you'll find skeleton implementations with `NotImplementedError`
- These include function signatures to guide your refactoring:
  - `read_users_from_csv(filepath: str = 'users.csv') -> list`
  - `calculate_user_score(purchases: str, visits: str, config: ScoringConfig = None) -> int`
  - `ScoringConfig` class for configuring score calculation weights
  - `UserDataError` exception for data validation errors
- Replace these skeletons with proper implementations as you refactor
- The tests will fail with `NotImplementedError` until you implement the functions properly

### Test Requirements
- All tests must pass (except the skipped one)
- Your refactored code must be importable and have the correct function signatures
- There is **one skipped test** (`test_generate_report_writes_correctly`) that is intentionally broken
  - The code behavior is **correct**
  - The test is **broken**
  - **Bonus challenge**: Fix the test and unskip it

### Success Criteria
✅ All non-skipped tests pass
✅ Code is well-structured and follows best practices
✅ You can explain the issues you fixed
✅ (Bonus) You identified and fixed the broken test

## The Task
The script currently:
- Reads user data from `users.csv`
- Filters users over 18 with a score above a threshold
- Generates a text report with user scores
- Exports filtered data to JSON

Your refactored code should maintain this functionality while fixing the issues.
