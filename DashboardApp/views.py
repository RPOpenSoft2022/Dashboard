from django.shortcuts import render
from DashboardApp.interconnect import send_request_get
from numerize import numerize
import json
from kubernetes import client, config


def dashboard(request):
    sales_url = "http://34.93.3.9/orderapp/last_month_sales/"
    add = send_request_get(sales_url)
    [_, sales_response] = send_request_get(sales_url)
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
    pod_details = getPodData()
    context = {
            'sales_months': sales_months,
            'sales': sales,
            'user_months': user_months,
            'users': users,
            "user_increase_percent": (users[-1]-users[-2])/100,
            "sales_increase": (sales[-1]-sales[-2]),
            "customers": numerize.numerize(users_data["customer"]),
            "staff": numerize.numerize(users_data["staff"]),
            "delivery": numerize.numerize(users_data["delivery"]),
            "podDetails":pod_details,
            "pod_count": len(pod_details)
        }
    return render(request, 'dashboard.html', context)


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

def getSvcData():
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    ret = api_instance.list_service_for_all_namespaces(watch=False)

    svcDict = []

    for i in ret.items:
        svcDict.append({
            "pod_ip": i.status.pod_ip, 
            "name": i.metadata.name, 
            "namespace": i.metadata.namespace,
            "status": i.status.phase,
            "containers": [j.image for j in i.spec.containers],
            "conditions": i.status.conditions
        })
    return svcDict
