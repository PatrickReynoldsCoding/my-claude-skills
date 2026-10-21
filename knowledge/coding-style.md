# Coding Style

## General — best practices & style (all languages)

**Extract logic into well-named helper functions before they get long.**
**Why:** Long functions are hard to test in isolation and obscure intent.
**How to apply:** If a block of logic inside a function has a clear purpose, pull it into a private helper with a name that says what it does.

**When refactoring a branch's diff, only touch code the branch actually added or changed — never pre-existing code the branch didn't touch, even in the same function.**
**Why:** Scope creep into untouched code mixes unrelated changes into the PR, makes the diff unreviewable/unattributable, and risks regressions in code nobody asked to change. It's also fine — expected, even — to find zero extraction-worthy blocks in a branch; don't manufacture extractions just to have something to show.
**How to apply:** Run `git diff <base>..<branch>` first and scope all extraction candidates to the actual diff hunks. If an extraction-worthy block sits right next to untouched code in the same function, leave the untouched part alone even if it looks improvable. If an extracted helper has only one call site, make it a local nested function rather than a class/object-level method; promote to object-level only when genuinely reused by multiple call sites in the same file.

**Separate orchestration from computation — callers own the wiring.**
**Why:** Functions that do their own data fetching/transformation AND computation are hard to unit-test.
**How to apply:** e.g. `get_retrieval_scores` takes `List[RetrievalData]`; the caller calls `get_retrieval_data` first. Each function does one thing.

**Separate pure computation from I/O — pure functions are testable and composable.**
**Why:** Pure functions (no side effects, deterministic inputs/outputs) are easier to test, reason about, and reuse. I/O is a separate concern.
**How to apply:** Extract pure logic (e.g., `_apply_sbt_version_to_lines()` takes lines, returns updated lines) from I/O wrappers (e.g., `update_sbt_version()` reads file, calls pure function, writes result).

**Never weaken a type with optional/nullable defaults to paper over missing test data — fix the test data instead.**
**Why:** Weakening a model's type to avoid updating a fixture hides a real design problem.
**How to apply:** If making a field required breaks tests, add the field to the test fixtures. The model should reflect reality.

**Replace if-elif/switch chains with lookup tables (maps/dicts).**
**Why:** Branch chains are verbose, error-prone to extend, and often have subtle bugs (e.g. string transformations applied before comparison).
**How to apply:** Module-level maps with descriptive names (e.g. `_ENV_SUFFIX_TO_DISPLAY_NAME`) replace chains cleanly.

**No single-character variable names — everything must be descriptive.**
**Why:** Code is read far more than written. `recorded_version` vs `candidate_version` is immediately clear; `a` vs `b` requires context-switching.
**How to apply:** Use semantic names that explain the variable's purpose. Loop indices where context is obvious (e.g., `for i in range(10)`) are acceptable; data variables always get full names.

**Comments should explain WHY, not WHAT — good names eliminate "what" comments.**
**Why:** Code that reads well doesn't need narration. Over-commenting reduces signal-to-noise and rots as code changes.
**How to apply:** Don't comment obvious code. Only comment when the decision is non-obvious (workarounds, hidden constraints, invariants, or surprising design choices).

**Use sealed error type hierarchies, not string messages.**
**Why:** Strings can't be pattern-matched exhaustively; a sealed hierarchy forces callers to handle every case and keeps error context structured.
**How to apply:** Define a sealed trait (or enum) as the root error type, with specific case classes for each failure mode carrying relevant fields (e.g. `MCPError(tool: String, message: String, cause: Option[Throwable])`). Wire errors through the type system, not exception messages.

**Separate service interface from implementation — callers depend on the trait, not the class.**
**Why:** Swapping implementations (for tests, different backends, staged rollouts) requires no call-site changes when the interface is stable.
**How to apply:** Define a trait for every service with the public contract. Put the implementation in a separate (often private) class. Expose a factory or layer in a companion object. Callers reference only the trait.

## Python

**Use plain for-loops, not list comprehensions, for multi-step logic.**
**Why:** List comprehensions that do non-trivial work read bottom-up; for-loops read top-down.
**How to apply:** Reserve comprehensions for simple transformations (e.g. `[x.id for x in items]`). Use a for-loop with named intermediate variables any time there are conditions, multiple steps, or an append.

**Use Pydantic models at system boundaries; don't do isinstance/dict-key guards inside business logic.**
**Why:** Defensive dict-access throughout the codebase hides schema issues and adds noise.
**How to apply:** Parse raw dicts into Pydantic models at the entry point (file load, API response). Internal functions work with typed models, not dicts.

## Scala / ZIO

**Service pattern: trait + private impl + companion object with `live: ZLayer`.**
**Why:** Decouples interface from construction; ZIO's DI is type-driven so the layer is the only wiring point.
**How to apply:**
```scala
trait MyService {
  def doThing(x: String): ZIO[Scope, MyError, Result]
}
object MyService {
  val live: ULayer[MyService] = ZLayer.succeed(new MyServiceImpl())
  def doThing(x: String): ZIO[MyService & Scope, MyError, Result] =
    ZIO.serviceWithZIO[MyService](_.doThing(x))
}
private class MyServiceImpl() extends MyService { ... }
```

**Use sealed trait / enum ADTs for all closed value sets.**
**Why:** The compiler enforces exhaustive pattern matching; adding a case surfaces every unhandled site immediately.
**How to apply:** `sealed trait Decision` with `case class`/`case object` subtypes for every variant. Use `enum` (Scala 3) when the cases are simple. Never use bare strings for values with a fixed set of options.

**Derive Circe codecs in companion objects — never inline.**
**Why:** Keeps the case class body clean; scoping in the companion makes implicits available everywhere the type is used.
**How to apply:**
```scala
case class QueryRequest(query: String, limit: Int)
object QueryRequest {
  implicit val decoder: Decoder[QueryRequest] = deriveDecoder
  implicit val encoder: Encoder[QueryRequest] = deriveEncoder
}
```
Use `Configuration.default.withSnakeCaseMemberNames` for API contracts where JSON uses snake_case.

**Thread ZIO dependency requirements through intersection types — never use global state.**
**Why:** The type signature documents every dependency; the compiler prevents missing wiring; no implicit globals.
**How to apply:** `ZIO[UserService & AuthService & Scope, AppError, Result]` — list every dependency in `R`. Compose layers in `Main` / `run`, not inside service implementations.

**Use `ZIO.attempt` for code that throws; `ZIO.succeed` for pure values; `ZIO.fromEither` for Either.**
**Why:** Correctly captures the effect boundary. Wrapping pure code in `attempt` is unnecessary overhead; missing `attempt` around throwing code leaks exceptions.
**How to apply:**
```scala
ZIO.attempt(parser.parse(body))          // may throw
ZIO.succeed(context.copy(done = true))   // pure
ZIO.fromEither(decode[Foo](json))        // circe Either
```

**Use for-comprehensions for sequential ZIO chains — not nested `.flatMap` calls.**
**Why:** For-comprehensions linearise async steps top-to-bottom; nested flatMap creates rightward drift and obscures the happy path.
**How to apply:** Any chain of more than two steps should be a for-comprehension with named bindings at each step.

**Use `foreachPar` for parallelism; `Semaphore` to cap concurrency; `Ref` for shared mutable state.**
**Why:** These are the ZIO primitives that compose cleanly with the effect system — no raw threads or `var`.
**How to apply:**
- `ZIO.foreachPar(items)(process)` — fan out
- `Semaphore.make(n).flatMap(sem => ZIO.foreachPar(items)(sem.withPermit(process(_))))` — capped fan out
- `Ref.make(initial).flatMap(ref => ...)` — safe mutable cell inside effects

**Make config errors fatal with `.orDie`; don't propagate `Config.Error` to callers.**
**Why:** Missing config is a startup problem, not a runtime one. Propagating it forces every caller to handle an error that can only be fixed by an operator.
**How to apply:** `ZIO.config[AppConfig](config).orDie` in the layer definition. App crashes at startup with a clear message rather than failing silently mid-request.

**Use type aliases to name complex types — especially ZIO environment intersections.**
**Why:** Long `ZIO[A & B & C & D, E, F]` signatures hurt readability and become a maintenance burden when the dependency set changes.
**How to apply:**
```scala
type SearchDeps = LLMClient & MCPClient & UserContextService & Scope
def search(...): ZIO[SearchDeps, AgentError, SearchResult]
```

**Use extension methods to add utility to ZIO effects without subclassing.**
**Why:** Keeps cross-cutting concerns (metrics, logging wrappers, error unwrapping) out of the core type hierarchy.
**How to apply:**
```scala
extension [R, E, A](zio: ZIO[R, E, A])
  def withTimer(metric: Metric): ZIO[R, E, A] = ...
```

## Bash

_(No rules captured yet.)_
