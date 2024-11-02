from typing import Any, Dict
import gi
from ctypes import CDLL
import json
from pathlib import Path

CDLL("libgtk4-layer-shell.so")

try:
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk, Gdk  # type: ignore
    from gi.repository import Gtk4LayerShell as LayerShell  # type: ignore
except ImportError or ValueError as err:
    print(err)
    gi.sys.exit(1)


class App(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config: Dict[str, Any]
        config_path = next(Path(__file__).parent.glob("*.json"))
        with open(config_path, "r") as file:
            self.config = json.load(file)
            file.close()

        self.display = Gdk.Display.get_default()

    def get_widget(self, name: str, config: Dict[str, Any]) -> Gtk.Widget:
        widget_import = __import__("widgets", globals(), locals(), [name], 0)
        widget = getattr(widget_import, name).setup(config)
        del widget_import
        return widget

    def load_css(self) -> None:
        css_path = self.config.get("style", "style.css")
        if css_path:
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                self.display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

    def process_config(self) -> Gtk.CenterBox:
        bar_widgets = Gtk.CenterBox()
        bar_widgets.add_css_class("bar")

        sections = {"left": Gtk.Box(), "center": Gtk.Box(), "right": Gtk.Box()}

        # Instantiate widgets
        for position, widgets in self.config.items():
            if widgets != {} and isinstance(widgets, dict):
                for widget_name, widget_config in widgets.items():
                    widget = self.get_widget(widget_name, widget_config)
                    widget.add_css_class("widget")

                    sections[position.lower()].append(widget)

                match position.lower():
                    case "left":
                        bar_widgets.set_start_widget(sections[position.lower()])
                    case "center":
                        bar_widgets.set_center_widget(sections[position.lower()])
                    case "right":
                        bar_widgets.set_end_widget(sections[position.lower()])

        return bar_widgets

    def on_activate(self, _):
        monitor = self.display.get_monitors()[0]
        width = monitor.get_geometry().width

        window = Gtk.ApplicationWindow(application=app)
        window.set_default_size(width, 32)

        LayerShell.init_for_window(window)
        LayerShell.set_layer(window, LayerShell.Layer.TOP)
        LayerShell.set_anchor(window, LayerShell.Edge.TOP, True)
        LayerShell.auto_exclusive_zone_enable(window)

        bar_widget = self.process_config()
        window.set_child(bar_widget)

        self.load_css()
        window.present()


app = App()
app.connect("activate", app.on_activate)
app.run(None)
