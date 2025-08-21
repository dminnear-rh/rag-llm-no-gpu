{{/*
Generate model ID from global values
*/}}
{{- define "llm-inference-service.modelId" -}}
{{- printf "%s/%s" .Values.model.repo .Values.model.name -}}
{{- end -}}
