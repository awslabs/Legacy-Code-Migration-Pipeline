```markdown
# Migration Roadmap

## Phase 1
- Workpackage 1: [Flow ID] - [Entry Point] - [Business Domain]
- Workpackage 2: [Flow ID] - [Entry Point] - [Business Domain]
[...]

## Phase 2
- Workpackage X: [Flow ID] - [Entry Point] - [Business Domain]
- Workpackage Y: [Flow ID] - [Entry Point] - [Business Domain]
[...]

[Additional phases...]

## Dependency Graph
```mermaid
graph TD
  WP1[Workpackage 1] --> WP3[Workpackage 3]
  WP1 --> WP4[Workpackage 4]
  WP2[Workpackage 2] --> WP5[Workpackage 5]
  [...]
```