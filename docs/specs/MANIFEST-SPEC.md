# Manifest Specification

Version: 1.0

---

# Purpose

Defines the source of truth for project generation.

---

# Example

```yaml
project:
  name: claims-modernization

domain:
  insurance

backend:
  java21

frontend:
  react

cloud:
  aws

architecture:
  microservices

ai:
  langgraph

modernization:
  ibmi
```

---

# Required Sections

## Project

```yaml
project:
  name:
```

---

## Domain

```yaml
domain:
```

---

## Backend

```yaml
backend:
```

Supported:

- java21
- java25
- python

---

## Frontend

```yaml
frontend:
```

Supported:

- react
- angular
- none

---

## Cloud

```yaml
cloud:
```

Supported:

- aws
- azure
- gcp

---

## Architecture

```yaml
architecture:
```

Supported:

- monolith
- modular-monolith
- microservices
- event-driven
- serverless
- agentic

---

## AI

```yaml
ai:
```

Supported:

- none
- rag
- langgraph
- multi-agent

---

## Modernization

```yaml
modernization:
```

Supported:

- none
- ibmi
- cobol
- mainframe
