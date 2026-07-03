import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Termux Android Apps Launcher")
        self.set_default_size(400, 300)

        # Create a button
        button = Gtk.Button(label="Click Me")
        button.connect("clicked", self.on_button_clicked)

        # Add the button to the window
        self.add(button)

    def on_button_clicked(self, widget):
        print("Button clicked!")

if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()