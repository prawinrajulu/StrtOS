# Contributing to StrtOS

Thank you for your interest in contributing to **StrtOS**!

## Development Guidelines

1. **Fork & Branch**: Create a feature branch off `main` (`git checkout -b feature/my-feature`).
2. **Code Standards**:
   - Python: Follow PEP 8, use Pydantic v2 schemas, and ensure strict type annotations.
   - Frontend: Use React 19, TypeScript, and adhere to the locked StrtOS dark visual design system.
3. **Specialist Agents**:
   - New specialist agents must inherit from `SpecialistAgentInterface` and register via `register_specialist_agent()`.
   - Never break the CEO Agent orchestrator delegation contract.
4. **Testing**: Add unit tests in `backend/app/tests/` for all new agent validators and services before opening a PR.
