# ectop

`ectop` is a powerful Textual-based Terminal User Interface (TUI) for monitoring and controlling [ecFlow](https://ecflow.readthedocs.io/en/latest/) servers.

## Features

- **Real-time Monitoring**: View the status of your ecFlow suites, families, and tasks in a hierarchical tree view. The UI updates periodically to reflect the latest server state.
- **Node Management**: Perform common ecFlow operations directly from the TUI:
    - **Suspend/Resume**: Pause or continue execution of nodes.
    - **Kill**: Terminate running tasks.
    - **Force Complete**: Manually set a node to the complete state.
    - **Requeue**: Reset a node for execution.
- **File Inspection**: Quickly view logs, scripts, and generated job files:
    - **Log Output**: Live view of task logs with optional auto-refresh.
    - **Scripts**: View the original ecFlow script.
    - **Jobs**: Inspect the generated job file.
- **Search**: Interactive live search to find nodes in large suites.
- **Why?**: A dedicated "Why" inspector to understand why a node is in its current state (e.g., waiting for triggers).
- **Variable Management**: View and modify node variables (Edit and Add) on the fly.
- **Interactive Script Editing**: Edit scripts using your preferred local editor (via `$EDITOR`) and update them on the ecFlow server instantly.

## Installation

### Using Conda (Recommended)

Since `ecflow` is primarily distributed via Conda, this is the easiest way to get started:

```bash
conda env create -f environment.yml
conda activate ectop
```

### Using Pip

If you already have `ecflow` installed on your system:

```bash
pip install .
```

## Usage

Start `ectop` by running:

```bash
ectop
```

### Command Line Options

Currently, `ectop` defaults to connecting to `localhost:3141`. Future versions will support command-line arguments for host and port.

### Configuration

- **Editor**: `ectop` uses the `$EDITOR` environment variable for script editing. If not set, it defaults to `vi`.
- **Server**: It connects to `localhost:3141` by default.

### Key Bindings

| Key | Action |
|-----|--------|
| `q` | **Quit** the application |
| `r` | **Refresh** the entire suite tree from the server |
| `l` | **Load** Logs, Script, and Job files for the selected node |
| `s` | **Suspend** the selected node |
| `u` | **Resume** the selected node |
| `k` | **Kill** the selected task |
| `f` | **Force Complete** the selected node |
| `/` | Open **Search** box (Live search) |
| `w` | Open **Why?** inspector for the selected node |
| `e` | **Edit** the node script in your local editor and update server |
| `t` | **Toggle Live** log updates for the current node |
| `v` | View/Edit **Variables** for the selected node |

## Documentation

- [Tutorial](tutorial.md)
- [Architecture](architecture.md)
- [Reference](reference.md)
- [Contributing](contributing.md)
