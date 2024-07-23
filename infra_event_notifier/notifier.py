import os
from typing import Mapping, Self


class Notifier:
    def __init__(self) -> None:

        # Notification fields
        self.title = None
        self.body = None
    
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

