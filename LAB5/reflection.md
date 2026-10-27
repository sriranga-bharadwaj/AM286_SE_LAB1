# Reflection — Lab 5: Static Code Analysis

---

## Q1. What is the difference between static and dynamic code analysis? Give one advantage of each.

**Static analysis** examines source code *without executing it* — the tool reads the text of the program and applies rules to detect issues such as unused variables, security patterns, or style violations.  
**Dynamic analysis** runs the program and observes its behaviour at runtime — tools like profilers, fuzzers, or test coverage reporters fall into this category.

| | Static | Dynamic |
|-|--------|---------|
| Execution required? | No | Yes |
| Example | Pylint, Bandit, Flake8 | pytest-cov, Valgrind, AFL++ |
| **Advantage** | Catches bugs before a single line is executed; cheap to run in CI on every commit | Can detect runtime-only issues (e.g., memory leaks, race conditions, unexpected input handling) that no static tool can reason about |

---

## Q2. Which tool (Pylint, Flake8, or Bandit) flagged the most severe issue in this code? Describe the issue and why it is dangerous.

**Bandit** flagged the most severe issues. Two findings were rated **HIGH** severity:

1. **`eval(discount_expr)` — B307, CWE-78 (OS Command Injection / Code Injection)**  
   The function `calculateDiscountedTotal` accepted a raw string and passed it to `eval()`. An attacker who can influence `discount_expr` (e.g., via an API parameter or a compromised upstream call) could run arbitrary Python code on the server — reading files, spawning processes, or exfiltrating secrets.

2. **`os.system("echo Receipt saved to: " + filename)` — B605, CWE-78**  
   Concatenating a user-controlled `filename` into a shell command is a classic shell-injection vulnerability. On Unix, a filename like `; rm -rf /` would delete the filesystem.

Both issues stem from the same root cause: treating *data* as *executable code or shell commands* without sanitisation.

---

## Q3. Describe one fix you made and explain how it improves the code's security or quality.

**Fix: Replaced `eval()` with direct arithmetic.**

*Before:*
```python
def calculateDiscountedTotal(item_id, discount_expr):
    base_price = cart_items[item_id]["price"]
    final_amount = eval(discount_expr)   # e.g. "base_price * 0.90"
    return final_amount
```

*After:*
```python
def calculate_discounted_total(item_id, discount_rate):
    """Calculate the discounted price for an item."""
    base_price = CART_ITEMS[item_id]["price"]
    final_amount = base_price * discount_rate   # e.g. 0.90
    return final_amount
```

**Why it is better:**
- The function now accepts a `float` (e.g., `0.90`) instead of an arbitrary string, making the API explicit and type-safe.
- There is no longer any path by which an attacker can inject code.
- The logic is clearer and easier to unit-test — the output is deterministic given the same inputs.
- Pylint, Flake8, and Bandit all stopped reporting issues for this function after the change.

---

## Q4. Would you use these tools in a real project? Why or why not?

**Yes, absolutely — and ideally integrated into CI/CD rather than run manually.**

- **Pylint** is valuable for maintaining consistency across a team. A shared `.pylintrc` configuration enforces agreed-upon conventions automatically, reducing style debates in code review.
- **Flake8** is lightweight and extremely fast, making it ideal as a pre-commit hook to block obviously non-PEP-8 code before it ever reaches the repository.
- **Bandit** is essential for any code that handles user input, network traffic, or credentials. The issues it found in this lab — `eval`, `os.system`, MD5, `random` for secrets — are real bugs that appear frequently in production codebases, yet are easy to miss in manual review.

The main limitation is that these tools produce **false positives** and cannot reason about runtime behaviour. For a real project I would combine them with dynamic analysis (e.g., pytest with coverage, integration tests) and periodic manual security review. The tools do not replace understanding; they amplify it.
