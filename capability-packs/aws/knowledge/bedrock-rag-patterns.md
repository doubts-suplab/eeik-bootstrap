# Amazon Bedrock RAG Architecture Patterns

**Type**: Reference Architecture  
**Stack**: AWS Bedrock, Knowledge Bases, OpenSearch Serverless, Lambda, CDK

---

## Pattern 1: Bedrock Knowledge Base (Managed RAG)

The simplest production RAG — fully managed retrieval, no custom vector logic.

```
S3 Data Source → Bedrock Knowledge Base → OpenSearch Serverless (vector store)
                         ↓
User Query → Bedrock RetrieveAndGenerate API → Foundation Model (Claude 3) → Response
```

### CDK Stack

```typescript
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import * as opensearchserverless from 'aws-cdk-lib/aws-opensearchserverless';
import * as s3 from 'aws-cdk-lib/aws-s3';

export class BedrockKnowledgeBaseStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: KnowledgeBaseProps) {
    super(scope, id, props);

    // S3 data source
    const docsBucket = new s3.Bucket(this, 'DocsBucket', {
      bucketName: `${props.projectName}-knowledge-${this.account}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // OpenSearch Serverless collection
    const vectorCollection = new opensearchserverless.CfnCollection(this, 'VectorCollection', {
      name: `${props.projectName}-vectors`,
      type: 'VECTORSEARCH',
    });

    // Bedrock Knowledge Base
    const knowledgeBase = new bedrock.CfnKnowledgeBase(this, 'KnowledgeBase', {
      name: `${props.projectName}-kb`,
      roleArn: knowledgeBaseRole.roleArn,
      knowledgeBaseConfiguration: {
        type: 'VECTOR',
        vectorKnowledgeBaseConfiguration: {
          embeddingModelArn: `arn:aws:bedrock:${this.region}::foundation-model/amazon.titan-embed-text-v2:0`,
        },
      },
      storageConfiguration: {
        type: 'OPENSEARCH_SERVERLESS',
        opensearchServerlessConfiguration: {
          collectionArn: vectorCollection.attrArn,
          vectorIndexName: 'knowledge-index',
          fieldMapping: {
            vectorField: 'embedding',
            textField: 'text',
            metadataField: 'metadata',
          },
        },
      },
    });

    // Data source
    new bedrock.CfnDataSource(this, 'S3DataSource', {
      knowledgeBaseId: knowledgeBase.attrKnowledgeBaseId,
      name: 'documents',
      dataSourceConfiguration: {
        type: 'S3',
        s3Configuration: { bucketArn: docsBucket.bucketArn },
      },
      vectorIngestionConfiguration: {
        chunkingConfiguration: {
          chunkingStrategy: 'FIXED_SIZE',
          fixedSizeChunkingConfiguration: { maxTokens: 512, overlapPercentage: 20 },
        },
      },
    });
  }
}
```

### Python — Query the Knowledge Base

```python
import boto3
from dataclasses import dataclass

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='eu-west-1')

@dataclass
class RagResponse:
    answer: str
    citations: list[dict]
    session_id: str

def query_knowledge_base(
    query: str,
    knowledge_base_id: str,
    model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
    session_id: str | None = None,
) -> RagResponse:
    kwargs = {
        "input": {"text": query},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": knowledge_base_id,
                "modelArn": f"arn:aws:bedrock:eu-west-1::foundation-model/{model_id}",
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {"numberOfResults": 5}
                },
                "generationConfiguration": {
                    "promptTemplate": {
                        "textPromptTemplate": (
                            "You are a helpful assistant. Answer using only the provided context.\n"
                            "Context: $search_results$\n\nQuestion: $query$\n\nAnswer:"
                        )
                    }
                },
            },
        },
    }
    if session_id:
        kwargs["sessionId"] = session_id

    response = bedrock_agent_runtime.retrieve_and_generate(**kwargs)

    return RagResponse(
        answer=response["output"]["text"],
        citations=[c["retrievedReferences"] for c in response.get("citations", [])],
        session_id=response["sessionId"],
    )
```

---

## Pattern 2: Custom RAG with pgvector (more control)

Use when: you need hybrid search (keyword + semantic), custom metadata filtering, or existing PostgreSQL.

```python
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_postgres import PGVector
from langchain.chains import RetrievalQA

# Embeddings
embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name="eu-west-1",
)

# Vector store (RDS PostgreSQL with pgvector extension)
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name="documents",
    connection=os.environ["DATABASE_URL"],
)

# Retriever with metadata filter
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5,
        "filter": {"document_type": "policy"},   # metadata filter
    },
)

# Chain
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="eu-west-1",
)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
```

---

## Pattern 3: Bedrock Agents (Agentic RAG)

Use when: the user's query requires tool calls (look up a database, call an API) in addition to RAG.

```
User → Bedrock Agent → Orchestration LLM → Action Group (Lambda) OR Knowledge Base
                              ↓
                       Synthesised Response
```

```python
# Lambda function for Bedrock Agent action group
def handler(event, context):
    action_group = event['actionGroup']
    function = event['function']
    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}

    if function == 'getOrderStatus':
        order_id = parameters['orderId']
        order = order_repository.find(order_id)
        return {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': {
                    'TEXT': {'body': f"Order {order_id} status: {order.status}"}
                }
            }
        }
```

---

## Guardrails

Always apply Bedrock Guardrails in production:

```python
response = bedrock_runtime.converse(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    messages=[{"role": "user", "content": [{"text": user_query}]}],
    guardrailConfig={
        "guardrailIdentifier": os.environ["GUARDRAIL_ID"],
        "guardrailVersion": "DRAFT",
        "trace": "enabled",
    },
)

# Check if guardrail blocked the response
if response.get('stopReason') == 'guardrail_intervened':
    logger.warning("guardrail_triggered", query=user_query)
    return {"answer": "I can't help with that request.", "blocked": True}
```

---

## Cost Governance

| Model | Input (per 1K tokens) | Output (per 1K tokens) | Use case |
|---|---|---|---|
| Claude 3 Haiku | $0.00025 | $0.00125 | Classification, extraction |
| Claude 3 Sonnet | $0.003 | $0.015 | General Q&A, RAG |
| Claude 3 Opus | $0.015 | $0.075 | Complex reasoning, compliance |
| Titan Embed v2 | $0.00002 | — | Embeddings |

Rules:
- Set `maxTokens` on every inference call — prevent runaway costs
- Use Haiku for classification and extraction tasks
- CloudWatch alarms on Bedrock token spend per day
- Enable model invocation logging for audit and cost attribution
