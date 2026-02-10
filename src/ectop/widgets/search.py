from textual.binding import Binding
from textual.widgets import Input


class SearchBox(Input):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel Search"),
        Binding("enter", "submit", "Search Next"),
    ]

    def action_cancel(self):
        self.value = ""
        self.remove_class("visible")
        self.app.set_focus(self.app.query_one("#suite_tree"))

    def on_blur(self):
        self.remove_class("visible")
