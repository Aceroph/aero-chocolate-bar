from datetime import datetime
from typing import Any, Dict
from gi.repository import Gtk, GLib  # type: ignore


def setup(config: Dict[str, Any]) -> Gtk.Widget:
    widget = Gtk.MenuButton()

    # Initial call
    tick(widget, config)

    # Popover
    popover = Gtk.Popover()
    calendar = Gtk.Calendar()
    popover.set_child(calendar)

    widget.set_popover(popover)
    widget.set_direction(Gtk.ArrowType.NONE)

    # Call every second
    GLib.timeout_add(config.get("interval", 1) * 1000, tick, widget, config)
    return widget


def tick(widget: Gtk.Widget, config: Dict[str, Any]) -> bool:
    format = datetime.now().strftime(config.get("format", "%b %-d ~ %H:%M:%S"))
    widget.set_label(format)
    return True
