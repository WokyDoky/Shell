import os
import sys

def process_command(cmd, background=False):
    if not cmd.strip() or cmd.strip().startswith('#'):
        return

    cmd = cmd.strip()
    if cmd.lower() == "quit":
        print("Bye bye!")
        sys.exit(0)

    if cmd.lower() == "inspiration":
        if 'INSPIRATION' not in os.environ:
            os.environ['INSPIRATION'] = 'Dream big'
        print(os.environ['INSPIRATION'])
        return

    # Check for directory change.
    if cmd.startswith('cd '):
        try:
            # Extract the directory path from the command
            directory = cmd[3:].strip()
            if not directory:
                # If no directory is provided, change to the home directory
                directory = os.path.expanduser("~")
            os.chdir(directory)
            print(f"Changed directory to {os.getcwd()}")
            return
        except FileNotFoundError:
            print(f"Directory not found: {directory}")
            return
        except Exception as e:
            print(f"Error changing directory: {e}")
            return
    # Check if the command should run in the background
    background = cmd.endswith("&")
    if background:
        cmd = cmd[:-1].strip()  # Remove '&' from the command

    # Split commands by pipes
    commands = cmd.split("|")
    if not commands:
        print("No commands entered")
        return

    input_fd = None

    for i, command in enumerate(commands):
        args = command.strip().split()
        if not args:
            continue

        # Create a pipe if needed
        if i < len(commands) - 1:
            pipe_read, pipe_write = os.pipe()

        pid = os.fork()
        if pid == 0:  # Child process
            try:
                if input_fd is not None:
                    os.dup2(input_fd, 0)
                    os.close(input_fd)

                if i < len(commands) - 1:
                    os.dup2(pipe_write, 1)
                    os.close(pipe_read)
                    os.close(pipe_write)

                executable = f"/usr/bin/{args[0]}"
                os.execv(executable, args)
            except FileNotFoundError:
                print(f"Command not found: {args[0]}")
            except Exception as e:
                print(f"Error executing command: {e}")
            os._exit(1)

        else:  # Parent process
            if input_fd is not None:
                os.close(input_fd)

            if i < len(commands) - 1:
                os.close(pipe_write)
                input_fd = pipe_read

            # Wait for the child process unless it's a background task
            if not background:
                os.waitpid(pid, 0)
            else:
                print(f"Started background task with PID {pid}")

    print()

def main():
    # Check if a file is specified as a command-line argument
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as file:
                for line in file:
                    if not line.strip() or line.strip().startswith('#'):
                        continue
                    process_command(line)
        except FileNotFoundError:
            print(f"Error: File '{sys.argv[1]}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        while True:
            try:
                cmd = input("Enter a command: ").strip()
                process_command(cmd)
            except EOFError:
                print("\nBye bye!")
                break
            except KeyboardInterrupt:
                print("\nOperation interrupted")
                continue

if __name__ == '__main__':
    main()