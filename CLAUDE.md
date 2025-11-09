# Claude Code Rules

## Python Standards

Use modern Python standards (Python 3.14+) including:

- **Structural pattern matching**: Use `match`/`case` statements for complex conditionals
- **Type statement**: Use `type` statement for type aliases (e.g., `type Vector = list[float]`)
- **Modern type hints**: Use PEP 604 union syntax (`X | Y` instead of `Union[X, Y]`), built-in generics (`list[str]` instead of `List[str]`)
- **PEP 695 syntax**: Use `def func[T](x: T) -> T:` for generic functions
- **Exception groups**: Use `except*` for handling exception groups when appropriate

## Quality Checks

After each prompt, run these commands to ensure code quality:

- Tests: `just test`
- Type checking: `just typecheck`
- Formatting: `just fmt`

All checks must pass before considering the task complete.
