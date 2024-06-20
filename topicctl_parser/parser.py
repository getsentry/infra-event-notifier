import json

from subprocess import Popen, PIPE
from pprint import pprint

from notifications.datadog import SENTRY_REGION, markdown_table_from_change, report_event_to_datadog


def main():
    p = Popen(['topicctl', 'apply', '/topicctl-config/topic-kafka-001-*.yaml', "--cluster-config", "/topicctl-config/cluster-kafka-001.yaml", '--json-output', '--dry-run'], stdout=PIPE, text=True)
    # p = Popen(['topicctl', 'apply', 'examples/local-cluster/topics/topic-default*.yaml', '--json-output', '--dry-run'], stdout=PIPE, text=True)
    # read stdout from subprocess
    data = p.communicate()[0]
    if not data:
        exit()
    dataSplit = data.splitlines()
    for line in dataSplit:
        dataJson = json.loads(line)
        dry_run = "Dry run: " if dataJson["dryRun"] else ""
        tags = {
            "source": "topicctl",
            "source_category": "infra_tools",
            "sentry_region": SENTRY_REGION,
        }
        changes_by_action = sorted(dataJson['changes'], key=lambda topic: topic['action'])
        for change in changes_by_action:
            title = f"{dry_run}Topicctl ran apply on topic {change['topic']} in region {SENTRY_REGION}"
            text = markdown_table_from_change(change)
            if len(text) > 3950:
                text = "Changes exceed 4000 character limit, check topicctl logs for details on changes"
            tags["topicctl_topic"] = change["topic"]
            report_event_to_datadog(title, text, tags)


if __name__ == "__main__":
    main()
