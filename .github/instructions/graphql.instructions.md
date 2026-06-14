---
applyTo: "**/*.graphql, **/*.graphqls, **/resolvers/**/*.java, **/resolvers/**/*.ts, **/graphql/**/*.java, **/graphql/**/*.ts"
---

## Context

This instruction file applies to GraphQL schema files and resolver implementations. The project follows a **schema-first** design: the `.graphql` / `.graphqls` schema file is the contract; resolver code is generated or implemented to satisfy it. The server uses Spring for GraphQL (Java) or Apollo Server / GraphQL-Yoga (TypeScript). N+1 query prevention via DataLoader is mandatory. Depth and complexity limiting is required in all production environments.

---

## Coding Standards

- **Schema-first:** Define the schema in `.graphql` files before writing any resolver code
- **Mutation payload types:** Every mutation returns a dedicated payload type with an `errors` field — never return the entity directly
- **No `input` reuse across mutations:** Each mutation has its own `input` type — never share `CreateOrderInput` between create and update
- **DataLoader mandatory:** Any resolver that loads a related entity must use a DataLoader — never call a repository in a loop
- **Cursor-based pagination:** Use Relay-spec `Connection` / `Edge` / `PageInfo` types — never offset-based `skip`/`limit`
- **Deprecate, never remove:** Mark unused fields `@deprecated(reason: "...")` and keep for one API lifecycle — never delete a field from a live schema
- **Depth limit:** Maximum query depth of 7 in production; enforced by `graphql-java-extended-scalars` or `graphql-depth-limit`
- **Complexity limit:** Maximum complexity of 200 per query; each field contributes 1 by default, connections contribute 10

---

## Preferred Patterns

### Schema Design

```graphql
# ✅ CORRECT — mutation payload with errors, dedicated input type
type Mutation {
  placeOrder(input: PlaceOrderInput!): PlaceOrderPayload!
  cancelOrder(input: CancelOrderInput!): CancelOrderPayload!
}

input PlaceOrderInput {
  customerId: ID!
  items: [OrderLineItemInput!]!
  currency: Currency!
}

type PlaceOrderPayload {
  order: Order
  errors: [UserError!]!
}

type UserError {
  message: String!
  field: [String!]
  code: String!
}

# ✅ CORRECT — Relay cursor pagination
type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type OrderEdge {
  node: Order!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# ❌ WRONG — mutation returns entity directly, no error handling
type Mutation {
  placeOrder(customerId: ID!, items: [OrderLineItemInput!]!): Order
}

# ❌ WRONG — offset-based pagination
type Query {
  orders(skip: Int, limit: Int): [Order!]!
}
```

### DataLoader (N+1 Prevention)

```java
// ✅ CORRECT — Spring for GraphQL DataLoader registration
@Component
public class CustomerDataLoader {

    @Bean
    public BatchLoaderRegistry batchLoaderRegistry(CustomerRepository repo) {
        return BatchLoaderRegistry.builder()
            .forTypePair(String.class, Customer.class)
            .registerMappedBatchLoader("customerLoader",
                (customerIds, env) -> Mono.fromCompletionStage(
                    repo.findAllByIds(customerIds)
                        .thenApply(customers -> customers.stream()
                            .collect(Collectors.toMap(c -> c.getId().toString(), c -> c)))
                ))
            .build();
    }
}

// ✅ CORRECT — resolver uses DataLoader, not direct repo call
@SchemaMapping(typeName = "Order", field = "customer")
public CompletableFuture<Customer> customer(Order order, DataLoader<String, Customer> customerLoader) {
    return customerLoader.load(order.getCustomerId().toString());
}

// ❌ WRONG — N+1: calls repo once per Order
@SchemaMapping(typeName = "Order", field = "customer")
public Customer customer(Order order) {
    return customerRepository.findById(order.getCustomerId()).orElseThrow();
}
```

### TypeScript Resolver (Apollo Server)

```typescript
// ✅ CORRECT — resolver with DataLoader, typed context
import DataLoader from "dataloader";

const resolvers = {
  Order: {
    customer: async (order: Order, _args: never, ctx: Context): Promise<Customer> => {
      return ctx.loaders.customer.load(order.customerId);
    },
  },
  Mutation: {
    placeOrder: async (_root: never, { input }: PlaceOrderArgs, ctx: Context): Promise<PlaceOrderPayload> => {
      try {
        const order = await ctx.orderService.place(input);
        return { order, errors: [] };
      } catch (err) {
        return { order: null, errors: [{ message: (err as Error).message, code: "ORDER_FAILED", field: null }] };
      }
    },
  },
};
```

---

## Anti-Patterns — Do NOT Generate

```graphql
# WRONG: mutation returns entity directly — no error handling [BLOCKER]
type Mutation {
  placeOrder(customerId: ID!, items: [OrderLineItemInput!]!): Order!
}

# WRONG: shared input type across mutations [MAJOR]
input OrderInput {
  id: ID
  customerId: ID
  items: [OrderLineItemInput!]
}

# WRONG: offset pagination — inconsistent on fast-moving datasets [MAJOR]
type Query {
  orders(skip: Int!, limit: Int!): [Order!]!
}

# WRONG: removing a field without deprecation period [MAJOR]
# (deleted field that was previously in schema)

# WRONG: field named with implementation details [MINOR]
type Order {
  mysqlId: Int!  # exposes storage detail
}
```

```java
// WRONG: N+1 — repository call inside a per-entity resolver [BLOCKER]
@SchemaMapping(typeName = "Order", field = "customer")
public Customer customer(Order order) {
    return customerRepository.findById(order.getCustomerId()).orElseThrow();
}
```

---

## Dependencies & Versions

| Technology | Version | Notes |
|-----------|---------|-------|
| Spring for GraphQL | 1.3+ | `@QueryMapping`, `@SchemaMapping`, `@MutationMapping` |
| graphql-java | 21+ | `BatchLoaderRegistry` for DataLoader integration |
| graphql-java-extended-scalars | 22+ | `Date`, `DateTime`, `JSON`, depth/complexity limiting |
| Apollo Server | 4.x | TypeScript; `ApolloServerPlugin` for complexity limits |
| DataLoader (npm) | 2.x | Batch + cache loader for N+1 prevention |
| graphql-depth-limit (npm) | 1.x | `depthLimit(7)` validation rule |

---

## Test Conventions

- Test resolvers with `GraphQlTester` (Spring) or `ApolloServer.executeOperation` (TypeScript) — not raw HTTP
- Test DataLoader batching: assert the repository `findAllByIds` is called once even when 10 orders are resolved
- Test mutation error paths: verify `errors` field is populated and `order` is null on failure
- Test pagination: verify `hasNextPage`, `endCursor`, and correct `edges` count for a given `first` value
- Test depth limiting: submit a deeply nested query (depth > 7) and assert a validation error is returned
- Test complexity limiting: submit a query exceeding complexity 200 and assert rejection
