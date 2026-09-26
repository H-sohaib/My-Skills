# Language Coding Conventions

Detailed language-specific conventions and code review standards extracted from Ostorlab's autonomous review system (`pr_review_agent`).

---

## Python Conventions

### 1. Imports
- **Top-Level Imports Only**: All imports must ALWAYS be located at the top of the file. Local imports inside functions, methods, or conditional blocks are strictly prohibited (the only rare exception is resolving unavoidable circular dependencies that cannot be refactored away).
- **Import Grouping**: Group imports into three distinct blocks separated by a blank line:
  1. Standard library imports
  2. Third-party imports
  3. Local/first-party project imports
- **One Line Per Symbol**: Each imported symbol must be on its own line. Never group imports from the same module on a single line:
  ```python
  # Correct
  from module import function_a
  from module import function_b

  # Incorrect
  from module import function_a, function_b
  from module import (
      function_a,
      function_b,
  )
  ```
- **No Relative Imports**: Always use absolute package imports. Never use relative imports:
  ```python
  # Correct
  from my_package.services import worker

  # Incorrect
  from .services import worker
  from ..worker import do_work
  ```
- **No Direct Class Imports (Except Typing)**: Never import classes directly into the module namespace, except when used strictly for type annotations. Instead, import the module and access the class via the module namespace:
  ```python
  # Correct (at runtime)
  from my_package import models
  user = models.User()

  # Correct (typing only)
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from my_package.models import User

  # Incorrect (direct class import for runtime instantiation)
  from my_package.models import User
  user = User()
  ```
- **No Wildcard Imports**: Never use `from module import *`.

### 2. Exceptions & Error Handling
- **Exception Hierarchy**: Each library, package, or tool must define a top-level `Error` class inheriting directly from `Exception`. All specialized domain exceptions must inherit from that top-level `Error`:
  ```python
  class Error(Exception):
      """Base error for this package."""

  class UserNotFoundError(Error):
      """Raised when user does not exist."""
  ```
- **MCP Tool Handlers**: Top-level `except Exception:` blocks in Model Context Protocol (MCP) tool handlers are permitted and encouraged when logging the exception and returning a sanitized, user-friendly error string. This prevents unhandled tracebacks from leaking internal system state to LLM clients.
- **Zero Generic `Exception` in Teardown/Cleanup**: Never catch generic `Exception` inside `finally:`, `__del__:`, or background cleanup blocks on the grounds of "defensive teardown". Generic catches silently mask programming bugs, typos, and syntax errors in the cleanup logic itself. Always catch specific operational exceptions (e.g., `(OSError, requests.RequestException)`).
- **Domain Exception Hierarchy Tracing**: Trace domain exception subclasses across the codebase (e.g., `RepositoryWorkspaceError` subclassing `RuntimeError`). Never assume standard library `OSError` covers domain path or workspace resolution errors.
- **Flat Exception Handling Without `isinstance` Branching**: Never catch multiple exception types into a tuple only to immediately branch on `isinstance(e, ...)` inside the `except` block. Use clean, distinct, flat `except TypeA:` and `except TypeB:` clauses. Python's runtime already performs exception type dispatch natively and efficiently:
  ```python
  # BAD
  except (UsageLimitExceeded, UsageLimitExceededError) as e:
      if isinstance(e, UsageLimitExceededError):
          raise
      raise UsageLimitExceededError from e

  # GOOD
  except UsageLimitExceededError:
      raise
  except UsageLimitExceeded as e:
      raise UsageLimitExceededError from e
  ```

### 3. Conditions & Truthiness
- **Explicit Condition Checks**: Avoid relying on implicit truthiness. Make comparisons explicit:
  ```python
  # Correct
  if item is None:
  if item is not None:
  if is_valid is True:
  if len(items) > 0:
  if len(items) == 0:

  # Incorrect
  if not item:
  if is_valid:
  if items:
  ```

### 4. Tests & Testing Integrity
- **Test File Location**: Every source file (`path/to/module.py`) must have a corresponding test file under `tests/` (`tests/path/to/module_test.py`).
- **Pytest Naming Convention**: Tests must follow the naming pattern:
  `testAction_conditionCamelCase_expectedResult`
  ```python
  def testCalculateDiscount_whenUserIsVip_appliesTwentyPercent():
      ...
  ```
- **No Over-Mocking & No Useless Unit Tests**:
  - **Never Mock the System Under Test**: Never mock the class, function, or module that is being tested.
  - **Avoid Useless Mock Tests**: Flag tests that mock external dependencies and only assert that the mock was called with certain arguments or returned a mocked value, without exercising any real production business logic.
  - **Prefer Real Concrete Objects**: Prefer real data structures, real instances, and integration tests over mock objects whenever feasible. Mocks should strictly be reserved for out-of-process boundaries (network requests, third-party APIs, disk I/O when unavoidable).
  - **Mock Contract Symmetry (Types & Signatures)**: In unit tests using test doubles, mocks, or fakes, ensure that every replacement callable or side-effect function (`record_*`, `fake_*`) strictly matches the parameter types and return type annotations of the real method being mocked (`sync_delta() -> list[pathlib.Path]`, NOT `list[str]`).
  - **Orchestrator Wiring Integration Tests**: For base class orchestrators wiring new subsystems or collaborators into their core execution lifecycle (e.g. `ExecutorAgent`), testing only mock call order (`["snapshot", "execute", "sync_delta"]`) is insufficient. Require at least one concrete integration test that runs the orchestrator with real collaborators producing actual artifacts to verify end-to-end data flow.
  - **Deep Deletion Audit**: When tests or code are deleted under the claim of being "obsolete", verify that deleted tests do not remove the sole coverage for fallback branches, legacy paths, or error handling that remain active in production code.
- **No Testing of Private Methods**: Avoid writing dedicated tests or mocking private methods (functions/methods prefixed with `_`). Test their behavior through the public contract.

### 5. Architectural Cleanliness
- **No Unnecessary Wrapper Functions**: Avoid functions that only call another function without adding logic, validation, error handling, or transforming data.
- **Django Model Relationships**: NEVER use `hasattr()` to check for related models, ForeignKey, or OneToOne relationships. `hasattr()` swallows unexpected exceptions and can trigger silent, expensive database queries. Always use `getattr(model, 'relation', None)` or an explicit `try...except RelatedObjectDoesNotExist:`.
- **API Classification Files**: Ostorlab backend services use explicit file partitioning for API endpoints:
  - `public.py`: Non-authenticated access.
  - `authenticated.py`: Authenticated access (MUST enforce authorization).
  - `robot.py`: Privileged internal system communication.
- **Zero Private/Underscored Attribute Tampering Across Library Boundaries**: Never mutate or read private underscored attributes (e.g. `obj._state.usage = ...`) of third-party libraries or external modules. Always leverage public parameters (e.g. `Agent.run(..., usage=initial_usage)`), public methods, or immutable constructors.
- **Base Class Polymorphism Over Orchestrator Type Branching**: Avoid building external runner wrappers, loops, or dispatch functions that inspect object types with `isinstance(agent, ...)`. Encapsulate execution lifecycles, warning thresholds, and rescue strategies directly on domain base classes (e.g. `AIAgent.run()`) so all subclasses and consumers inherit the behavior uniformly without glue code.
- **Line Length**: There is no hard maximum line length restriction; prefer readability over artificial line wrapping.

### 6. Autonomous Security Agents & Budget Parity
All autonomous agent runs across Ostorlab's security agent repositories (`agent_auto_exploit`, `agent_threat_intelligence`, `agent_threat_intelligence_stream`) must implement the bounded budget and rescue run pattern:
- **Upper Request Bound**: Default exploration requests must be explicitly bounded (standard default: 500 requests).
- **Dynamic Horizon Warning**: When `agent_run.usage.requests >= request_limit - 2`, enqueue an urgent wind-down warning (`HORIZON_WARNING_PROMPT`) via native message queuing to instruct the model to wrap up tool calls and formulate its final answer.
- **Tool-Free Rescue Pass**: On `UsageLimitExceeded`, execute a tool-free rescue agent pass initialized with the accumulated context and usage (`usage=initial_usage`) to extract structured findings without infinite loops.
- **Tenacity Retry Suppression**: Never convert `UsageLimitExceeded` into a retryable `AgentRunError`. Exhausting a tool budget is an expected boundary condition; retrying it causes exponential turn explosions.
- **Agent Prompt & Behavioral Contract Parity**: System prompts and tool docstrings are operational specifications for LLM reasoning. When prompts contain universal or absolute claims (*"every file"*, *"always persists"*, *"tracks all changes"*), verify them against the actual code constraints (size limits like `MAX_SYNC_BYTES = 5MB`, excluded directories like `site-packages` or `__pycache__`, transport restrictions like UTF-8 GraphQL String vs raw binary). Unqualified prompt promises lead to agent hallucinations and task execution failures.

---

## TypeScript & JavaScript Conventions

### 1. Variables & Exports
- **No `var`**: Always use `const` by default. Use `let` only when variable reassignment is required.
- **Named Exports**: Avoid default exports (`export default ...`). Always use named exports (`export const ...`, `export function ...`) for better refactorability and searchability.
- **Strict Equality**: Always use `===` and `!==` instead of loose equality `==` and `!=`.

### 2. Typing & Null Safety (TypeScript)
- **Explicit Null & Undefined Checks**: Check explicitly for `null`, `undefined`, or empty string rather than relying on falsy coercion:
  ```typescript
  // Correct
  if (value !== null && value !== undefined) { ... }

  // Incorrect
  if (value) { ... }
  ```
- **Interfaces Over Type Aliases**: Prefer `interface` for defining object shapes; reserve `type` for unions, primitives, and mapped types.
- **Avoid Enums**: Avoid TypeScript `enum`. Use union types of string literals instead:
  ```typescript
  // Correct
  type Status = 'pending' | 'active' | 'completed';

  // Incorrect
  enum Status {
    Pending = 'PENDING',
    Active = 'ACTIVE',
  }
  ```
- **Avoid `any`**: Disallow `any`. Use `unknown` combined with type narrowing or type guards.
- **Strict Null Checks**: Ensure strict null checks are respected; do not bypass type checking with unnecessary non-null assertions (`!`).

### 3. Localization & Strings
- **i18n Placeholders**: Always use internationalization (i18n) translation helpers for user-facing text. Never hardcode English strings directly in UI components or templates.

### 4. Tests
- Apply the same anti-mocking standards: never mock the unit under test, avoid testing mock wiring without real business logic, and prefer concrete objects.

---

## Vue Conventions

### 1. Component Architecture & Script
- **Component Naming**: Use PascalCase for component filenames and template usage (`<NotificationBanner />` instead of `<notification-banner>`).
- **Script Null Safety**: Inside `<script setup>` or `<script>`, enforce explicit null and undefined checks (`value !== null && value !== undefined`).
- **Template Directives Exception**: Inside `<template>` directive expressions (e.g., `v-if="isLoading"`), idiomatic Vue truthiness checks are accepted and standard.

### 2. Component Testing Scope
- Only recommend component-mounting tests (`@vue/test-utils`, `mount()`) if the repository already has an active component-test harness configured in `package.json`. If no component test harness is present, focus test recommendations on unit/composable logic.

---

## Markdown (.md) Marketing & Content Conventions

### 1. Marketing & Content Review Separation (File-Based Routing)
- **Zero Software Engineering Rules on Markdown**: Markdown (`.md`) files represent product marketing, technical documentation, public announcements, and articles. Never apply software engineering, programming, or code-testing rules to `.md` files:
  - Do NOT comment on or request unit tests, mock coverage, test harnesses, or CI pipelines for documentation changes.
  - Do NOT comment on unhandled exceptions, error hierarchies, or type hinting on markdown content.
  - Do NOT comment on top-level imports, module structures, variable naming, or snake_case conventions on markdown files.
  - Focus 100% of review attention on editorial clarity, technical accuracy, reader experience, anti-slop standards, narrative flow, and Answer Engine Optimization (AEO/GEO).

### 2. Anti-Slop Discipline & Banned Buzzwords (Zero Tolerance)
- **Purge AI Boilerplate Openings**: Strip generic throat-clearing openings (*"In today's fast-paced digital landscape..."*, *"In the modern era of cybersecurity..."*, *"It is worth noting that..."*). Start *in media res* with actual operational friction, technical stakes, or direct payoff.
- **Purge Empty Filler Transitions**: Eliminate robotic filler transitions (*"Furthermore"*, *"Moreover"*, *"At its core"*, *"In conclusion"*, *"Let's unpack"*). Use mechanical, causal transitions that move the technical narrative forward.
- **Banned AI & Corporate Buzzwords**: Flag and eliminate generic buzzwords:
  `delve`, `dive into`, `testament`, `revolutionize`, `game-changing`, `transformative`, `seamlessly`, `frictionless`, `robust`, `unlock`, `supercharge`, `empower`, `synergy`, `leverage`, `tapestry`, `beacon`, `pivotal`.
  Replace them with mechanical active verbs, concrete architectural details, and measurable outcomes.

### 3. Authentic Engineering Voice (Stripe / Fly.io / Cloudflare Standard)
- **Peer-to-Peer Tone**: Speak as a senior systems engineer explaining a hard-won lesson over coffee—pragmatic, precise, slightly understated, and brutally honest about architectural trade-offs, limitations, and edge cases rather than promising effortless magic.
- **Show Mechanics & Physics Over Assertions**: Never allow unbacked claims like "lightning-fast", "bulletproof", or "highly scalable". Demand concrete metrics and evidence: flame graphs, query plans, packet captures, P99 latency benchmarks, memory allocations, or reproducible curl requests.

### 4. Storytelling Architecture (Invert the Pyramid)
- **Act I: Upfront Payoff & Hook**: Reveal the crowning payoff, exploit proof, core thesis, or punchline in the opening paragraph (first 40–60 words). Never bury the lead behind a lengthy background preamble.
- **Act II: Conflict & Breakdown**: Explain why the existing status quo, standard tools, or previous architectures failed under real-world conditions.
- **Act III: Step-by-Step Evidence Chain**: Provide granular technical deconstruction with real data schemas, concrete code diffs, and exact API payloads.
- **Act IV: Frictionless Technical On-Ramp**: Provide concrete, runnable commands (CLI flags, curl snippets, minimal configuration blocks) so the reader can reproduce or adopt the solution immediately.
- **Anti-"Harbor Tour" Rule**: Flag and reject sequential walkthroughs of UI menus, setting tabs, and button clicks (e.g., *"Click Settings, then click Integrations, then click Add"*). Reframe into a problem-and-solution narrative driven by technical goals.

### 5. Answer Engine Optimization (AEO & GEO Standards)
- **Passage-Level Direct Answer**: The first 40–60 words directly beneath each major heading (H2/H3) must provide a direct, extractable answer to the question implied by the heading.
- **Query-Framed Headers**: Structure headings as natural search queries or clear technical statements (e.g., *"How does autonomous API discovery work?"* instead of *"Overview"*).
- **Objective Entity Headings in Comparisons**: In comparison sections, use objective headings (`### Tool Name` followed by `**Focus:** ...`) rather than subjective marketing labels (avoid `### Best for Enterprise`).
- **Extractable Definition Anchors**: Format core definitions prominently using bold anchors (e.g., `**[Concept]** is...`) alongside structured comparison tables and checklists.
- **Stand-Alone Modularity**: Each section must function as an independent, modular knowledge unit without relying on backward-referencing filler (*"As mentioned above"*, *"As previously stated"*).
- **Entity Reality**: Replace generic placeholder domains (`foo.com`, `example.org`) with realistic enterprise architectures, realistic headers, and realistic payload schemas.

