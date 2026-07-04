import tapps_launcher
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Termux Android Apps Launcher")

        # Initialize TappsLauncher
        tapps_launcher.load_cached_json()

        self.set_default_size(400, 600)
        self.set_border_width(10)

        # header bar and title
        header_bar = Gtk.HeaderBar(title="Termux Android Apps Launcher")
        header_bar.set_show_close_button(True)
        self.set_titlebar(header_bar)

        # scrolling vertical box to hold widgets
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_size_request(400, 600)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scrolled_window.add(vbox)
        
        # root box to hold scroll window so that it wont expand width of children
        root_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, halign=Gtk.Align.CENTER)
        root_box.pack_start(scrolled_window, False, False, 0)
        self.add(root_box)

        # Search bar to filter apps
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search for an app...")
        self.search_entry.connect("changed", self.on_search_changed, vbox)
        vbox.pack_start(self.search_entry, False, False, 0)


        # refresh button to rebuild cached JSON data and refresh the app list
        refresh_button = Gtk.Button(label="Refresh App List")
        refresh_button.connect("clicked", self.on_refresh_clicked, vbox)
        header_bar.pack_start(refresh_button)

        # iterate through the cached JSON data and create buttons for each app
        for package in tapps_launcher.config_data.get("packages", []):
            self._add_button(vbox, package)

    def on_refresh_clicked(self, button, vbox):
        tapps_launcher.rebuild_cached_data()
        
        self._clear_vbox(vbox)

        # Add buttons for apps in the newly rebuilt cached JSON data
        for package in tapps_launcher.config_data.get("packages", []):
            self._add_button(vbox, package)

        vbox.show_all()

    def on_search_changed(self, entry, vbox):
        self._clear_vbox(vbox)

        # Add buttons for apps that match the search text
        search_text = entry.get_text().lower()
        for package in tapps_launcher.config_data.get("packages", []):
            common_name = package.get("common_name", "").lower()
            package_name = package.get("package_name", "").lower()
            if search_text in common_name or search_text in package_name:
                self._add_button(vbox, package)

        vbox.show_all()

    def on_app_button_clicked(self, button, package):
        package_name = package.get("package_name", "")
        if package_name:
            tapps_launcher.run_app(package_name)
        else:
            print("Package name not found for the selected app.")
    
    def _clear_vbox(self, vbox):
        # Remove all existing buttons from the vbox
        # Starting from 1 to skip the search entry
        for child in vbox.get_children()[1:]:
            vbox.remove(child)

    def _add_button(self, vbox, package):
        # invalid data
        if package.get("package_name") is None:
            return

        button = Gtk.Button(label=package.get("common_name", "Unknown App"))
        button.connect("clicked", self.on_app_button_clicked, package)
        button.set_size_request(200, 50)

        # On hover, show the package name as a tooltip
        button.set_tooltip_text(package.get("package_name", "Unknown Package"))

        vbox.pack_start(button, False, False, 0)

if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()