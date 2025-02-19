import os
import sys
import re


def find_executable(cmd, path):
    """Find the full path of an executable in PATH."""
    if '/' in cmd:
        return cmd if os.access(cmd, os.X_OK) else None
    for directory in path:
        full_path = os.path.join(directory, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None


def parse_command(command):
    """Parse command for redirections, pipes, and background execution."""
    parts = re.split(r'\s+', command.strip())
    cmd_parts = {'args': [], 'input': None, 'output': None, 'pipe': None, 'background': False}
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


def execute_command(cmd_parts, path, running):
    """Execute the command with the given parts."""
    if not cmd_parts['args']:
        return running

    cmd = cmd_parts['args'][0]

    if cmd == 'quit':
        return False
    elif cmd == 'cd':
        if len(cmd_parts['args']) > 1:
            try:
                os.chdir(cmd_parts['args'][1])
            except FileNotFoundError:
                print(f"Directory not found: {cmd_parts['args'][1]}")
        return running
    elif cmd == 'inspiration':
        print(os.environ.get('phrase', 'No inspiration set!'))
        return running

    executable = find_executable(cmd, path)
    if not executable:
        print("command not found")
        return running

    pipe_read, pipe_write = None, None
    if cmd_parts['pipe']:
        pipe_read, pipe_write = os.pipe()

    pid = os.fork()
    if pid == 0:
        try:
            if cmd_parts['input']:
                fd = os.open(cmd_parts['input'], os.O_RDONLY)
                os.dup2(fd, 0)
                os.close(fd)
            if cmd_parts['output']:
                fd = os.open(cmd_parts['output'], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, 1)
                os.close(fd)
            if pipe_write is not None:
                os.dup2(pipe_write, 1)
                os.close(pipe_read)
                os.close(pipe_write)
            os.execv(executable, cmd_parts['args'])
        except Exception as e:
            print(f"Error executing command: {e}")
            os._exit(1)

    if pipe_write is not None:
        os.close(pipe_write)
        pipe_pid = os.fork()
        if pipe_pid == 0:
            os.dup2(pipe_read, 0)
            os.close(pipe_read)
            pipe_parts = parse_command(cmd_parts['pipe'])
            pipe_executable = find_executable(pipe_parts['args'][0], path)
            if pipe_executable:
                os.execv(pipe_executable, pipe_parts['args'])
            else:
                print("Pipe command not found")
                os._exit(1)
        os.close(pipe_read)
        os.waitpid(pipe_pid, 0)

    if not cmd_parts['background']:
        _, status = os.waitpid(pid, 0)
        exit_code = status >> 8
        if cmd == 'grep' and exit_code == 1:
            if '-c' in cmd_parts['args'] and 'output' not in cmd_parts:
                print("0")
        elif exit_code != 0:
            print(f"Program terminated: exit code {exit_code}")

    return running


def run_shell():
    """Main shell loop."""
    running = True
    path = os.environ.get('PATH', '').split(':')

    while running:
        try:
            if len(sys.argv) > 1:
                with open(sys.argv[1], 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            print(f"$ {line}")
                            cmd_parts = parse_command(line)
                            running = execute_command(cmd_parts, path, running)
                break
            else:
                command = input('$ ')
                if command.strip():
                    cmd_parts = parse_command(command)
                    running = execute_command(cmd_parts, path, running)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            continue


if __name__ == '__main__':
    run_shell()
