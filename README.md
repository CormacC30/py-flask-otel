# A simple test environment in OpenShift for demonstrating an Python web server instrumented for metrics, logs and traces using Red Hat Build of OpenTelemetry

1. Install the following Operators:

- Red Hat Build of OpenTelemetry
- Cluster Observability Operator
- OpenShift Logging
- Loki
- Distributed Tracing

2. Set up Object storage and LokiStack and TempoStack

3. Create a namespace, deploy the Python-flask webserver, create a service and route:

```
oc new-project test
oc create deployment test-py --image quay.io/rhn-support-ccostell/ping-py:latest -n test
oc expose deployment test-py -n test --port 8090
oc expose svc test-py
```


4. verify the functioning route, use endpoint to generate traffic:

```
HOST=$(oc get route test-py -n test -o jsonpath='{.spec.host}')
curl -I http://$HOST/ping
```

5. Create serviceaccount, and assign correct permissions

```
# Create the serviceaccount 
oc create sa otel-collector-sa -n test
#
# Assign permissions
#
cat <<EOF | oc apply -f - 
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: otel-collector-role
rules:
- apiGroups: [""]
  resources: ["pods", "namespaces", "nodes"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["apps"]
  resources: ["replicasets"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: otel-collector-binding
subjects:
- kind: ServiceAccount
  name: otel-collector-sa
  namespace: test
roleRef:
  kind: ClusterRole
  name: otel-collector-role
  apiGroup: rbac.authorization.k8s.io
EOF
```

```
cat <<EOF | oc apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: otel-collector-logs-writer
rules:
 - apiGroups: ["loki.grafana.com"]
   resourceNames: ["logs"]
   resources: ["application"]
   verbs: ["create"]
 - apiGroups: [""]
   resources: ["pods", "namespaces", "nodes"]
   verbs: ["get", "watch", "list"]
 - apiGroups: ["apps"]
   resources: ["replicasets"]
   verbs: ["get", "list", "watch"]
 - apiGroups: ["extensions"]
   resources: ["replicasets"]
   verbs: ["get", "list", "watch"]
EOF
```

```
cat <<EOF | oc apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: otel-collector-logs-writer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: otel-collector-logs-writer
subjects:
  - kind: ServiceAccount
    name: otel-collector-sa
    namespace: test
EOF
```

6. Create instrumentation: https://docs.redhat.com/en/documentation/openshift_container_platform/4.19/html/red_hat_build_of_opentelemetry/otel-configuration-of-instrumentation#otel-instrumentation-options_otel-configuration-of-instrumentation

```
oc apply -f manifests/instrumentation.yaml
```

7. Create the OTEL collector:

```
oc apply -f manifests/collector.yaml
```

8. Add the following annotation to the PodSpec:

```
oc patch deployment test-py -n test --type=json -p='[                                                                                                
  {                                                                                                                                                    
    "op": "add",                                                                                                                                          
    "path": "/spec/template/metadata/annotations",                                                                                                     
    "value": {                                                                                                                                                 
      "instrumentation.opentelemetry.io/inject-python": "true"                                                                                          
    }                                                                                                                                                 
  }             
]' 
```

9. Check metrics and Logs


