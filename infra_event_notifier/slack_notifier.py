from infra_event_notifier.backends.slack import send_notification


class SlackNotifier:
    """
    Class that supports sending Slack messages.
    A URL for eng-pipes and eng-pipes secret key are required.
    """

    def __init__(self, eng_pipes_key: str, eng_pipes_url: str) -> None:
        self.eng_pipes_key = eng_pipes_key
        self.eng_pipes_url = eng_pipes_url

    def send(self, title: str, body: str) -> None:
        """
        Sends the message to slack
        """
        assert self.eng_pipes_key is not None, "Missing Eng-Pipes Signing Key"
        assert self.eng_pipes_url is not None, "Missing Eng-Pipes API URL"

        if self.eng_pipes_url == "":  # For tests, to avoid sending them out
            return

        send_notification(
            title=title,
            text=body,
            eng_pipes_key=self.eng_pipes_key,
            eng_pipes_url=self.eng_pipes_url,
        )
