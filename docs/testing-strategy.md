# YINI Test Suite — Coverage and Quality Plan

This document describes the testing strategy, coverage priorities, and quality principles for the entire yini-test-suite project.

## Purpose

The purpose of `yini-test-suite` is to verify that YINI parser implementations behave consistently and conform to the YINI specification.

The suite should prioritize **test quality, specification coverage, and meaningful edge cases** over simply increasing the number of test cases.

A smaller collection of carefully designed tests covering the specification is more valuable than a large collection containing redundant cases or leaving important behaviors untested.

## Test Coverage Priorities

The test suite should focus on the following areas:

### 1. Valid Inputs

Verify that valid YINI documents are accepted and produce the expected parsed results.

Cover supported syntax and value types, including strings, numbers, booleans, null, lists, inline objects, sections, and nested sections.

Tests should verify both the resulting values and their hierarchy.

### 2. Invalid Inputs

Verify that invalid YINI documents are correctly rejected.

Tests should cover malformed syntax, invalid values, unsupported constructs, and violations of specification rules.

The goal is not merely to confirm that a parser can process valid input, but also that it reliably rejects invalid input.

### 3. Strict and Lenient Modes

Test strict and lenient parsing separately, including cases where the same input is expected to behave differently.

Verify that:

- Strict mode enforces its additional requirements.
- Lenient mode accepts only the exceptions explicitly permitted by the specification.
- Mode declarations are handled correctly.
- Differences in validation and diagnostics match the specification.

### 4. Boundary and Edge Cases

Include tests for boundary conditions and less common but valid or invalid inputs.

Important areas include:

- Section nesting limits and hierarchy transitions.
- Duplicate keys and section declarations.
- Missing or empty values.
- String delimiters, escapes, and multiline content.
- Numeric formats, ranges, and invalid representations.
- Unicode and unusual character combinations.
- Whitespace, indentation, comments, and line endings.

Boundary tests should focus on behavior that could reasonably differ between parser implementations.

### 5. Diagnostics

Where the specification defines diagnostic behavior, verify that parsers report the expected errors and warnings.

Particular attention should be given to:

- Duplicate declarations and first-wins behavior, where applicable.
- Deprecated syntax and features.
- Strict and lenient mode violations.
- Invalid nesting or structural rules.
- Other cases where the specification distinguishes warnings from errors.

Diagnostics should be tested consistently without requiring unnecessarily identical human-readable error messages across implementations.

### 6. Regression Tests

When a parser bug, specification ambiguity, or previously untested edge case is discovered, consider adding a corresponding regression test.

Regression tests should help prevent known issues from reappearing and improve consistency across parser implementations.

Tests should reflect the intended specification behavior rather than implementation-specific quirks.

## Test Organization

Maintain the distinction between **smoke tests** and **golden tests**.

### Smoke Tests

Smoke tests provide a small, representative collection of cases for quickly checking parser compatibility.

They should:

- Cover fundamental YINI syntax and value types.
- Include representative valid and invalid inputs.
- Exercise important strict and lenient behaviors.
- Be fast and straightforward to run during development and CI.

Smoke tests are intended as an initial compatibility check, not as proof of complete specification conformance.

### Golden Tests

Golden tests provide more comprehensive verification of parser behavior against the specification.

They should:

- Cover normative specification requirements.
- Verify expected parsed structures and values.
- Include valid, invalid, boundary, and edge cases.
- Exercise differences between strict and lenient modes.
- Include diagnostic expectations where applicable.
- Serve as the primary shared conformance test collection.

Golden tests should be independent of any particular parser implementation.

## Test Quality Over Quantity

The number of test cases should not be treated as the primary measure of test-suite quality.

Instead, the main question should be:

**How thoroughly does the test suite cover the requirements and expected behavior defined by the YINI specification?**

A single feature may require several tests to cover:

- Normal valid usage.
- Invalid usage.
- Strict-mode behavior.
- Lenient-mode behavior.
- Boundary conditions.
- Interactions with other features.

However, additional cases should provide meaningful coverage rather than merely repeat behavior already tested.

Tests should be:

- **Focused:** Each case should have a clear purpose and expected outcome.
- **Deterministic:** The same input and mode should consistently produce the same expected result.
- **Specification-driven:** Expectations should follow the specification, not a particular implementation.
- **Independent:** Tests should avoid unnecessary dependencies on other tests.
- **Maintainable:** Test names, inputs, and expected results should be understandable and easy to review.
- **Relevant:** Each case should verify a meaningful requirement, boundary, or known regression.

## Coverage Tracking

Where practical, maintain a mapping between normative specification requirements and the test cases that verify them.

This can help identify:

- Requirements with no test coverage.
- Features covered only by valid-input tests.
- Missing strict or lenient mode coverage.
- Missing boundary or diagnostic cases.
- Redundant tests that add little additional value.

Coverage should be assessed by specification behavior, not only by code coverage or test count.

## Guiding Principle

**Prioritize meaningful specification coverage over test quantity.**

The test suite should grow as the specification evolves, as new edge cases are identified, and as parser implementations reveal potential inconsistencies.

The long-term goal is a reliable, maintainable, language-independent conformance suite that helps all YINI parser implementations produce consistent and predictable results.
