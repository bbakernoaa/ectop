from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Static


class VariableTweaker(ModalScreen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("v", "close", "Close"),
        Binding("a", "add_variable", "Add Variable"),
        Binding("d", "delete_variable", "Delete Variable"),
    ]

    def __init__(self, node_path, client):
        super().__init__()
        self.node_path = node_path
        self.client = client

    def compose(self) -> ComposeResult:
        with Vertical(id="var_container"):
            yield Static(f"Variables for {self.node_path}", id="var_title")
            yield DataTable(id="var_table")
            yield Input(placeholder="Enter new value...", id="var_input")
            with Horizontal(id="var_actions"):
                yield Button("Close", variant="primary", id="close_btn")

    def on_mount(self) -> None:
        table = self.query_one("#var_table", DataTable)
        table.add_columns("Name", "Value", "Type")
        table.cursor_type = "row"
        self.refresh_vars()
        self.query_one("#var_input").add_class("hidden")

    def action_close(self) -> None:
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_btn":
            self.app.pop_screen()

    def refresh_vars(self):
        table = self.query_one("#var_table", DataTable)
        table.clear()

        try:
            self.client.sync_local()
            defs = self.client.get_defs()
            node = defs.find_abs_node(self.node_path)

            if not node:
                self.app.notify("Node not found", severity="error")
                return

            seen_vars = set()

            # User variables
            for var in node.variables:
                table.add_row(var.name(), var.value(), "User", key=var.name())
                seen_vars.add(var.name())

            # Generated variables
            for var in node.generated_variables:
                table.add_row(var.name(), var.value(), "Generated", key=var.name())
                seen_vars.add(var.name())

            # Inherited variables (climb up the tree)
            parent = node.parent
            while parent:
                for var in parent.variables:
                    # Only add if not already present (overridden)
                    if var.name() not in seen_vars:
                        table.add_row(var.name(), var.value(), f"Inherited ({parent.name()})", key=f"inh_{var.name()}")
                        seen_vars.add(var.name())
                parent = parent.parent

        except Exception as e:
            self.app.notify(f"Error fetching variables: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value
        if row_key.startswith("inh_"):
            self.app.notify("Cannot edit inherited variables directly. Add it to this node to override.", severity="warning")
            return

        # Check if it's generated
        # We'll just try to edit and see if the user wants to override it as a user variable

        self.selected_var_name = row_key
        input_field = self.query_one("#var_input", Input)
        input_field.remove_class("hidden")
        input_field.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "var_input":
            value = event.value
            try:
                if self.selected_var_name:
                    # Editing existing
                    self.client.alter(self.node_path, "add_variable", self.selected_var_name, value)
                    self.app.notify(f"Updated {self.selected_var_name}")
                else:
                    # Adding new (expecting name=value)
                    if "=" in value:
                        name, val = value.split("=", 1)
                        self.client.alter(self.node_path, "add_variable", name.strip(), val.strip())
                        self.app.notify(f"Added {name.strip()}")
                    else:
                        self.app.notify("Use name=value format to add", severity="warning")
                        return

                event.input.add_class("hidden")
                event.input.value = ""
                event.input.placeholder = "Enter new value..."
                self.refresh_vars()
                self.query_one("#var_table").focus()
            except Exception as e:
                self.app.notify(f"Error: {e}", severity="error")

    def action_add_variable(self):
        # For simplicity, I'll use a prompt or just another input
        # I'll implement a simple way to add: name=value
        input_field = self.query_one("#var_input", Input)
        input_field.placeholder = "Enter name=value to add"
        input_field.remove_class("hidden")
        input_field.focus()
        self.selected_var_name = None

    def action_delete_variable(self):
        table = self.query_one("#var_table", DataTable)
        row_index = table.cursor_row
        if row_index is not None:
            # Get row key
            row_key = list(table.rows.keys())[row_index].value
            if row_key.startswith("inh_"):
                 self.app.notify("Cannot delete inherited variables", severity="error")
                 return
            try:
                self.client.alter(self.node_path, "delete_variable", row_key)
                self.app.notify(f"Deleted {row_key}")
                self.refresh_vars()
            except Exception as e:
                self.app.notify(f"Error: {e}", severity="error")
