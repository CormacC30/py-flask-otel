# A simple test environment in OpenShift for demonstrating an auto-instrumented Python web server using Red Hat Build of OpenTelemetry

1. Install the following Operators:

- Red Hat Build of OpenTelemetry
- Cluster Observability Operator
- OpenShift Logging
- Loki
- Tempo
- Ensure `User Workload Monitoring` is enabled

2. Set up Object storage and LokiStack and TempoStack

3. Create a namespace, deploy the Python-flask webserver, create a service and route:

```
oc new-project test
oc create deployment test-py --image quay.io/rhn-support-ccostell/ping-py:latest -n test
oc expose deployment test-py -n test --port 8090
oc expose svc test-py
```

4. Add the instrumentation annotation to the PodSpec

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

5. Create serviceaccount, and assign correct permissions

```
# Create the serviceaccount 
oc create sa otel-collector-sa -n test
# Assign permissions, create the collector, instrumentation 
oc create -Rf manifests
```

6. Use the application's endpoint to generate traffic:

```
HOST=$(oc get route test-py -n test -o jsonpath='{.spec.host}')
curl -I http://$HOST/ping
```

7. Verify the instrumented metrics:

```
# First check the servicemonitors have been created
oc get servicemonitor -n test
# cURL the target /metrics endpoint
COLLECTOR_SVC_IP=$(oc -n test get service otel-collector-collector -o jsonpath='{.spec.clusterIP}')
oc -n openshift-monitoring exec -it prometheus-k8s-0 -- curl http://$COLLECTOR_SVC_IP:8889/metrics
```



