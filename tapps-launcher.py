import sys
import subprocess
import json
import os

# JSON data structure to hold cached package information. Structure: {"packages": [{"common_name": "App Name", "package_name": "com.example.app"}, ...]}
config_data = {}
config_json_path = "~/.config/tapps-launcher/config.json"

list_packages_command_prefix = "cmd package list packages"
launch_app_command_prefix = "am start -p"

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
    try:
        result = subprocess.run(list_packages_command_prefix.split(), capture_output=True, text=True)
        if result.returncode == 0:
            packages = result.stdout.strip().splitlines()
            for package in packages:
                print(package)
        else:
            print("Error listing packages:", result.stderr)
    except Exception as e:
        print("An error occurred while listing packages:", str(e))

def run_app(package_name):
    try:
        matching_apps = find_app(package_name)
        if not matching_apps:
            print(f"No matching apps found for '{package_name}'.")
            sys.exit(1)
        
        command = f"{launch_app_command_prefix} {matching_apps[0]['package_name']}"

        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully launched {package_name}")
        else:
            print(f"Error launching {package_name}: {result.stderr}")
    except Exception as e:
        print(f"An error occurred while launching {package_name}: {str(e)}")

def find_app(app_name):
    # Search app in cached JSON file
    matching_apps = []
    for package in config_data.get("packages", []):
        if app_name.lower() in package.lower():
            matching_apps.append(package)

    return matching_apps

def load_cached_json():
    # Load cached JSON data from config file

    # If file not found, create directory and empty file, then rebuild cached data
    if not os.path.exists(os.path.expanduser(config_json_path)):
        os.makedirs(os.path.dirname(os.path.expanduser(config_json_path)), exist_ok=True)
        with open(os.path.expanduser(config_json_path), 'w') as f:
            json.dump({"packages": []}, f, indent=4)

        rebuild_cached_data()

    global config_data
    try:
        with open(config_json_path, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found at {config_json_path}. Please run the rebuild command.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {config_json_path}. Please check the file format.")

def rebuild_cached_data():
    # Rebuild cached data by listing packages and saving to JSON file
    try:
        result = subprocess.run(list_packages_command_prefix.split(), capture_output=True, text=True)
        if result.returncode == 0:
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
            package_list = [{"common_name": common_name, "package_name": package} for common_name, package in zip(common_names, packages)]
            
            #os.makedirs(os.path.dirname(os.path.expanduser(config_json_path)), exist_ok=True)
            with open(config_json_path, 'w') as f:
                # Read each entry and only update new packages to the config_data
                if os.path.exists(os.path.expanduser(config_json_path)):
                    with open(config_json_path, 'r') as existing_file:
                        try:
                            existing_data = json.load(existing_file)
                        except json.JSONDecodeError:
                            existing_data = {"packages": []}
                else:
                    existing_data = {"packages": []}
                
                # Merge existing packages with new packages, avoiding duplicates
                existing_packages = set(existing_data.get("packages", []))
                new_packages = set(package_list)
                merged_packages = list(existing_packages.union(new_packages))
                json.dump(merged_packages, f, indent=4)

            print(f"Cached data rebuilt and saved to {config_json_path}.")
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