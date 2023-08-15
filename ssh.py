import os
import subprocess
from venv import logger
import paramiko
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
#from logging.handlers import HTMLFormatter
import sys
import pdb
import subprocess

def check_number_of_lines(file_path):
    try:
        # Execute the grep command
        result = subprocess.run(['grep', '-c', '^', file_path], capture_output=True, text=True)

        # Get the number of lines from the output
        num_lines = int(result.stdout.strip())

        # Perform different actions based on the number of lines
        if num_lines > 1 :
            logger.info(f"Service is running")
            
            # Do something if the file has three lines
        #else:
        #    logger.error(f"Service is installed with some issue.Check installlog_{timestamp}_{OS}")  
        #    # Do something else if the file does not have three lines

    except FileNotFoundError:
        print(f"Error: The file {file_path} not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error: The command returned a non-zero exit status. Output: {e.output}")


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

# def log_success(message):
#     logger.log(logging.SUCCESS, message)

# def log_fail(message):
#     logger.log(logging.FAIL, message)

# # Adding new logging levels to the logging module
# logging.SUCCESS = 25  # You can choose a numeric value not already used by standard levels
# logging.addLevelName(logging.SUCCESS, 'SUCCESS')

# logging.FAIL = 35     # Another custom level
# logging.addLevelName(logging.FAIL, 'FAIL')


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
            return False
        #    raise PingError(f"The IP address {ip_address} is not reachable.")
        
    except subprocess.TimeoutExpired:
        logger.error(f"Timed out while trying to ping {ip_address}.")
        #raise PingError(f"Timed out while trying to ping {ip_address}.")
    except Exception as e:
        logger.error(f"Error occurred while pinging {ip_address}: {e}")
        #raise PingError(f"Error occurred while pinging {ip_address}: {e}")

def timeout(n):
    try:
        # Run the subprocess with a timeout of 3 seconds
        result = subprocess.run(['your_command', 'arg1', 'arg2'], timeout=n, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("The command timed out after 3 seconds.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")

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

 #def sudo_execute_remote_commands(ssh_client, command, sudo_password=None):
    try:
            # Add 'sudo' to the command to run it with elevated privileges
            sudo_command = f"sudo -S {command}"

            stdin, stdout, stderr = ssh_client.exec_command(sudo_command)
            
            # If sudo password is provided, send it to the command prompt
            if sudo_password:
                stdin.write(sudo_password + "\n")
                stdin.flush()

            output = stdout.readlines()
            error = stderr.readlines()

            if output:
                print(f"Command output on the remote server:")
                print("".join(output))

            if error:
                print(f"Command error on the remote server:")
                print("".join(error))

    except paramiko.SSHException as e:
        print(f"SSH error occurred while executing the commands: {str(e)}")
    except Exception as e:
        print(f"An error occurred while executing the commands: {str(e)}")

def execute_remote_commands(ssh_client, command,sudo_password=None):
    try:
            if sudo_password :
                command = f"echo '{sudo_password}' | sudo -S {command}"

            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.readlines() #.decode()
            error = stderr.readlines()  #.decode()

            if sudo_password:
                stdin.write(f"{sudo_password}\n")
                stdin.flush()

            if output:
                print(f"Command output on the remote server:")
                print("".join(output))

            #if error:
            #    print(f"Command error on the remote server:")
            #    print("".join(error))

    except paramiko.SSHException as e:
        logger.error(f"SSH error occurred while executing the commands: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred while executing the commands: {str(e)}")

def close_ssh_connection(ssh_client):
    ssh_client.close()

def check_status_service(file_path):
    try:
        # Read the content of the file
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Check if the desired string is present in the file content
        if "active (running)" in file_content:
            logger.info(f"Systemctl EPSecClient.Service is running")
        #else :
        #    logger.error(f"Service is installed with some issue.Check installlog_{timestamp}_{OS}")
        #    print("The file contains 'active (running)'.")
        #    #Do something if the file contains the string 'active (running)'
        
    except FileNotFoundError:
        print(f"Error: The file {file_path} not found.")
    except Exception as e:
        print(f"Error occurred while reading the file {file_path}: {str(e)}")

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

#def read_commands_from_file(file_path):
#    commands = []
#    try:
#        with open(file_path, 'r') as cmd_file:
#            for line in cmd_file:
#                commands.append(line.strip())
#
#    except FileNotFoundError as e:
#       logger.error(f"{file_path} not found. No additional commands will be executed.")
#    
#   return commands
def create_folder_if_not_exists(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        try:
            # Create the folder
            os.makedirs(folder_path)
            print(f"Folder created at {folder_path}")
        except OSError as e:
            print(f"Error occurred while creating the folder: {str(e)}")

def main():
    file_path = "/home/testubuntu/testing_client/python_script/server_list.txt"  # Replace with the path to your file containing username, IP, and passwords.

    #current_script_path = os.path.abspath(__file__)
    # Get the directory path of the current script
    #current_directory = os.path.dirname(current_script_path)
    #filename = 'atirwraplinux.sh'  # Replace 'example.txt' with your desired file name
    #binary_path = os.path.join(current_directory, filename)

    binary_path="/home/testubuntu/testing_client/python_script/atirwraplinux.sh" #atirwraplinux.sh"
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
#    commands_to_execute_part1 = read_commands_from_file('/home/testubuntu/testing_client/python_script/commands_list_part1.txt') #('commands_list_part1.txt')
#    commands_to_execute_part2 = read_commands_from_file('/home/testubuntu/testing_client/python_script/commands_list_part2.txt')

    try:
        with open(file_path, "r") as file:
            for line in file:
                OS, username, ip, password = line.strip().split(",")
                logger.info(f"Testing on {OS} flavour")
                logger.info(f"Creating local folder for storage of {OS} service logs")
                create_folder_if_not_exists('/home/testubuntu/testing_client/python_script/buffer/'+OS)
                logger.info(f"Testing Reachability on {ip}")
                reachable = is_pingable(ip)
                if reachable :
                    logger.info(f"IP {ip} is reachable")
                    logger.info(f"Connecting to {username}@{ip}")
                else:
                    logger.error(f"The IP address {ip} of {OS} machine is not reachable.")

                ssh_client = ssh_into_server(username, ip, password)

                if ssh_client:
                    
                    logger.info(f"Executing remote commands on {username}@{ip}")
                    counter = 1
                    logger.info(f"Executing {counter}. command which create the directory on remote {OS} server.")
                    # Execute commands from commands_list_part1.txt
                    cmd = 'mkdir -p test'
                    #print(cmd)
                    execute_remote_commands(ssh_client, cmd)
        
                    counter+=1
                    #print(binary_path)
                    logger.info(f"Executing {counter}. command which Upload the binary on remote {OS} server.")
                    # Upload Binary file
                    local_file = binary_path # Replace with the path of the local file to upload
                    remote_file = "/home/"+username+"/test/atirwraplinux.sh"  # Replace with the desired remote path
                    upload_file(ssh_client, local_file, remote_file)
                    
                    #pdb.set_trace()
                    counter+=1
                    logger.info(f"Executing {counter}. command which grant the executable permission hosted on remote {OS} server.")
                    # Execute commands from commands_list_part2.txt
                    #commands_to_execute_part1.clear()
                    #print(commands_to_execute_part1)
                    cmd = "chmod +x /home/"+username+"/test/atirwraplinux.sh"

                    execute_remote_commands(ssh_client,cmd,password)
                    #commands_to_execute_part1.append(cmd)
                    #print(commands_to_execute_part1)


                    counter += 1
                    logger.info(f"Executing {counter}. command which Run the script on remote {OS} server.")
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    cmd = "bash /home/{username}/test/atirwraplinux.sh -ia -service -v > /home/"+username+"/test/installlog_"+timestamp+"_"+OS
                    #commands_to_execute_part1.append(cmd)
                    #print(commands_to_execute_part1)
                    #print(cmd)
                    execute_remote_commands(ssh_client, cmd,password)
                    #timeout(3)

                    # Download logs 
                    counter += 1
                    logger.info(f"Executing {counter}. command which download logs from remote {OS} server.")
                    remote_path = "/home/"+username+"/test/installlog_"+timestamp+"_"+OS  # "/home/remote_user/remote_file.txt"  # Replace with the remote file to download
                    local_path = "/home/testubuntu/testing_client/python_script/logs/installlog_"+timestamp+"_"+OS
                    download_file(ssh_client,remote_path,local_path)
                    
                    # 6.1
                    counter +=1 
                    sub_counter = 1
                    logger.info(f"Executing {counter}. command to perform some testing on remote {OS} server.")
                    logger.info(f"Executing {counter}.{sub_counter} command to perform basic testing whether the service is running on remote {OS} server.")
                    cmd = 'ps -ef | grep "EPSecClient" > '
                    cmd += '/home/'+username+'/test/top_service_running_'+timestamp+'_'+OS
                    execute_remote_commands(ssh_client,cmd)
                    remote_path = '/home/'+username+'/test/top_service_running_'+timestamp+'_'+OS  # "/home/remote_user/remote_file.txt"  # Replace with the remote file to download
                    local_path = "/home/testubuntu/testing_client/python_script/buffer/"+OS+"/top_service_running_"+timestamp+"_"+OS
                    download_file(ssh_client,remote_path,local_path)
                    check_number_of_lines(local_path)
                    
                    #6.2
                    sub_counter += 1
                    logger.info(f"Executing {counter}.{sub_counter} command to perform basic testing to check the service status on remote {OS} server.")
                    cmd = 'systemctl status EPSecClient > /home/'+username+'/test/status_service_running_'+timestamp+'_'+OS
                    execute_remote_commands(ssh_client,cmd)
                    remote_path = "/home/"+username+"/test/status_service_running_"+timestamp+"_"+OS  # "/home/remote_user/remote_file.txt"  # Replace with the remote file to download
                    local_path = "/home/testubuntu/testing_client/python_script/buffer/"+OS+"/status_service_running_"+timestamp+"_"+OS
                    download_file(ssh_client,remote_path,local_path)
                    check_status_service(local_path)
                    
                    # 6.3
                    sub_counter += 1
                    logger.info(f"Executing {counter}.{sub_counter} command to perform feature testing like DNS trace on remote {OS} server.")
                    cmd = "cat /etc/hosts > /home/"+username+"/test/dns_"+timestamp+"_"+OS
                    execute_remote_commands(ssh_client,cmd)
                    remote_path = "/home/"+username+"/test/dns_"+timestamp+"_"+OS  # "/home/remote_user/remote_file.txt"  # Replace with the remote file to download
                    local_path = "/home/testubuntu/testing_client/python_script/buffer/"+OS+"/dns_"+timestamp+"_"+OS
                    download_file(ssh_client,remote_path,local_path)
                    check_number_of_lines(local_path)

                    # 6.4
                    sub_counter += 1
                    logger.info(f"Executing {counter}.{sub_counter} command to perform feature testing like OpenSSH trace on remote {OS} server.")
                    cmd = 'cat ~/.ssh/known_hosts > /home/'+username+"/test/openssh_"+timestamp+"_"+OS
                    execute_remote_commands(ssh_client,cmd)
                    remote_path = "/home/"+username+"/test/openssh_"+timestamp+"_"+OS  # "/home/remote_user/remote_file.txt"  # Replace with the remote file to download
                    local_path = "/home/testubuntu/testing_client/python_script/buffer/"+OS+"/openssh_"+timestamp+"_"+OS
                    download_file(ssh_client,remote_path,local_path)
                    check_number_of_lines(local_path)
                    
                    counter +=1 
                    logger.info(f"Executing {counter}. command which remove the directory on remote {OS} server.")
                    #commands_to_execute_part1.clear()
                    cmd = "rm -r /home/"+username+"/test"
                    #commands_to_execute_part1.append(cmd)
                    execute_remote_commands(ssh_client,cmd)

                    counter += 1
                    logger.info(f"Executing {counter}. command closing ssh connection with remote {OS} server.")
                    close_ssh_connection(ssh_client)

                    logger.info(f"Successfull testing on remote {OS} server.")
                    logger.info(f"-----------Next Server I---------")
                    #timeout(3)


    except PingError as e:
        logger.error(f"IP:{ip} not reachable")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"An error occurred while processing the file: {str(e)}")

def success_parsing(input_file_path, output_file_path):
    try:
        # Open the input file for reading
        with open(input_file_path, "r") as input_file:
            lines = input_file.readlines()

            # Loop through the lines and check for the target text
            successful_lines = [line for line in lines if "Successfull testing on remote" in line]

        # Create the output file and write matching lines
        with open(output_file_path, "w") as output_file:
            output_file.writelines(successful_lines)

        print("Extraction completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def failed_parsing(input_file_path, output_file_path):
    try:
        # Open the input file for reading
        with open(input_file_path, "r") as input_file:
            lines = input_file.readlines()

            # Loop through the lines and check for "ERROR"
            error_lines = [line for line in lines if "ERROR" in line]

        # Create the output file and write error lines
        with open(output_file_path, "w") as output_file:
            output_file.writelines(error_lines)

        print("Extraction completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def final_status(input_file_path, output_file_path):
    try:
        # Open the input file for reading
        with open(input_file_path, "r") as input_file:
            lines = input_file.readlines()

            # Extract VM names and corresponding statuses (Pass/Fail)
            status_lines = []
            for line in lines:
                if "Successfull testing on remote" in line:
                    status_lines.append("Pass: " + line.split("Successfull testing on remote ")[-1].strip())
                elif "ERROR" in line:
                    status_lines.append("Fail: " + line.split("ERROR")[-1].strip())

        # Write status lines to the common output file
        with open(output_file_path, "w") as output_file:
            output_file.write("\n".join(status_lines))

        print("Extraction completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



if __name__ == "__main__":
    main()
    #success_parsing("ssh_script_logs.log","Success_Output.log")
    #failed_parsing("ssh_script_logs.log","Failure_Output.log")
    final_status("ssh_script_logs.log","Final_Output.log")
