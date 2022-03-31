
from kubernetes import client, config
def getPodData():
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    ret = api_instance.list_pod_for_all_namespaces(watch=False)

    podDict = []

    for i in ret.items:
        podDict.append({
            "pod_ip": i.status.pod_ip, 
            "name": i.metadata.name, 
            "namespace": i.metadata.namespace,
            "status": i.status.phase,
            "containers": [j.image for j in i.spec.containers]
        })
    return podDict

print(getPodData()[0])