# A basic Unix-like shell implemented in Python with built-in commands,
# foreground/background job control, and process management.

import os
import shlex
import signal
import subprocess
import sys

jobs = []  # List to track background jobs
job_counter = 1

def run_builtin(command, args):
    try:
        if command == "cd":
            os.chdir(args[0] if args else os.environ['HOME'])
        elif command == "pwd":
            print(os.getcwd())
        elif command == "exit":
            print("Exiting shell...")
            sys.exit(0)
        elif command == "echo":
            print(' '.join(args))
        elif command == "clear":
            os.system('clear')
        elif command == "jobs":
            for i, job in enumerate(jobs):
                print(f"[{i+1}] PID: {job['pid']} CMD: {' '.join(job['cmd'])} STATUS: {job['status']}")
        elif command == "fg":
            if not args:
                print("Usage: fg [job_id]")
                return
            bring_to_foreground(int(args[0]) - 1)
        elif command == "bg":
            if not args:
                print("Usage: bg [job_id]")
                return
            resume_in_background(int(args[0]) - 1)
        else:
            return False
        return True
    except Exception as e:
        print(f"Error in built-in command '{command}': {e}")
        return True

def bring_to_foreground(job_id):
    try:
        job = jobs[job_id]
        os.kill(job['pid'], signal.SIGCONT)
        _, status = os.waitpid(job['pid'], 0)
        job['status'] = 'Done'
    except IndexError:
        print("Invalid job ID")

def resume_in_background(job_id):
    try:
        job = jobs[job_id]
        os.kill(job['pid'], signal.SIGCONT)
        job['status'] = 'Running'
    except IndexError:
        print("Invalid job ID")

def execute_command(cmd_line):
    global job_counter
    if not cmd_line.strip():
        return

    background = cmd_line.strip().endswith('&')
    if background:
        cmd_line = cmd_line.strip()[:-1].strip()

    try:
        tokens = shlex.split(cmd_line)
        command, args = tokens[0], tokens[1:]

        if run_builtin(command, args):
            return

        process = subprocess.Popen(tokens)
        if background:
            jobs.append({
                'pid': process.pid,
                'cmd': tokens,
                'status': 'Running'
            })
            print(f"Started background job [{len(jobs)}] with PID {process.pid}")
        else:
            process.wait()
    except FileNotFoundError:
        print(f"Command not found: {cmd_line}")
    except Exception as e:
        print(f"Error executing command: {e}")

def shell_loop():
    print("Welcome to the Custom Shell! Type 'exit' to quit.")
    while True:
        try:
            cmd_line = input("$ ")
            execute_command(cmd_line)
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the shell.")
        except EOFError:
            print("\nExiting.")
            break

if __name__ == "__main__":
    shell_loop()
