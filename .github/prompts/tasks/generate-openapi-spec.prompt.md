---
mode: "ask"
description: "Generate an OpenAPI 3.0 YAML specification for a described REST interface"
---

## Objective

Generate a complete, valid OpenAPI 3.0 YAML specification for a described REST API. The spec must be ready to import into API management tools (Kong, Apigee, AWS API Gateway) and usable as a contract for consumer-driven contract testing.

---

## Instructions to Copilot

1. Use OpenAPI 3.0.3 format
2. Define `info` with title, version, and description
3. Define `servers` with at least a development URL placeholder
4. For each endpoint:
   - Define the `path` with correct resource naming (plural nouns: `/customers`, `/orders`)
   - Define the HTTP method: `get`, `post`, `put`, `patch`, `delete`
   - Add `operationId` in `lowerCamelCase` format
   - Add `summary` and `description`
   - Define `tags` for grouping (one tag per resource)
   - Define `parameters` for path variables and query parameters
   - Define `requestBody` for POST/PUT/PATCH with `application/json` content
   - Define responses:
     - `200` or `201` for success with response schema
     - `204` for delete/no-content operations
     - `400` for bad request (validation)
     - `401` for unauthenticated
     - `403` for unauthorized
     - `404` for not found
     - `422` for validation errors (use `application/problem+json` with `ProblemDetail` schema)
     - `500` for internal server error
5. Define all schemas in `components/schemas` — reference them with `$ref`
6. Use `format` annotations on fields: `format: uuid`, `format: date-time`, `format: email`
7. Add `example` values on at least one schema per resource
8. Define `securitySchemes` if the API requires authentication (JWT Bearer)
9. Apply `security: [bearerAuth: []]` to all endpoints unless explicitly public

---

## Input

Provide:
- **API name and purpose** — 1-2 sentences
- **Resources** — list each resource type (Customer, Order, etc.)
- **Endpoints** — for each resource: which HTTP operations are supported
- **Field definitions** — fields for each request/response schema
- **Authentication** — JWT, API key, or none
- **Error handling conventions** — RFC 7807 ProblemDetail or custom error format

---

## Output

Complete OpenAPI 3.0 YAML file:

```yaml
openapi: 3.0.3
info:
  title: Customer Management API
  version: 1.0.0
  description: |
    Manages customer records including creation, retrieval, update, and deactivation.
    All endpoints require Bearer JWT authentication.

servers:
  - url: http://localhost:8080
    description: Local development

security:
  - bearerAuth: []

tags:
  - name: Customers
    description: Customer management operations

paths:
  /api/v1/customers:
    get:
      tags: [Customers]
      operationId: listCustomers
      summary: List all customers (paginated)
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 0 }
        - name: size
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
        - name: status
          in: query
          schema: { $ref: '#/components/schemas/CustomerStatus' }
      responses:
        '200':
          description: Paginated list of customers
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CustomerPageResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  schemas:
    Customer:
      type: object
      required: [id, name, email, status]
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
          example: "550e8400-e29b-41d4-a716-446655440000"
        name:
          type: string
          maxLength: 100
          example: "Acme Corporation"
        email:
          type: string
          format: email
          example: "contact@acme.com"
        status:
          $ref: '#/components/schemas/CustomerStatus'

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
```

---

## Quality Gates

- [ ] Valid OpenAPI 3.0.3 YAML — passes `openapi-generator validate`
- [ ] Every endpoint has `operationId`, `summary`, and at least one response
- [ ] All schemas defined in `components/schemas` (no inline schemas in paths)
- [ ] `422` response defined using `application/problem+json` with `ProblemDetail` schema
- [ ] `securitySchemes` defined and applied to all non-public endpoints
- [ ] `format` applied to `uuid`, `date-time`, `email`, `int64` fields
- [ ] At least one `example` value per resource schema
