# llm-inference-service chart

This chart deploys a vLLM-based large language model inference service using KServe on Red Hat OpenShift AI. It provides a scalable, production-ready endpoint for serving LLM models as part of the RAG-LLM Validated Pattern.

## Purpose

This chart creates the necessary KServe resources to serve a large language model for inference requests. It configures both the serving runtime environment and the inference service, enabling the LLM component of the RAG pipeline to process user queries and generate responses.

## Configuration

The chart deploys two main components:

1. **ServingRuntime** - Configures the vLLM runtime environment ([serving-runtime.yaml](./templates/serving-runtime.yaml))
2. **InferenceService** - Defines the model serving endpoint with scaling and resource configuration ([inference-service.yaml](./templates/inference-service.yaml))

### Configurable Options

The chart supports the following configuration options via `values.yaml`:

#### Model Configuration
- `model.repo`: Hugging Face repository/organization name (e.g., "mistralai")
- `model.vllm`: Specific model name (e.g., "Mistral-7B-Instruct-v0.3")

#### Serving Runtime Configuration
- `servingRuntime.name`: Name of the serving runtime
- `servingRuntime.modelFormat`: Model format type (default: "vLLM")
- `servingRuntime.image.repo`: Container image repository for the vLLM server
- `servingRuntime.image.tag`: Container image tag
- `servingRuntime.port`: Port for the inference server (default: 8080)

#### Inference Service Configuration
- `inferenceService.resources.limits`: Maximum CPU and memory allocation
- `inferenceService.resources.requests`: Minimum CPU and memory allocation
- `inferenceService.minReplicas`: Minimum number of replicas (default: 1)
- `inferenceService.maxReplicas`: Maximum number of replicas (default: 1)

## Prerequisites

The following must be configured on your OpenShift cluster:

- Red Hat OpenShift AI with KServe enabled
- Istio service mesh configured
- Sufficient cluster resources to meet the configured CPU/memory requirements

### Hugging Face Token Setup

The Validated Pattern automatically configures Vault and creates the required Hugging Face secret. To enable this functionality, you must:

1. Copy `values-secret.yaml.template` from the root of this repository to `$HOME/values-secret-$(basename $PWD).yaml` (outside of git)
2. Update the token value in the copied file with your own Hugging Face token
3. Ensure your token has read access to the model specified in your configuration
4. **Important**: Accept the model's terms and conditions on Hugging Face if required (e.g., the default Mistral model requires accepting terms before access is granted)

## Helper Templates

The chart includes a helper template for generating the model ID:

- `llm-inference-service.modelId`: Combines repo and model name (e.g., "mistralai/Mistral-7B-Instruct-v0.3")

## Notes

- The inference service is configured with Istio sidecar injection for secure communication
- Prometheus metrics are exposed on the configured port for monitoring
- The service requires a Hugging Face token for downloading models from private repositories
- Resource requests and limits should be adjusted based on the specific model size and expected load
