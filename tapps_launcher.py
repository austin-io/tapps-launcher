import sys
import subprocess
import json
import os

debug = False  # Set to True to enable debug output
debug_data = """package:com.example.app
package:com.other.app
package:com.foo.app
package:com.bar.app
package:com.baz.app"""

# JSON data structure to hold cached package information. Structure: {"packages": [{"common_name": "App Name", "package_name": "com.example.app"}, ...]}
config_data = {}
config_json_path = os.path.expanduser("~/.config/tapps-launcher/")
json_data_file_name = "data.json"
json_file_path = os.path.expanduser(os.path.join(config_json_path, json_data_file_name))

list_packages_command_prefix = "cmd package list packages"
launch_app_command_prefix = "am start"
main_activity_suffix = "/.MainActivity"

def print_help():
    help_text = """
Termux Android Apps Launcher
Usage:
    tapps-launcher [OPTIONS] [PACKAGE_NAME] 
Options:
    -h --help          Show this help message and exit
    -l --list          List available Android apps
    -r --run <app>     Launch the specified Android app
    -s --search <app>  Search for Android apps
    -b --rebuild       Rebuild cached apps data. Run this if app list is out of date."""

    print(help_text)

def show_app_list():
    # List available Android apps from cached JSON data
    if not config_data.get("packages"):
        _make_config_dir()
        rebuild_cached_data()
    
    for package in config_data.get("packages", []):
        print(package.get("common_name", "Unknown App"), "-", package.get("package_name", "Unknown Package"))

def run_app(package_name):
    try:
        matching_apps = find_app(package_name)
        if not matching_apps:
            print(f"No matching apps found for '{package_name}'.")
            sys.exit(1)
        
        command = f"{launch_app_command_prefix} {matching_apps[0]['package_name']}"
        if debug:
            print(f"Debug: Running command: {command}")
            return

        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully launched {package_name}")
        else:
            print(f"Error launching {package_name}: {result.stderr}")
            print("Trying again using Main Activity")
            command = command + main_activity_suffix
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully launched {package_name} using Main Activity")
            else:
                print(f"Error launching {package_name} using Main Activity: {result.stderr}")
                
    except Exception as e:
        print(f"An error occurred while launching {package_name}: {str(e)}")

def find_app(app_name):
    # Search app in cached JSON file
    matching_apps = []
    for package in config_data.get("packages", []):
        common_name = package.get("common_name", "").lower()
        package_name = package.get("package_name", "").lower()
        if app_name.lower() in common_name or app_name.lower() in package_name:
            matching_apps.append(package)

    return matching_apps

def _make_config_dir():
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(config_json_path), exist_ok=True)
    
    # Create empty JSON file if it doesn't exist
    if not os.path.exists(json_file_path):
        with open(json_file_path, 'w') as f:
            json.dump({"packages": []}, f, indent=4)

def load_cached_json():
    # Load cached JSON data from config file

    # If file not found, create directory and empty file, then rebuild cached data
    if not os.path.exists(json_file_path):
        _make_config_dir()
        rebuild_cached_data()

    global config_data
    try:
        with open(json_file_path, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found at {json_file_path}. Please run the rebuild command.")
        pass
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {json_file_path}. Please check the file format.")
        pass

def rebuild_cached_data():
    # Rebuild cached data by listing packages and saving to JSON file
    
    try:
        result = None
        if not debug:
            result = subprocess.run(list_packages_command_prefix.split(), capture_output=True, text=True)

        if debug or result.returncode == 0:
            if debug:
                print("Debug: Using debug data for package list.")
                packages = debug_data.strip().splitlines()
            else:
                packages = result.stdout.strip().splitlines()

            # Parse out "package:" prefix from each line
            packages = [pkg.replace("package:", "") for pkg in packages]

            # Generate common names for each package.
            # Split package name by '.' and take the last 2 parts as common name.
            common_names = []
            for pkg in packages:
                parts = pkg.split('.')
                if len(parts) >= 2:
                    common_name = ' '.join(parts[-2:]).title()
                else:
                    common_name = pkg.title()
                common_names.append(common_name)
            
            # Create a list of dictionaries with common_name and package_name
            new_data = [{"common_name": common_name, "package_name": package} for common_name, package in zip(common_names, packages)]
            
            existing_json = {}
            with open(json_file_path, 'r') as json_file:
                try:
                    existing_json = json.load(json_file)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {json_file_path}. Overwriting with new data.")

            with open(json_file_path, 'w') as json_file:
                # Merge existing packages with new packages, avoiding duplicates
                old_data = [{"common_name": pkg["common_name"], "package_name": pkg["package_name"]} for pkg in existing_json.get("packages", [])]
                final_json_data = {"packages": old_data + [pkg for pkg in new_data if pkg not in old_data]}
                json.dump(final_json_data, json_file, indent=4)

            print(f"Cached data rebuilt and saved to {json_file_path}.")
        else:
            print("Error rebuilding cached data:", result.stderr)
    except Exception as e:
        print("An error occurred while rebuilding cached data:", str(e))

def main():
    
    # Get cli arguments
    args = sys.argv[1:]

    # Load cached json file
    load_cached_json()
    
    if len(args) == 0:
        print("No arguments provided. Use --help for usage information.")
        print_help()
        sys.exit(1)
    
    if "--help" in args or "-h" in args:
        print_help()
        sys.exit(0)
    
    if "--list" in args or "-l" in args:
        # List available Android apps
        print("Listing available Android apps...")
        show_app_list()

        sys.exit(0)
    
    if "--run" in args or "-r" in args:
        # Launch the specified Android app
        run_app(_get_arg_input(args, ["--run", "-r"]))

        sys.exit(0)
    
    if "--search" in args or "-s" in args:
        # Search for Android apps
        search_term = _get_arg_input(args, ["--search", "-s"])
        matching_apps = find_app(search_term)
        if matching_apps:
            print(f"Found {len(matching_apps)} matching apps:")
            for app in matching_apps:
                print(app.get("common_name", "Unknown App"), "-", app.get("package_name", "Unknown Package"))
        else:
            print(f"No matching apps found for '{search_term}'.")

        sys.exit(0)
    
    if "--rebuild" in args or "-b" in args:
        # Rebuild cached apps data
        rebuild_cached_data()
        sys.exit(0)

def _get_arg_input(args, arg_list):
    for arg in arg_list:
        if arg in args:
            return args[args.index(arg) + 1]
    
if __name__ == "__main__":
    main()