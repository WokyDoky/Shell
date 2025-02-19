import os
import sys
import re


class MiniShell:
    def __init__(self):
        self.running = True

    def parse_command(self, command):
        """Parse command for redirections, pipes, and background execution."""
        parts = re.split(r'\s+', command.strip())
        cmd_parts = {'args': [], 'input': None, 'output': None,
                     'pipe': None, 'background': False}

        i = 0
        while i < len(parts):
            if parts[i] == '<':
                i += 1
                if i < len(parts):
                    cmd_parts['input'] = parts[i]
            elif parts[i] == '>':
                i += 1
                if i < len(parts):
                    cmd_parts['output'] = parts[i]
            elif parts[i] == '|':
                cmd_parts['pipe'] = ' '.join(parts[i + 1:])
                break
            elif parts[i] == '&':
                cmd_parts['background'] = True
                break
            else:
                cmd_parts['args'].append(parts[i])
            i += 1

        return cmd_parts

    def execute_command(self, cmd_parts):
        """Execute the command with the given parts."""
        if not cmd_parts['args']:
            return

        cmd = cmd_parts['args'][0]

        # Handle built-in commands
        if cmd == 'quit':
            self.running = False
            return
        elif cmd == 'cd':
            if len(cmd_parts['args']) > 1:
                try:
                    os.chdir(cmd_parts['args'][1])
                except FileNotFoundError:
                    print(f"Directory not found: {cmd_parts['args'][1]}")
            return
        elif cmd == 'inspiration':
            phrase = os.environ.get('phrase', 'No inspiration set!')
            print(phrase)
            return

        # Check if command exists in /bin or current directory
        executable = None
        if os.path.isfile(f"/bin/{cmd}") and os.access(f"/bin/{cmd}", os.X_OK):
            executable = f"/bin/{cmd}"
        elif os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            executable = f"./{cmd}"

        if not executable:
            print("command not found")
            return

        # Handle pipe
        pipe_read, pipe_write = None, None
        if cmd_parts['pipe']:
            pipe_read, pipe_write = os.pipe()

        # Fork and execute
        pid = os.fork()
        if pid == 0:  # Child process
            try:
                # Handle input redirection
                if cmd_parts['input']:
                    fd = os.open(cmd_parts['input'], os.O_RDONLY)
                    os.dup2(fd, 0)
                    os.close(fd)

                # Handle output redirection
                if cmd_parts['output']:
                    fd = os.open(cmd_parts['output'], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                    os.dup2(fd, 1)
                    os.close(fd)

                # Handle pipe
                if pipe_write is not None:
                    os.dup2(pipe_write, 1)
                    os.close(pipe_read)
                    os.close(pipe_write)

                # Execute the command
                if executable.startswith('./'):
                    cmd_parts['args'][0] = executable
                os.execv(executable, cmd_parts['args'])
            except Exception as e:
                print(f"Error executing command: {e}")
                os._exit(1)

        # Parent process
        if pipe_write is not None:
            os.close(pipe_write)

            # Fork and execute the piped command
            pipe_pid = os.fork()
            if pipe_pid == 0:  # Child for pipe
                os.dup2(pipe_read, 0)
                os.close(pipe_read)

                pipe_parts = self.parse_command(cmd_parts['pipe'])
                pipe_cmd = pipe_parts['args'][0]

                # Check pipe command in /bin or current directory
                pipe_executable = None
                if os.path.isfile(f"/bin/{pipe_cmd}") and os.access(f"/bin/{pipe_cmd}", os.X_OK):
                    pipe_executable = f"/bin/{pipe_cmd}"
                elif os.path.isfile(pipe_cmd) and os.access(pipe_cmd, os.X_OK):
                    pipe_executable = f"./{pipe_cmd}"
                    pipe_parts['args'][0] = pipe_executable

                if pipe_executable:
                    os.execv(pipe_executable, pipe_parts['args'])
                else:
                    print("Pipe command not found")
                    os._exit(1)

            os.close(pipe_read)
            os.waitpid(pipe_pid, 0)

        # Wait for child process unless it's a background task
        if not cmd_parts['background']:
            _, status = os.waitpid(pid, 0)
            exit_code = status >> 8

            # Special handling for grep exit codes
            if cmd == 'grep' and exit_code == 1:
                # Don't treat grep's "no matches found" as an error
                if '-c' in cmd_parts['args']:
                    # For grep -c, ensure we print 0 when no matches are found
                    if 'output' not in cmd_parts:
                        print("0")
            elif exit_code != 0:
                print(f"Program terminated: exit code {exit_code}")

    def run(self):
        """Main shell loop."""
        while self.running:
            try:
                if len(sys.argv) > 1:  # Batch mode
                    with open(sys.argv[1], 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                print(f"$ {line}")
                                cmd_parts = self.parse_command(line)
                                self.execute_command(cmd_parts)
                    break
                else:  # Interactive mode
                    command = input('$ ')
                    if command.strip():
                        cmd_parts = self.parse_command(command)
                        self.execute_command(cmd_parts)
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                continue


if __name__ == '__main__':
    shell = MiniShell()
    shell.run()