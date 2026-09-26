---
name: coding-style
description: Use whenever writing, modifying, refactoring, or extending code. Apply the repository's Python, typing, GraphQL, Graphene, and Django coding conventions before implementation and when changing legacy code.
---

# Coding Style and Conventions

Use this skill whenever the agent writes or changes code. Apply the general
rules first, then the language and framework rules that match the files being
changed. Preserve existing behavior unless the task explicitly requests a
behavior change.

## Universal implementation rules

- Prefer the smallest direct change that solves the requirement.
- Keep each module, class, and function focused on one responsibility.
- Preserve public contracts unless the task explicitly changes them.
- Use explicit types, names, conditions, and error paths rather than implicit
  behavior or dynamic reflection.
- Keep security checks at the trust boundary and make authorization decisions
  observable and testable.
- Add or update tests for changed behavior, edge cases, and failure paths.
- Do not introduce speculative abstractions, duplicated APIs, or framework
  workarounds without a demonstrated need.

## Python conventions

### Imports and module structure

- Put imports at module scope. Local imports are allowed only when required to
  break an unavoidable circular dependency.
- Use absolute imports, never relative imports.
- Import one symbol per line and group imports in this order: standard
  library, third-party, then first-party modules.
- Do not use wildcard imports.
- Add `from __future__ import annotations` when the project supports it.
- For runtime class usage, import the module and use `module.ClassName`.
  Direct class imports are reserved for type-only usage when that convention
  is required by the project.

### Explicit logic and type safety

- Use explicit checks for optional values: `value is None` or
  `value is not None`.
- Use explicit boolean checks when a value is required to be a boolean.
- For collections, use an intentional emptiness check such as
  `len(items) > 0` when the repository convention requires it.
- Use `isinstance()` for type checks; do not compare types directly.
- Prefer built-in generics such as `list[str]`, `dict[str, int]`, and
  `tuple[int, ...]`.
- Prefer `X | Y` and `T | None` over `Union` and `Optional`.
- Use abstract collection types such as `Sequence` and `Mapping` for inputs;
  use concrete collection types for returned values when appropriate.
- Use `Protocol` and `@runtime_checkable` for structural interfaces and
  `TypeIs` or `TypeGuard` for safe narrowing of dynamic values.
- Annotate every parameter, return value, and class or instance attribute that
  can be determined. Use `-> None` for procedures.
- Prefer specific types over `Any`; use `Any` only where the design is truly
  dynamic or the boundary cannot provide more information.

### Dynamic attribute access

Do not introduce or preserve `getattr()` or `hasattr()` as a substitute for
missing type information. Use one of these alternatives:

1. Add the field to the model or dataclass.
2. Define a `Protocol` or abstract interface.
3. Narrow the type with `isinstance()`.
4. Use `typing.cast()` only at a genuine external-library boundary.

### Async, data modeling, and control flow

- Prefer `asyncio.TaskGroup` for related concurrent tasks.
- Use `asyncio.timeout()` for async timeouts.
- Never perform blocking CPU or synchronous I/O work directly in an async
  event loop; offload it to a thread or process pool.
- Handle exception groups with targeted `except*` clauses.
- Use `dataclass(slots=True)` when memory layout and attribute discipline
  benefit from it; add `frozen=True` and `kw_only=True` when the data model is
  immutable and keyword clarity is useful.
- Move helpers that do not use `self` outside the class as private module-level
  functions.
- Use structural pattern matching when it makes typed payload dispatch clearer.

### Exceptions and tests

- Define module or package exception hierarchies for domain errors.
- Catch the narrowest operational exception that can be handled. Do not use a
  broad `except Exception` to hide programming errors.
- Keep tests behavior-focused and tied to real persistence and public APIs.
- Prefer real database models for database behavior instead of mocks that
  bypass persistence, authorization, or relations.
- Test happy paths, validation failures, edge cases, security boundaries, and
  every changed branch.
- Avoid tautological assertions and mocks whose signatures do not match the
  real callable.
- Follow the repository's established test naming and file-matching
  conventions.

## GraphQL, Graphene, and Django conventions

### Schema and naming

- Prefer list-based root queries with ID filters over duplicate single-object
  root queries.
- Name ID arguments with the entity, such as `scanId`, `assetId`, or
  `vulnerabilityId`; declare them as `scan_id`, `asset_id`, and
  `vulnerability_id` in Python.
- Use `PascalCase` for object, input, payload, and enum types.
- Use `camelCase` for GraphQL fields, arguments, and mutations; Graphene's
  snake-case declarations provide the conversion.
- Use `SCREAMING_SNAKE_CASE` for enum values.
- Resolve related objects through fields on their parent type rather than
  adding disconnected root queries.

### Nullability and mutations

- Make required input fields non-null so invalid requests fail at validation.
- Keep secondary or integration-backed output fields nullable so partial
  failures do not nullify an entire response tree.
- Keep IDs and core system identifiers non-null.
- Use `graphene.relay.ClientIDMutation` with one structured input object and a
  predictable payload.
- Prefer intent-driven mutations such as `AssignTicket` or
  `ChangeTicketSeverity` over generic CRUD mutations with large property bags.
- Return structured user errors with field, message, and machine-readable code
  where the API uses that pattern.

### Pagination and resolver performance

- Use Relay connection pagination for lists and relationships.
- Use opaque cursors based on stable sort keys; do not expose raw database IDs
  as cursors or use offset pagination for large tables.
- Instantiate DataLoaders per request, never as global singletons.
- Use `select_related` and `prefetch_related` based on the requested fields and
  avoid filtering prefetched relations in child resolvers in a way that causes
  N+1 queries.
- Keep types as graph navigators; enforce tenant and authorization checks at
  query and mutation trust boundaries.

### Security and resilience

- Scope every organisation-owned query, resolver, and mutation to the active
  organisation.
- Validate relational IDs against the active organisation before attaching
  them to an object.
- Apply authorization at the query and mutation layer and preserve object-level
  access rules for users and API keys.
- Apply query depth, complexity, and introspection controls appropriate to the
  deployment.
- Model expected domain failures explicitly and keep unexpected exceptions
  observable rather than silently converting them into success responses.
- Use safe schema deprecation and persisted-query or edge-caching controls
  without weakening authorization.

## Legacy Python typing mode

When adding types to existing Python code:

- Do not change business logic or control flow.
- Add parameter, return, attribute, optional, container, and union types that
  accurately reflect existing behavior.
- Preserve correct annotations, formatting, comments, and docstrings.
- Add `from __future__ import annotations` and only the required typing imports.
- Prefer explicit protocols, models, or casts at boundaries over dynamic
  reflection.
- Use `T | None`, built-in generics, and specific types instead of `Optional`,
  legacy `typing.List`, or unnecessary `Any`.

## Pre-completion checklist

Before declaring an implementation complete:

- Confirm naming, imports, types, and public API shape match the applicable
  conventions.
- Check authorization, tenant scoping, validation, nullability, and error
  paths.
- Check query count, async blocking, pagination, and resource behavior.
- Run focused tests and relevant broader checks.
- Review the final diff for unrelated changes and verify no behavior changed
  unintentionally.
