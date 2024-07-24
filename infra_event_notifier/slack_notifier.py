from infra_event_notifier.backends.slack import send_notification
from infra_event_notifier.notifier import Notifier


class SlackNotifier(Notifier):
    def __init__(self, title: str, body: str, slack_api_key: str) -> None:
        super().__init__(title, body)
        self.slack_api_key = slack_api_key

    def send(self) -> None:
        """
        Sends the notification
        """
        # TODO: implement
        if self.slack_api_key is not None and self.title and self.body:
            send_notification(
                title=self.title,
                text=self.body,
                slack_api_key=self.slack_api_key,
            )
