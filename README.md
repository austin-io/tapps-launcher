# Termux Android Apps Launcher

Launch and Search for Android apps from withing Termux and Termux-X11

## Key Features

- Launch apps directly from Termux without needing to know the full package name
- List all installed apps, with dynamically generated Labels
- Search all installed apps
- GUI app written in Python GTK to launch apps straight from Termux X11 environment (WIP)

## CLI Usage

### Help

Show help options

```
tapps_launcher
tapps_launcher -h
tapps_launcher --help
```

### Run

Run an app using `-r/--run`. You don't need the full package name, `tapps_launcher` will search for the app name.

```
tapps_launcher -r firefox
tapps_launcher --run mozilla
```

### Search

Search for installed apps with `-s/--search` using a keyword.

```
tapps_launcher -s firefox
tapps_launcher --search mozilla
```

### List

List all the available apps using `-l/--list`.

```
tapps_launcher -l
tapps_launcher --list
```

## GUI Usage

> ***WORK IN PROGRESS***
>
> IMPORTANT NOTE: YOU MUST CHANGE TERMUX SETTINGS TO ALWAYS SHOW ON TOP OR ELSE ANDROID APPS WONT LAUNCH

Launch the GTK app in an X11 environment using `tapps_gui`.

