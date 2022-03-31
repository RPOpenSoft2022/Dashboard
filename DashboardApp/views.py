from django.shortcuts import render
from DashboardApp.interconnect import send_request_get
from numerize import numerize
import json
from kubernetes import client, config


def dashboard(request):
    sales_url = "http://34.93.3.9/orderapp/last_month_sales/"
    add = send_request_get(sales_url)
    [_, sales_response] = send_request_get(sales_url)
    print(sales_response)
    sales_data = sales_response.json()
    print(sales_data)
    sales_months = list(sales_data.keys())
    sales_months.reverse()
    print(sales_months)
    sales = [sales_data[i]['total_sales'] for i in sales_months]
    users_url = "http://34.93.3.9/userapp/api/usershistory/"
    [_, users_response] = send_request_get(users_url)
    users_data = users_response.json()
    user_months = list(users_data["history"].keys())
    user_months.reverse()
    users = [users_data["history"][i] for i in user_months]
    pod_details, podCt = getPodData()
    svc_details, svcCt = getSvcData()
    context = {
            'sales_months': sales_months,
            'sales': sales,
            'last_sales': sales[-1],
            'user_months': user_months,
            'users': users,
            'last_users': users[-1],
            "user_increase_percent": (users[-1]-users[-2])/100,
            "sales_increase": (sales[-1]-sales[-2]),
            "customers": numerize.numerize(users_data["customer"]),
            "staff": numerize.numerize(users_data["staff"]),
            "delivery": numerize.numerize(users_data["delivery"]),
            "podDetails":pod_details,
            "pod_count": podCt,
            "svcDetails": svc_details,
            "svc_count": svcCt
        }
    return render(request, 'dashboard.html', context)


def getPodData():
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # ret = api_instance.list_pod_for_all_namespaces(watch=False)
    ret = api_instance.list_namespace(watch=False)
    namespaces = []
    for name in ret.items:
        namespaces.append(name.metadata.name)
    podDict = {}
    podCt = 0
    for name in namespaces:
        ret = api_instance.list_namespaced_pod(name ,watch=False)
        podList = []
        for i in ret.items:
            podCt = podCt + 1
            for j in i.spec.containers:
                j.image = j.image.replace("rp", "")
            podList.append({
                "pod_ip": i.status.pod_ip, 
                "name": i.metadata.name,
                "status": i.status.phase,
                "containers": [j.image for j in i.spec.containers]
            })
        podDict[name] = podList
    return podDict, podCt
 
def getSvcData():
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    # ret = api_instance.list_pod_for_all_namespaces(watch=False)
    ret = api_instance.list_namespace(watch=False)
    namespaces = []
    for name in ret.items:
        namespaces.append(name.metadata.name)
    podDict = {}
    podCt = 0
    for name in namespaces:
        ret = api_instance.list_namespaced_service(name ,watch=False)
        podList = []
        for i in ret.items:
            podCt = podCt + 1
            podList.append({
                "name": i.metadata.name,
                "type": i.spec.type,
                "cluster_ip": i.spec.cluster_ip,
                "external_ips": i.spec.external_i_ps or i.spec.load_balancer_ip,
            })
        podDict[name] = podList
    return podDict, podCt