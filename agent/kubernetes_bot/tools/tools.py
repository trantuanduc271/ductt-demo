from kubernetes import client, config
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config.load_config()


api_v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
batch_v1 = client.BatchV1Api()
networking_v1 = client.NetworkingV1Api()
rbac_v1 = client.RbacAuthorizationV1Api()
storage_v1 = client.StorageV1Api()


def list_namespaces() -> list:
    """
    List all namespaces in the Kubernetes cluster.
    
    Returns:
        list: A list of namespace names.
    """
    namespaces = api_v1.list_namespace()
    return [ns.metadata.name for ns in namespaces.items]

def list_deployments_from_namespace(namespace: str) -> list:
    """
    List all deployments in a specific namespace.

    Args:
        namespace (str): The namespace to list deployments from.

    Returns:
        list: A list of deployment names in the specified namespace.
    """
    deployments = apps_v1.list_namespaced_deployment(namespace)
    return [deploy.metadata.name for deploy in deployments.items]

def list_pods_from_namespace(namespace: str) -> list:
    """
    List all pods in a specific namespace.

    Args:
        namespace (str): The namespace to list pods from.

    Returns:
        list: A list of pod names in the specified namespace.
    """
    pods = api_v1.list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items]

def list_services_from_namespace(namespace: str) -> list:
    """
    List all services in a specific namespace.

    Args:
        namespace (str): The namespace to list services from.

    Returns:
        list: A list of service names in the specified namespace.
    """
    services = api_v1.list_namespaced_service(namespace)
    return [svc.metadata.name for svc in services.items]

def list_all_resources(namespace: str) -> dict:
    """
    List all resources in a specific namespace.

    Args:
        namespace (str): The namespace to list resources from.

    Returns:
        dict: A dictionary containing lists of deployments, pods, and services for a specific namespace.
    """
    resources = {
        "deployments": list_deployments_from_namespace(namespace),
        "pods": list_pods_from_namespace(namespace),
        "services": list_services_from_namespace(namespace)
    }
    return resources


# Describe/Get functions for detailed information

def describe_pod(namespace: str, pod_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific pod.

    Args:
        namespace (str): The namespace of the pod.
        pod_name (str): The name of the pod.

    Returns:
        dict: Detailed information about the pod including status, containers, labels, and events.
    """
    pod = api_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    
    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "labels": pod.metadata.labels,
        "annotations": pod.metadata.annotations,
        "status": pod.status.phase,
        "node_name": pod.spec.node_name,
        "pod_ip": pod.status.pod_ip,
        "host_ip": pod.status.host_ip,
        "start_time": str(pod.status.start_time),
        "containers": [
            {
                "name": c.name,
                "image": c.image,
                "ready": cs.ready if cs else None,
                "restart_count": cs.restart_count if cs else None,
                "state": str(cs.state) if cs else None
            }
            for c, cs in zip(pod.spec.containers, pod.status.container_statuses or [])
        ],
        "conditions": [
            {
                "type": cond.type,
                "status": cond.status,
                "reason": cond.reason,
                "message": cond.message
            }
            for cond in (pod.status.conditions or [])
        ]
    }


def get_pod_logs(namespace: str, pod_name: str, container: Optional[str] = None, tail_lines: int = 50) -> str:
    """
    Get logs from a pod.

    Args:
        namespace (str): The namespace of the pod.
        pod_name (str): The name of the pod.
        container (str, optional): Specific container name if pod has multiple containers.
        tail_lines (int): Number of lines from the end of the logs to show (default: 50).

    Returns:
        str: The pod logs.
    """
    logger.info(f"Getting logs for pod: {pod_name} in namespace: {namespace}, container: {container}")
    try:
        logs = api_v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines
        )
        logger.info(f"Successfully retrieved {len(logs.splitlines())} lines of logs")
        return logs
    except Exception as e:
        error_msg = f"Error fetching logs: {str(e)}"
        logger.error(error_msg)
        return error_msg


def describe_deployment(namespace: str, deployment_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific deployment.

    Args:
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment.

    Returns:
        dict: Detailed information about the deployment.
    """
    deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    
    return {
        "name": deployment.metadata.name,
        "namespace": deployment.metadata.namespace,
        "labels": deployment.metadata.labels,
        "annotations": deployment.metadata.annotations,
        "replicas": deployment.spec.replicas,
        "ready_replicas": deployment.status.ready_replicas,
        "available_replicas": deployment.status.available_replicas,
        "updated_replicas": deployment.status.updated_replicas,
        "selector": deployment.spec.selector.match_labels,
        "strategy": deployment.spec.strategy.type,
        "containers": [
            {
                "name": c.name,
                "image": c.image,
                "ports": [{"container_port": p.container_port, "protocol": p.protocol} for p in (c.ports or [])],
                "resources": {
                    "limits": c.resources.limits if c.resources and c.resources.limits else None,
                    "requests": c.resources.requests if c.resources and c.resources.requests else None
                }
            }
            for c in deployment.spec.template.spec.containers
        ]
    }


def describe_service(namespace: str, service_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific service.

    Args:
        namespace (str): The namespace of the service.
        service_name (str): The name of the service.

    Returns:
        dict: Detailed information about the service.
    """
    service = api_v1.read_namespaced_service(name=service_name, namespace=namespace)
    
    return {
        "name": service.metadata.name,
        "namespace": service.metadata.namespace,
        "labels": service.metadata.labels,
        "annotations": service.metadata.annotations,
        "type": service.spec.type,
        "cluster_ip": service.spec.cluster_ip,
        "external_ips": service.spec.external_i_ps,
        "ports": [
            {
                "name": p.name,
                "port": p.port,
                "target_port": str(p.target_port),
                "protocol": p.protocol,
                "node_port": p.node_port
            }
            for p in (service.spec.ports or [])
        ],
        "selector": service.spec.selector,
        "load_balancer_ip": service.spec.load_balancer_ip,
        "load_balancer_ingress": [
            {"ip": ing.ip, "hostname": ing.hostname}
            for ing in (service.status.load_balancer.ingress or [])
        ] if service.status.load_balancer else []
    }


# Additional resource listing functions

def list_statefulsets_from_namespace(namespace: str) -> List[str]:
    """
    List all StatefulSets in a specific namespace.

    Args:
        namespace (str): The namespace to list StatefulSets from.

    Returns:
        list: A list of StatefulSet names.
    """
    statefulsets = apps_v1.list_namespaced_stateful_set(namespace)
    return [sts.metadata.name for sts in statefulsets.items]


def list_daemonsets_from_namespace(namespace: str) -> List[str]:
    """
    List all DaemonSets in a specific namespace.

    Args:
        namespace (str): The namespace to list DaemonSets from.

    Returns:
        list: A list of DaemonSet names.
    """
    daemonsets = apps_v1.list_namespaced_daemon_set(namespace)
    return [ds.metadata.name for ds in daemonsets.items]


def list_replicasets_from_namespace(namespace: str) -> List[str]:
    """
    List all ReplicaSets in a specific namespace.

    Args:
        namespace (str): The namespace to list ReplicaSets from.

    Returns:
        list: A list of ReplicaSet names.
    """
    replicasets = apps_v1.list_namespaced_replica_set(namespace)
    return [rs.metadata.name for rs in replicasets.items]


def list_configmaps_from_namespace(namespace: str) -> List[str]:
    """
    List all ConfigMaps in a specific namespace.

    Args:
        namespace (str): The namespace to list ConfigMaps from.

    Returns:
        list: A list of ConfigMap names.
    """
    configmaps = api_v1.list_namespaced_config_map(namespace)
    return [cm.metadata.name for cm in configmaps.items]


def list_secrets_from_namespace(namespace: str) -> List[str]:
    """
    List all Secrets in a specific namespace.

    Args:
        namespace (str): The namespace to list Secrets from.

    Returns:
        list: A list of Secret names.
    """
    secrets = api_v1.list_namespaced_secret(namespace)
    return [secret.metadata.name for secret in secrets.items]


def list_jobs_from_namespace(namespace: str) -> List[str]:
    """
    List all Jobs in a specific namespace.

    Args:
        namespace (str): The namespace to list Jobs from.

    Returns:
        list: A list of Job names.
    """
    jobs = batch_v1.list_namespaced_job(namespace)
    return [job.metadata.name for job in jobs.items]


def list_cronjobs_from_namespace(namespace: str) -> List[str]:
    """
    List all CronJobs in a specific namespace.

    Args:
        namespace (str): The namespace to list CronJobs from.

    Returns:
        list: A list of CronJob names.
    """
    cronjobs = batch_v1.list_namespaced_cron_job(namespace)
    return [cj.metadata.name for cj in cronjobs.items]


def list_ingresses_from_namespace(namespace: str) -> List[str]:
    """
    List all Ingresses in a specific namespace.

    Args:
        namespace (str): The namespace to list Ingresses from.

    Returns:
        list: A list of Ingress names.
    """
    ingresses = networking_v1.list_namespaced_ingress(namespace)
    return [ing.metadata.name for ing in ingresses.items]


def list_persistent_volumes() -> List[str]:
    """
    List all PersistentVolumes in the cluster.

    Returns:
        list: A list of PersistentVolume names.
    """
    pvs = api_v1.list_persistent_volume()
    return [pv.metadata.name for pv in pvs.items]


def list_persistent_volume_claims_from_namespace(namespace: str) -> List[str]:
    """
    List all PersistentVolumeClaims in a specific namespace.

    Args:
        namespace (str): The namespace to list PVCs from.

    Returns:
        list: A list of PersistentVolumeClaim names.
    """
    pvcs = api_v1.list_namespaced_persistent_volume_claim(namespace)
    return [pvc.metadata.name for pvc in pvcs.items]


def list_nodes() -> List[Dict[str, Any]]:
    """
    List all nodes in the cluster with basic information.

    Returns:
        list: A list of dictionaries containing node information.
    """
    nodes = api_v1.list_node()
    return [
        {
            "name": node.metadata.name,
            "status": next((cond.type for cond in node.status.conditions if cond.status == "True" and cond.type == "Ready"), "NotReady"),
            "roles": [label.split("/")[1] for label in node.metadata.labels if "node-role.kubernetes.io" in label],
            "version": node.status.node_info.kubelet_version,
            "internal_ip": next((addr.address for addr in node.status.addresses if addr.type == "InternalIP"), None),
            "external_ip": next((addr.address for addr in node.status.addresses if addr.type == "ExternalIP"), None)
        }
        for node in nodes.items
    ]


def describe_node(node_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific node.

    Args:
        node_name (str): The name of the node.

    Returns:
        dict: Detailed information about the node.
    """
    node = api_v1.read_node(name=node_name)
    
    return {
        "name": node.metadata.name,
        "labels": node.metadata.labels,
        "annotations": node.metadata.annotations,
        "conditions": [
            {
                "type": cond.type,
                "status": cond.status,
                "reason": cond.reason,
                "message": cond.message
            }
            for cond in (node.status.conditions or [])
        ],
        "capacity": node.status.capacity,
        "allocatable": node.status.allocatable,
        "node_info": {
            "machine_id": node.status.node_info.machine_id,
            "system_uuid": node.status.node_info.system_uuid,
            "kernel_version": node.status.node_info.kernel_version,
            "os_image": node.status.node_info.os_image,
            "container_runtime_version": node.status.node_info.container_runtime_version,
            "kubelet_version": node.status.node_info.kubelet_version,
            "kube_proxy_version": node.status.node_info.kube_proxy_version
        }
    }


def get_events_from_namespace(namespace: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get recent events from a specific namespace.

    Args:
        namespace (str): The namespace to get events from.
        limit (int): Maximum number of events to return (default: 50).

    Returns:
        list: A list of events with their details.
    """
    events = api_v1.list_namespaced_event(namespace, limit=limit)
    
    # Sort events by timestamp, handling None values
    def get_event_time(event):
        return event.last_timestamp or event.first_timestamp or event.metadata.creation_timestamp
    
    try:
        sorted_events = sorted(events.items, key=get_event_time, reverse=True)
    except (TypeError, AttributeError):
        # If sorting fails, just use the events as-is
        sorted_events = events.items
    
    return [
        {
            "type": event.type,
            "reason": event.reason,
            "message": event.message,
            "source": f"{event.source.component}/{event.source.host}" if event.source else None,
            "first_timestamp": str(event.first_timestamp) if event.first_timestamp else None,
            "last_timestamp": str(event.last_timestamp) if event.last_timestamp else None,
            "count": event.count,
            "involved_object": {
                "kind": event.involved_object.kind,
                "name": event.involved_object.name,
                "namespace": event.involved_object.namespace
            }
        }
        for event in sorted_events
    ]


def list_pods_with_labels(namespace: str, labels: str) -> List[str]:
    """
    List pods in a namespace filtered by label selector.

    Args:
        namespace (str): The namespace to list pods from.
        labels (str): Label selector (e.g., "app=nginx,tier=frontend").

    Returns:
        list: A list of pod names matching the label selector.
    """
    pods = api_v1.list_namespaced_pod(namespace, label_selector=labels)
    return [pod.metadata.name for pod in pods.items]


def get_pods_with_details(namespace: str, label_selector: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get pods in a namespace with their labels, annotations, and basic status.
    Useful for identifying pods related to specific workloads or DAG runs.

    Args:
        namespace (str): The namespace to list pods from.
        label_selector (str, optional): Label selector to filter pods (e.g., "dag_id=example_dag").

    Returns:
        list: A list of dictionaries containing pod details including labels and annotations.
    """
    logger.info(f"Getting pods from namespace: {namespace}, label_selector: {label_selector}")
    try:
        pods = api_v1.list_namespaced_pod(namespace, label_selector=label_selector)
        logger.info(f"Found {len(pods.items)} pods in namespace {namespace}")
        return [
            {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "labels": pod.metadata.labels,
                "annotations": pod.metadata.annotations,
                "created": str(pod.metadata.creation_timestamp),
                "node": pod.spec.node_name,
                "pod_ip": pod.status.pod_ip,
                "containers": [c.name for c in pod.spec.containers]
            }
            for pod in pods.items
        ]
    except Exception as e:
        logger.error(f"Error getting pods: {str(e)}")
        raise


def get_resource_quotas_from_namespace(namespace: str) -> List[Dict[str, Any]]:
    """
    Get resource quotas for a namespace.

    Args:
        namespace (str): The namespace to get resource quotas from.

    Returns:
        list: A list of resource quotas with their limits and usage.
    """
    quotas = api_v1.list_namespaced_resource_quota(namespace)
    return [
        {
            "name": quota.metadata.name,
            "hard": quota.status.hard,
            "used": quota.status.used
        }
        for quota in quotas.items
    ]


def get_namespace_details(namespace_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a namespace.

    Args:
        namespace_name (str): The name of the namespace.

    Returns:
        dict: Detailed namespace information.
    """
    ns = api_v1.read_namespace(name=namespace_name)
    
    return {
        "name": ns.metadata.name,
        "status": ns.status.phase,
        "labels": ns.metadata.labels,
        "annotations": ns.metadata.annotations,
        "creation_timestamp": str(ns.metadata.creation_timestamp)
    }


__all__ = [
    # Original functions
    "list_namespaces",
    "list_deployments_from_namespace",
    "list_pods_from_namespace",
    "list_services_from_namespace",
    "list_all_resources",
    
    # Describe/Get functions
    "describe_pod",
    "get_pod_logs",
    "describe_deployment",
    "describe_service",
    "describe_node",
    "get_namespace_details",
    
    # Additional listing functions
    "list_statefulsets_from_namespace",
    "list_daemonsets_from_namespace",
    "list_replicasets_from_namespace",
    "list_configmaps_from_namespace",
    "list_secrets_from_namespace",
    "list_jobs_from_namespace",
    "list_cronjobs_from_namespace",
    "list_ingresses_from_namespace",
    "list_persistent_volumes",
    "list_persistent_volume_claims_from_namespace",
    "list_nodes",
    
    # Events and filtering
    "get_events_from_namespace",
    "list_pods_with_labels",
    "get_pods_with_details",
    "get_resource_quotas_from_namespace"
]
