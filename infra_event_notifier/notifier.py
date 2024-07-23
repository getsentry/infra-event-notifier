from typing import Self


class Notifier:
    def __init__(self) -> None:
        # Notification fields
        self.title: None | str = None
        self.body: None | str = None

    def set_title(self, title: str) -> Self:
        """
        (Required) Title for the event

        Args:
            title (str): Event title
        """
        self.title = title
        return self

    def set_body(self, text: str) -> Self:
        """
        (Required) Main body of the event

        Args:
            text (str): Event body text
        """
        self.body = text
        return self
