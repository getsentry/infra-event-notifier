from infra_event_notifier.backends.slack import send_notification


class SlackNotifier:
    """
    Class that supports sending Slack messages.
    A URL for eng-pipes and eng-pipes secret key are required.
    """

    def __init__(self, eng_pipes_key: str, eng_pipes_url: str) -> None:
        self.eng_pipes_key = eng_pipes_key
        self.eng_pipes_url = eng_pipes_url

    def send(self, title: str, body: str, channel_id: str) -> None:
        """
        Sends the message to slack
        """
        assert self.eng_pipes_key is not None, "Missing Eng-Pipes Signing Key"
        assert self.eng_pipes_url is not None, "Missing Eng-Pipes API URL"
        assert channel_id is not None, "Missing Slack Channel ID"

        if (
            self.eng_pipes_url == "" or channel_id == ""
        ):  # For tests, to avoid sending them out
            return

        send_notification(
            title=title,
            text=body,
            channel_id=channel_id,
            eng_pipes_key=self.eng_pipes_key,
            eng_pipes_url=self.eng_pipes_url,
        )


# Remove before committing
if __name__ == "__main__":
    notif = SlackNotifier(
        "", "http://localhost:3000/metrics/infra-event-notifier/webhook"
    )
    notif.send("Test Title", "Test Body__", "C07EKV0T2E6")
