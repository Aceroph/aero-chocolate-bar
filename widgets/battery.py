from typing import Any, Dict, List
from gi.repository import Gtk, GLib  # type: ignore
import psutil


def setup(config: Dict[str, Any]) -> Gtk.Widget:
    widget = Gtk.Label()

    # Initial call
    tick(widget, config)

    GLib.timeout_add(config.get("interval", 5) * 1000, tick, widget, config)
    return widget


def tick(widget: Gtk.Widget, config: Dict[str, Any]) -> bool:
    battery = psutil.sensors_battery()

    if battery.power_plugged:
        icon = config.get("icon-plugged", "")
    else:
        icons: List[str] = config.get("icons", ["", "", "", "", ""])
        icon = icons[int(len(icons) * battery.percent / 100) - 1]

    format = config.get("format", "{icon} ")
    tooltip_format = config.get("tooltip_format", "{percentage} %")

    variables = {"icon": icon, "percentage": f"{min(100, battery.percent):.2f}"}

    widget.set_text(format.format(**variables))
    widget.set_tooltip_text(tooltip_format.format(**variables))
    return True
