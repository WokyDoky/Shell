import os
import sys
import re


def execute_command(command, background=False):
    pid = os.fork()
    if pid == 0:
        # Child process
        try:
            # Split command into parts
            args = re.split(r'\s+', command)
            # Handle input/output redirection
            if '>' in args:
                index = args.index('>')
                output_file = args[index + 1]
                args = args[:index]
                os.close(1)  # Close stdout
                os.open(output_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
            if '<' in args:
                index = args.index('<')
                input_file = args[index + 1]
                args = args[:index]
                os.close(0)  # Close stdin
                os.open(input_file, os.O_RDONLY)
            # Execute the command
            os.execvp(args[0], args)
        except FileNotFoundError:
            print("command not found")
            sys.exit(1)
        except PermissionError:
            print("not executable")
            sys.exit(1)
        except Exception as e:
            print(f"Program terminated: exit code {e}.")
            sys.exit(1)
    else:
        # Parent process
        if not background:
            os.waitpid(pid, 0)


def change_directory(path):
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"Directory not found: {path}")


def handle_pipe(command):
    commands = command.split('|')
    prev_read_fd = None
    for cmd in commands:
        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if pid == 0:
            # Child process
            if prev_read_fd is not None:
                os.dup2(prev_read_fd, 0)
                os.close(prev_read_fd)
            os.dup2(write_fd, 1)
            os.close(write_fd)
            execute_command(cmd.strip())
            sys.exit(0)
        else:
            # Parent process
            os.close(write_fd)
            if prev_read_fd is not None:
                os.close(prev_read_fd)
            prev_read_fd = read_fd
    # Wait for the last command
    os.waitpid(pid, 0)


def main():
    while True:
        command = input("microshell> ").strip()
        if command == "quit":
            break
        elif command == "inspiration":
            phrase = os.environ.get("phrase", "Believe in yourself")
            print(phrase)
        elif command.startswith("cd "):
            change_directory(command[3:])
        elif '|' in command:
            handle_pipe(command)
        else:
            background = command.endswith('&')
            if background:
                command = command[:-1].strip()
            execute_command(command, background)

        # Ensure the prompt is printed on a new line after command execution
        print()  # Print a newline after command execution


if __name__ == "__main__":
    main()