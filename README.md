# MicroShell

## Overview
MicroShell is a simple command-line shell implemented in Python. It enables users to execute basic Unix commands, handle input and output redirection, run background tasks, and execute piped commands. The goal of this project is to gain experience working with POSIX system calls and process manipulation.

## Features
- **Execute Unix Commands**: Supports standard commands like `ls`, `cat`, `grep`, and others found in `/usr/bin/`.
- **Quit Command**: Typing `quit` terminates the shell.
- **Inspiration Command**: Typing `inspiration` prints an inspiring phrase stored in the `INSPIRATION` environment variable (default: "Dream big").
- **Background Execution**: Commands ending with `&` run in the background.
- **Command Execution from File**: If a file is specified as an argument, commands are read and executed line by line.
- **Change Directory (`cd`)**: Allows navigation between directories.
- **Input Redirection (`<`)**: Redirects input from a file.
- **Output Redirection (`>`)**: Redirects command output to a file.
- **Piping (`|`)**: Supports simple pipes to connect multiple commands.
- **Error Handling**: Displays informative error messages for invalid commands, missing files, and execution failures.

## Installation
MicroShell requires Python 3 to run. Install Python if you haven't already:
```sh
sudo apt install python3  # For Debian/Ubuntu
```
```sh
sudo dnf install python3  # For Fedora <3
```
```sh
brew install python3      # For macOS
```

## Usage
### Running MicroShell
To start the shell interactively, run:
```sh
python3 shell.py
```
To execute commands from a script file:
```sh
python3 shell.py script.txt
```

### Example Commands
#### Executing Unix Commands
```sh
ls -l
cat file.txt
```

#### Changing Directory
```sh
cd /home/user/Documents
```

#### Running Background Tasks
```sh
sleep 10 &
```

#### Input and Output Redirection
```sh
sort < input.txt > output.txt
```

#### Piping Commands
```sh
grep 'error' logs.txt | sort | uniq
```

#### Environment Variables
```sh
export INSPIRATION="Keep pushing forward"
inspiration  # Outputs: Keep pushing forward
```

## Error Handling
- **Command not found**: Displays `command not found` when an invalid command is entered.
- **Not executable**: If a file exists but is not executable, prints `not executable`.
- **Failed Commands**: If a command fails, prints `Program terminated: exit code n`.

