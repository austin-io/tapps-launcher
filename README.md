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
tapps-launcher
tapps-launcher -h
tapps-launcher --help
```

### Run

Run an app using `-r/--run`. You don't need the full package name, `tapps-launcher` will search for the app name.

```
tapps-launcher -r firefox
tapps-launcher --run mozilla
```

### Search

Search for installed apps with `-s/--search` using a keyword.

```
tapps-launcher -s firefox
tapps-launcher --search mozilla
```

### List

List all the available apps using `-l/--list`.

```
tapps-launcher -l
tapps-launcher --list
```

## GUI Usage

> ***WORK IN PROGRESS***
>
> IMPORTANT NOTE: YOU MUST CHANGE TERMUX SETTINGS TO ALWAYS SHOW ON TOP OR ELSE ANDROID APPS WONT LAUNCH

Launch the GTK app in an X11 environment using `tapps-gui`.

