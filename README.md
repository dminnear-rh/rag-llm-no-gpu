# RAG-LLM without GPU - Validated Pattern

This Validated Pattern deploys a simple RAG-LLM (Retrieval-Augmented Generation with Large Language Model) chatbot on Red Hat OpenShift using Red Hat OpenShift AI. The pattern is designed to run entirely on CPU nodes without requiring GPU hardware, making it accessible for environments where GPU resources are not available.

## What This Pattern Provides

- A complete RAG-LLM pipeline deployed on OpenShift
- Model serving using KServe and vLLM runtime
- Istio service mesh integration for secure communication
- Automated configuration of Red Hat OpenShift AI components
- Vault-based secret management for secure token storage

## Deployment Instructions

1. **Prerequisites**: Ensure you are logged into your OpenShift cluster with cluster-admin privileges

2. **Configure Secrets**:
   - Copy `values-secret.yaml.template` to `~/values-secret-rag-llm-no-gpu.yaml`
   - Update the Hugging Face token in the copied file
   - Ensure you have accepted the model's terms and conditions on Hugging Face

3. **Deploy the Pattern**:
   ```bash
   ./pattern.sh make install
   ```

   This command will install the complete pattern and load the required secrets.
