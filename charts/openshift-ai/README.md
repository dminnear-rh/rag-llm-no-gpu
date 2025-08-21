# openshift-ai chart

This chart configures the Red Hat OpenShift AI (RHOAI) data science cluster components required for serving machine learning models via KServe. This configuration is essential for enabling model inference capabilities within the RAG-LLM pattern.

## Purpose

This chart enables RHOAI to serve models by configuring the necessary infrastructure components. Without these configurations, model serving would not be available, preventing the deployment of inference services required for the RAG-LLM workflow.

## Configuration

The chart performs two key configurations:

1. **Enable Istio service mesh** for model inference services ([dsci.yaml](./templates/dsci.yaml))
2. **Enable KServe serverless model serving** for scalable inference ([dsc.yaml](./templates/dsc.yaml))

### Configurable Options

The chart supports the following configuration options via `values.yaml`:

#### KServe Deployment Mode
- `kserve.defaultDeploymentMode`: Sets the default deployment mode for models
  - `Serverless` (default): Advanced mode with auto-scaling capabilities
  - `RawDeployment`: Standard mode for traditional deployments

#### Load Balancing Configuration
- `kserve.rawDeploymentServiceConfig`: Controls load balancing behavior
  - `Headed` (default): Normal cluster-based load balancing over workload replicas
  - `Headless`: Client-side load balancing for environments where inference request load balancing is handled client-side

## Prerequisites

The following operators must be installed on your OpenShift cluster:

- `rhods-operator` - Red Hat OpenShift AI operator
- `servicemeshoperator` - Red Hat OpenShift Service Mesh operator
- `serverless-operator` - Red Hat OpenShift Serverless operator

## Reference

Based on the [RHOAI documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.23/html/installing_and_uninstalling_openshift_ai_self-managed/installing-the-single-model-serving-platform_component-install#configuring-automated-installation-of-kserve_component-install).
