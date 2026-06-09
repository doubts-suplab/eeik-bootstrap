# eeik-managed pack=java
# REST API Standard

**Pack:** java-pack | **Version:** 1.0

---

## URI Design

- Use nouns, not verbs: `/orders` not `/createOrder`
- Kebab-case for multi-word resources: `/line-items` not `/lineItems`
- Nest to show ownership: `/orders/{orderId}/line-items`
- Max 2 levels of nesting — deeper = design smell
- API versioning in path: `/v1/orders`, `/v2/orders`

## HTTP Method Semantics

| Method | Use | Idempotent |
|--------|-----|-----------|
| GET | Read (no side effects) | Yes |
| POST | Create | No |
| PUT | Replace entire resource | Yes |
| PATCH | Partial update | No |
| DELETE | Remove | Yes |

## Response Shapes

### Success
```json
{
  "orderId": "uuid",
  "status": "CONFIRMED",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### Error (RFC 7807 ProblemDetail)
```json
{
  "type": "https://api.example.com/errors/order-not-found",
  "title": "Order Not Found",
  "status": 404,
  "detail": "No order found with ID: 550e8400-e29b-41d4-a716-446655440000",
  "instance": "/v1/orders/550e8400-e29b-41d4-a716-446655440000",
  "orderId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## OpenAPI Documentation

Every endpoint requires:
- `@Operation(summary = "...")`
- `@ApiResponse` for each possible status code
- `@Schema` on all request/response DTOs
- `@Parameter` on all path/query parameters

## Pagination

```json
GET /v1/orders?page=0&size=20&sort=createdAt,desc

{
  "content": [...],
  "page": { "number": 0, "size": 20, "totalElements": 143, "totalPages": 8 }
}
```

Use Spring Data `Pageable` — never manual offset/limit SQL.
