# Architecture

`ectop` is built using the [Textual](https://textual.textualize.io/) framework, providing a modern and responsive TUI experience.

## Design Goals

1.  **Responsiveness**: The UI should never freeze, even when performing long-running network operations or fetching large files.
2.  **Simplicity**: Provide a clean wrapper around the `ecflow` Python API.
3.  **Extensibility**: Modular widget design for easy expansion of features.

## Core Components

### App (`ectop.app.Ectop`)
The main application class that coordinates the UI, handles global key bindings, and manages the lifecycle of the application. It uses Textual's `Screen` and `Worker` systems to handle concurrency.

### Client (`ectop.client.EcflowClient`)
A thin wrapper around `ecflow.Client`. It provides:
- Simplified API for common operations.
- Centralized error handling and conversion of `RuntimeError` into more informative exceptions.
- Mapping of node states to visual icons.

### Widgets (`ectop.widgets`)
The UI is decomposed into several modular widgets:
- **SuiteTree**: A customized `Tree` widget that displays the hierarchical structure of ecFlow suites. It uses **lazy loading** to only fetch and render nodes as they are expanded, ensuring high performance for large trees.
- **StatusBar**: Displays real-time server connection status and the timestamp of the last successful synchronization.
- **MainContent**: A `TabbedContent` widget that hosts the Log, Script, and Job views.
- **SearchBox**: A specialized input for live-filtering the suite tree.
- **Modals**: Lightweight screens for confirmation (`ConfirmModal`), variable editing (`VariableTweaker`), and "Why" inspection (`WhyInspector`).

## Concurrency and Workers

To maintain a smooth UI, all blocking calls to the ecFlow server (which involve network I/O) are offloaded to **Textual Workers** using the `@work` decorator.

- **Thread-safe Updates**: Workers that need to update the UI use `self.call_from_thread()` or Textual's message-passing system.
- **Exclusive Workers**: Operations like "Refresh" use `exclusive=True` to prevent multiple simultaneous sync operations.

## Event Loop

`ectop` uses a periodic interval (set in `on_mount`) to perform "live" updates, such as tailing log files when a node is active and the "Live" toggle is enabled.
