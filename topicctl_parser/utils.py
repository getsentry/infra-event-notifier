import os

from typing import Any, Dict, List

SENTRY_REGION = os.getenv("SENTRY_REGION", "unknown")

def markdown_table_from_change(topic: List[Dict[str, Any]]) -> str:
    topic_name = topic['topic']
    action = topic['action']
    configs = """"""
    if action == "create":
        for config in topic['configEntries']:
                configs += f"{config['name']}={config['current']}, "
        # TODO: implement replicaAssignments/replicationFactor/numPartitions in ChangesTracker
        partition_count = str(topic['numPartitions']['current'])
        replica_assignments = ""
        replication_factor = str(topic['replicationFactor']['current'])
    elif action == "update":
        for config in topic['configEntries']:
            configs += f"{config['name']}: {config['current']} --> {config['updated']}, "
        # TODO: implement replicaAssignments/replicationFactor/numPartitions in ChangesTracker
        partition_count = f"{topic['numPartitions']['current']} --> {topic['numPartitions']['updated']}"
        replica_assignments = ""
        replication_factor = f"{topic['replicationFactor']['current']} --> {topic['replicationFactor']['updated']}"
    else:
        raise AttributeError("Invalid action key, must be \'create\' or \'update\'")
    table = f"""|||
|:--------------------------:|-|
| **Topic Name**             |{topic_name}|
| **Action (create/update)** |{action}|
|         **Configs**        |{configs}|
|     **Partition Count**    |{partition_count}|
| **Partition Reassignment** |{replica_assignments}|
|   **Replication Factor**   |{replication_factor}|"""

    return f"%%%\n{table}\n%%%"
