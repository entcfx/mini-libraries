# A custom implementation of the subprocess library
import os
import sys
import time
import cshutil as shutil

class CompletedProcess:
    def __init__(self, args, returncode, stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

class PopenResult:
    def __init__(self, command, pid, stdout=None, stderr=None):
        self.command = command
        self.pid = pid
        self.stdout = stdout
        self.stderr = stderr

    def communicate(self):
        if self.stdout:
            stdout_data = os.read(self.stdout[1], 4096)
            self.stdout = stdout_data.decode()

        if self.stderr:
            stderr_data = os.read(self.stderr[1], 4096)
            self.stderr = stderr_data.decode()

        return self.stdout, self.stderr
    
    def poll(self):
        pid, status = os.waitpid(0, os.WNOHANG)
        if not pid:
            return None
        else:
            return os.WEXITSTATUS(status)

    def wait(self):
        while True:
            retcode = self.poll()
            if retcode is None:
                time.sleep(.1)
            elif retcode == 0 or retcode != 256:
                break
            assert retcode in (None, 0), "Command failed with error %d" % retcode
            return retcode

    def terminate(self):
        try:
            os.kill(self.pid, 9)
        except OSError as e:
            return e

    def kill(self):
        try:
            os.kill(self.pid, 15)
        except OSError as e:
            return e

def popen(*args, **kwargs):
    stdout_pipe = os.pipe()
    stderr_pipe = os.pipe()

    try:
        pid = os.fork()

        if pid == 0:  # Child process
            # Close unused ends in the child process
            os.close(stdout_pipe[0])
            os.close(stderr_pipe[0])

            # Redirect stdout and stderr to pipes
            os.dup2(stdout_pipe[1], sys.stdout.fileno())
            os.dup2(stderr_pipe[1], sys.stderr.fileno())

            # Execute the command in the child process
            try:
                os.execvp(args[0], args)
            except Exception as e:
                sys.stderr.write(f"Error executing {args[0]}: {e}\n")
                sys.exit(1)

        else:  # Parent process
            # Close unused ends in the parent process
            os.close(stdout_pipe[1])
            os.close(stderr_pipe[1])

            return PopenResult(args, pid, (None, stdout_pipe[0]), (None, stderr_pipe[0]))

    except Exception as e:
        sys.stderr.write(f"Error creating process: {e}\n")
        sys.exit(1)

def run(command, input_data=None, capture_output=False, text=False):
    stdout_pipe = os.pipe() if capture_output else None
    stderr_pipe = os.pipe() if capture_output else None

    try:
        pid = os.fork()

        if pid == 0:  # Child process
            if capture_output:
                os.close(stdout_pipe[0])
                os.close(stderr_pipe[0])

                os.dup2(stdout_pipe[1], sys.stdout.fileno())
                os.dup2(stderr_pipe[1], sys.stderr.fileno())

            try:
                os.execvp(command[0], command)
            except Exception as e:
                sys.stderr.write(f"Error executing {command[0]}: {e}\n")
                sys.exit(1)

        else:  # Parent process
            if capture_output:
                os.close(stdout_pipe[1])
                os.close(stderr_pipe[1])

            _, status = os.waitpid(pid, 0)

            if capture_output:
                stdout_data = os.read(stdout_pipe[0], 4096).decode() if stdout_pipe else None
                stderr_data = os.read(stderr_pipe[0], 4096).decode() if stderr_pipe else None
                return CompletedProcess(command, status, stdout_data, stderr_data)

    except Exception as e:
        sys.stderr.write(f"Error creating process: {e}\n")
        sys.exit(1)

def call(command):
    try:
        pid = os.fork()

        if pid == 0:  # Child process
            try:
                os.execvp(command[0], command)
            except Exception as e:
                sys.stderr.write(f"Error executing {command[0]}: {e}\n")
                sys.exit(1)

        else:  # Parent process
            _, status = os.waitpid(pid, 0)
            return status

    except Exception as e:
        sys.stderr.write(f"Error creating process: {e}\n")
        sys.exit(1)