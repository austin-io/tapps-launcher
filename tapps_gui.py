import tapps_launcher
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Termux Android Apps Launcher")

        # Initialize TappsLauncher
        tapps_launcher.load_cached_json()

        self.set_default_size(500, 600)
        self.set_border_width(10)

        # header bar and title
        header_bar = Gtk.HeaderBar(title="Termux Android Apps Launcher")
        header_bar.set_show_close_button(True)
        self.set_titlebar(header_bar)
        
        # root box to hold scroll window so that it wont expand width of children
        root_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, halign=Gtk.Align.CENTER)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        #root_box.pack_start(scrolled_window, True, True, 0)
        root_box.pack_start(vbox, True, True, 0)
        self.add(root_box)

        # list box instead of vbox to hold buttons for better performance with many apps
        list_box = Gtk.ListBox()

        # Search bar to filter apps
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search for an app...")
        self.search_entry.connect("search-changed", self.on_search_changed, list_box)
        vbox.pack_start(self.search_entry, False, False, 0)
        
        # scrolling vertical box to hold widgets
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_size_request(500, 600)
        
        scrolled_window.add(list_box)
        vbox.pack_start(scrolled_window, True, True, 0)

        # refresh button to rebuild cached JSON data and refresh the app list
        refresh_button = Gtk.Button(label="Refresh App List")
        refresh_button.connect("clicked", self.on_refresh_clicked, list_box)
        header_bar.pack_start(refresh_button)

        # iterate through the cached JSON data and create buttons for each app
        for package in tapps_launcher.config_data.get("packages", []):
            self._add_button(list_box, package)

    def on_refresh_clicked(self, button, list_box):
        tapps_launcher.rebuild_cached_data()
        
        self._clear_buttons(list_box)

        # Add buttons for apps in the newly rebuilt cached JSON data
        for package in tapps_launcher.config_data.get("packages", []):
            self._add_button(list_box, package)

        list_box.show_all()

    def on_search_changed(self, entry, list_box):
        self._clear_buttons(list_box)

        # Add buttons for apps that match the search text
        search_text = entry.get_text().lower()
        for package in tapps_launcher.config_data.get("packages", []):
            common_name = package.get("common_name", "").lower()
            package_name = package.get("package_name", "").lower()
            if search_text in common_name or search_text in package_name:
                self._add_button(list_box, package)

        list_box.show_all()

    def on_app_button_clicked(self, button, package):
        package_name = package.get("package_name", "")
        if package_name:
            tapps_launcher.run_app(package_name)
        else:
            print("Package name not found for the selected app.")
    
    def _clear_buttons(self, list_box):
        # Remove all existing buttons from the list_box
        # Starting from 1 to skip the search entry
        for child in list_box.get_children():
            list_box.remove(child)

    def _add_button(self, list_box, package):
        # invalid data
        if package.get("package_name") is None:
            return

        button = Gtk.Button(label=package.get("common_name", "Unknown App"))
        button.connect("clicked", self.on_app_button_clicked, package)
        button.set_size_request(200, 50)

        # On hover, show the package name as a tooltip
        button.set_tooltip_text(package.get("package_name", "Unknown Package"))

        # list box row
        list_box_row = Gtk.ListBoxRow()
        list_box_row.add(button)
        
        list_box_row.set_margin_top(10)
        list_box_row.set_margin_bottom(10)
        list_box_row.set_margin_start(10)
        list_box_row.set_margin_end(10)

        list_box.add(list_box_row)

        #list_box.add(button)

if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()