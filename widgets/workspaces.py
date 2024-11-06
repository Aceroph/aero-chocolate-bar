from typing import Any, Dict
import json
import os

from gi.repository import Gtk, GLib  # type: ignore

last_active: int = 0


def setup(config: Dict[str, Any]) -> Gtk.Widget:
    workspaces_widget = Gtk.Box()
    workspaces_widget.set_name("workspaces")

    labels = config.get("format")

    for id in range(1, 11):
        label = labels[id - 1] if labels and id < len(labels) else str(id)

        workspace_widget = Gtk.Button()
        workspace_widget.set_label(label)
        workspace_widget.connect("clicked", change_workspace, id)

        workspaces_widget.append(workspace_widget)

    update_workspaces(workspaces_widget, config)

    # Call every second
    GLib.timeout_add(
        config.get("interval", 1) * 1000, update_workspaces, workspaces_widget, config
    )

    return workspaces_widget


def change_workspace(_: Gtk.Button, workspace: int) -> None:
    os.popen(f"hyprctl dispatch workspace {workspace}")


def update_workspaces(widget: Gtk.Widget, config: Dict[str, Any]) -> bool:
    active = json.loads(os.popen("hyprctl -j activeworkspace").read())["id"]

    global last_active
    if active != last_active:
        workspaces = json.loads(os.popen("hyprctl -j workspaces").read())
        workspace_ids = [int(workspace["id"]) for workspace in workspaces]

        id = 0
        workspace = widget.get_first_child()
        while workspace:
            id += 1

            if config.get("hide-inactive", True) and id not in workspace_ids:
                workspace.set_visible(False)
            else:
                workspace.set_visible(True)

            if id == active:
                workspace.add_css_class("active")
            else:
                workspace.remove_css_class("active")

            workspace = workspace.get_next_sibling()

        last_active = active

    return True
