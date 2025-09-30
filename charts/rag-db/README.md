# rag-db chart

This chart deploys vector database services and document processing components for the RAG (Retrieval-Augmented Generation) pipeline. It provides multiple database backend options and automated document embedding capabilities as part of a RAG-LLM Validated Pattern.

**Note**: This chart is designed for testing and demonstration purposes, allowing easy comparison between different vector database providers. For production deployments, consider using dedicated operators and charts specifically tuned for your chosen database provider.

## Purpose

This chart creates the necessary resources to store and retrieve vector embeddings for the RAG pipeline. It supports multiple vector database providers and includes a job to automatically process and embed documents from various sources, enabling the retrieval component of the RAG system to find relevant context for user queries.

## Configuration

The chart deploys the following main components:

1. **Vector Database Provider** - Configurable database backend for storing embeddings ([deployment.yaml](./templates/deployment.yaml))
2. **Database Service** - Service endpoint for database access ([service.yaml](./templates/service.yaml))
3. **Vector Embedding Job** - Processes documents and creates embeddings ([vector-embed-job.yaml](./templates/vector-embed-job.yaml))
4. **External Secret** - Manages database credentials via Vault integration ([external-secret.yaml](./templates/external-secret.yaml))

### Configurable Options

The chart supports the following configuration options via `values.yaml`:

#### Global Configuration
- `global.embeddingModel`: Hugging Face model for generating embeddings (default: "sentence-transformers/all-mpnet-base-v2")

#### Database Provider Selection
Choose one of the supported vector database providers by setting `enabled: true`:

**Qdrant**
- `providers.qdrant.enabled`: Enable Qdrant vector database
- `providers.qdrant.deployment.image`: Qdrant container image
- `providers.qdrant.service.port`: Service port (default: 6333)
- `providers.qdrant.jobEnv`: Environment variables for the embedding job

**Redis**
- `providers.redis.enabled`: Enable Redis with vector search capabilities
- `providers.redis.deployment.image`: Redis Stack container image
- `providers.redis.service.port`: Service port (default: 6379)
- `providers.redis.jobEnv`: Environment variables for the embedding job

**PostgreSQL with pgvector**
- `providers.pgvector.enabled`: Enable PostgreSQL with pgvector extension
- `providers.pgvector.deployment.image`: PostgreSQL container image
- `providers.pgvector.service.port`: Service port (default: 5432)
- `providers.pgvector.secrets.vault.fields`: Database credentials managed by Vault

**Elasticsearch**
- `providers.elastic.enabled`: Enable Elasticsearch vector search
- `providers.elastic.deployment.image`: Elasticsearch container image
- `providers.elastic.service.port`: Service port (default: 9200)
- `providers.elastic.secrets.vault.fields`: Database credentials managed by Vault

**Microsoft SQL Server**
- `providers.mssql.enabled`: Enable SQL Server with vector capabilities (default: true)
- `providers.mssql.deployment.image`: SQL Server container image
- `providers.mssql.service.port`: Service port (default: 1433)
- `providers.mssql.secrets.vault.fields`: Database credentials managed by Vault

#### Vector Embedding Job Configuration
- `vectorEmbedJob.image`: Container image for the document processing job
- `vectorEmbedJob.backoffLimit`: Maximum retry attempts (default: 10)
- `vectorEmbedJob.logLevel`: Logging verbosity (default: "info")
- `vectorEmbedJob.repoSources`: Git repositories to process for documents
- `vectorEmbedJob.webSources`: Web URLs to scrape and embed
- `vectorEmbedJob.chunking.size`: Text chunk size for embeddings (default: 1024)
- `vectorEmbedJob.chunking.overlap`: Overlap between chunks (default: 40)

## Prerequisites

The following must be configured on your OpenShift cluster:

- Red Hat OpenShift AI or OpenDataHub for model serving capabilities
- Vault integration for secret management (configured by the Validated Pattern)
- Sufficient cluster resources to meet the configured CPU/memory requirements
- Network access to external document sources (for web scraping and git repositories)

### Secret Management

The Validated Pattern automatically configures Vault and creates the required database secrets. To enable this functionality for database providers that require authentication, you must:

1. Copy `values-secret.yaml.template` from the root of this repository to `$HOME/values-secret-$(basename $PWD).yaml` (outside of git)
2. Update the secret values in the copied file for the database providers you plan to use
3. The following providers require secret configuration:
   - **pgvector**: Requires `user`, `password`, and `db` fields
   - **elastic**: Requires `user` and `password` fields
   - **mssql**: Requires `sapassword` field

Database credentials are then automatically generated and managed through:

1. Vault secret storage and rotation
2. External Secrets Operator integration
3. Automatic connection string generation for each provider

You can see all available secret fields that need to be configured in `values-secret.yaml.template`.

## Data Sources

The embedding job processes documents from multiple sources:

### Repository Sources
- Git repositories with configurable glob patterns for file selection
- Default includes PDF documentation from the llm-on-openshift project

### Web Sources
- Web pages scraped and processed for embedding
- Default includes comprehensive OpenShift AI documentation

### Document Processing
- Automatic text chunking with configurable size and overlap
- Vector embedding generation using the specified Hugging Face model
- Storage in the selected vector database provider

## Helper Templates

The chart includes helper templates for generating database connection strings and managing provider-specific configurations across different database backends.

## Notes

- Multiple database providers may be enabled simultaneously
- The vector embedding job runs once to populate the database with initial content
- Database persistence is configured with emptyDir volumes by default
- Resource requests and limits should be adjusted based on document volume and expected query load
- The embedding model can be changed, but requires reprocessing all documents
