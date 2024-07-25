from infra_event_notifier.backends.slack import send_notification


class SlackNotifier:
    def __init__(self, slack_api_key: str) -> None:
        self.slack_api_key = slack_api_key

    def send(self, title: str, body: str) -> None:
        """
        Sends the notification
        """
        # TODO: implement
        if self.slack_api_key is not None and title and body:
            send_notification(
                title=title, text=body, slack_api_key=self.slack_api_key
            )
