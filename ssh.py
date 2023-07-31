import os
import subprocess
from venv import logger
import paramiko
import logging
from logging.handlers import RotatingFileHandler
#from logging.handlers import HTMLFormatter
import sys

class HTMLFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        message = record.msg
        time = self.formatTime(record, self.datefmt)

        html = f'<p>[{time}] <b>{level}</b>: {message}</p>\n'
        return html

# Example usage
logger = logging.getLogger('my_logger')
handler = logging.StreamHandler()  # You can use other handlers like FileHandler
formatter = HTMLFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Test logging
#logger.warning('This is a warning message.')
#logger.error('This is an error message.')

class PingError(Exception):
    pass

def is_pingable(ip_address):
    try:
        # Execute the ping command
        result = subprocess.run(['ping', '-c', '1', ip_address], capture_output=True, text=True, timeout=5)

        # Check the return code to see if the ping was successful
        if result.returncode == 0:
            return True
        else:
            raise PingError(f"The IP address {ip_address} is not reachable.")
    except subprocess.TimeoutExpired:
        raise PingError(f"Timed out while trying to ping {ip_address}.")
    except Exception as e:
        raise PingError(f"Error occurred while pinging {ip_address}: {e}")

def ssh_into_server(username, ip, password):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ip, username=username, password=password)
        return ssh_client

    except paramiko.AuthenticationException:
        logger.error(f"Failed to authenticate to {username}@{ip} with the given password.")
    except paramiko.SSHException as e:
        logger.error(f"SSH error occurred while connecting to {username}@{ip}: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred while connecting to {username}@{ip}: {str(e)}")
    return None

def execute_remote_commands(ssh_client, commands):
    try:
        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                logger.info(f"Command output on the remote server:\n{output}")

            if error:
                logger.error(f"Command error on the remote server:\n{error}")

    except paramiko.SSHException as e:
        logger.error(f"SSH error occurred while executing the commands: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred while executing the commands: {str(e)}")

def close_ssh_connection(ssh_client):
    ssh_client.close()

def upload_file(ssh_client, local_path, remote_path):
    try:
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(local_path, remote_path)
        logger.info(f"File {local_path} uploaded to {remote_path} on the remote server.")
    
#    except FileNotFoundError:
#    logger.error(f"Local file {local_path} not found.")
    
    except Exception as e:
        logger.error(f"An error occurred while uploading file {local_path}: {str(e)}")
    
    finally :
        sftp_client.close()
    

def download_file(ssh_client, remote_path, local_path):
    try:
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(remote_path, local_path)
        sftp_client.close()
        logger.info(f"File {remote_path} downloaded to {local_path} from the remote server.")
    
    except FileNotFoundError:
        logger.error(f"Remote file {remote_path} not found.")
    
    except Exception as e:
        logger.error(f"An error occurred while downloading file {remote_path}: {str(e)}")
    
    finally :
        sftp_client.close()

def read_commands_from_file(file_path):
    commands = []
    try:
        with open(file_path, 'r') as cmd_file:
            for line in cmd_file:
                commands.append(line.strip())

    except FileNotFoundError as e:
        logger.error(f"{file_path} not found. No additional commands will be executed.")
    
    return commands

def main():
    file_path = "server_list.txt"  # Replace with the path to your file containing username, IP, and passwords.

    current_script_path = os.path.abspath(__file__)
    # Get the directory path of the current script
    current_directory = os.path.dirname(current_script_path)
    filename = 'atirwraplinux.sh'  # Replace 'example.txt' with your desired file name
    binary_path = os.path.join(current_directory, filename)
    #binary_path="python_script/atirwraplinux.sh"
    # Set up the logging configuration
    log_file = 'ssh_script_logs.log'
    html_report_file = 'ssh_script_logs.html'

    # Create the logger and set the logging level
    logger = logging.getLogger('ssh_script')
    logger.setLevel(logging.INFO)

    # Create a formatter for the log messages
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a rotating file handler for the log file
    file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_formatter)

    # Create a file handler for the HTML report
    html_file_handler = logging.FileHandler(html_report_file, mode='a')
    html_file_handler.setLevel(logging.INFO)
    html_formatter = HTMLFormatter()
    html_file_handler.setFormatter(html_formatter)

    # Create a stream handler for printing log messages to the console (verbose)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_formatter)

    # Add all the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(html_file_handler)
    logger.addHandler(console_handler)

    # Read the commands from commands_list.txt using the new function
    commands_to_execute_part1 = read_commands_from_file('commands_list_part1.txt')
    commands_to_execute_part2 = read_commands_from_file('commands_list_part2.txt')

    try:
        with open(file_path, "r") as file:
            for line in file:
                OS, username, ip, password = line.strip().split(",")
                logger.info(f"Testing on {OS} flavour")

                logger.info(f"Testing Reachability on {ip}")
                reachable = is_pingable(ip)
                logger.info(f"IP {ip} is reachable")

                logger.info(f"Connecting to {username}@{ip}")
                ssh_client = ssh_into_server(username, ip, password)
                if ssh_client:
                    
                    logger.info(f"Executing remote commands on {username}@{ip}")
                    # Execute commands from commands_list_part1.txt
                    execute_remote_commands(ssh_client, commands_to_execute_part1)
                    
                    # Execute commands from commands_list_part2.txt
                    #execute_remote_commands(ssh_client, commands_to_execute_part2)

                    #Upload and download files, as before
                    #local_file = binary_path  # Replace with the path of the local file to upload
                    #binary_path = "assets/atirwraplinux.sh"
                    remote_file = "/home/"+username+"/test/atirwraplinux.sh"  # Replace with the desired remote path
                    upload_file(ssh_client, binary_path, remote_file)

                    #remote_file = "/home/remote_user/remote_file.txt"  # Replace with the remote file to download
                    #local_file = "downloaded_file.txt"  # Replace with the desired local path
                    #download_file(ssh_client, remote_file, local_file)

                    close_ssh_connection(ssh_client)

    except PingError as e:
        logger.error(f"IP:{ip} not reachable")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"An error occurred while processing the file: {str(e)}")

if __name__ == "__main__":
    main()
