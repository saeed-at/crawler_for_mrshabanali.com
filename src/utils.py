import os
import subprocess
from logger import setup_logging


conversion_logger = setup_logging("./Logs/conversion_logs.txt")
change_filename_logger = setup_logging("./Logs/change_filename_logs.txt")


def create_directory(directory_path):
    """
    Create a directory at the specified path if it does not exist.

    :param directory_path: The path where the directory needs to be created.
    :return: None
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        else:
            print(f"Directory '{directory_path}' already exists. Skipping creation.")
    except OSError as e:
        print(f"Error: {e}")


def pdf_generator(file_name):
    """
    Converts an HTML file to a PDF using PrinceXML.

    This function takes an HTML file named 'output.html' located in the 'Output_PDFs' directory
    and converts it into a PDF file with the specified name in the same directory.

    :param file_name: The name of the output PDF file (excluding the extension).
    :return: None
    """
    bash_command = (
        f"prince Output_PDFs/output.html -o./Output_PDFs/{file_name}.pdf "
        f"--pdf-creator=telegram:@saeed0047,Github::saeed-at --pdf-author=Mr.Shabanali"
    )
    try:
        result = subprocess.run(bash_command, shell=True, text=True, capture_output=False)
        if result.returncode == 0:
            conversion_logger.info(f"Successfully converted {file_name}.html to pdf.")
        else:
            conversion_logger.error(f"Error converting {file_name}.html to pdf., {file_name}\n{bash_command}")
    except:
        conversion_logger.error(f"Error executing command: {bash_command}.")


def rename_file(old_name, new_name, post_number):
    """
    Rename a PDF file located in the 'Output_PDFs' directory.

    This function renames a PDF file from the 'Output_PDFs' directory with the specified
    'old_name' to the 'new_name' provided.

    :param old_name: The current name of the PDF file (excluding the extension).
    :param new_name: The desired new name of the PDF file (excluding the extension).
    :param post_number: The number of post based on first post in the site till now
    :return: None
    """
    try:
        os.rename(f"{old_name}.pdf", f"./Output_PDFs/[{post_number}]_{new_name}.pdf")
        change_filename_logger.info(f"File {old_name}.pdf has been renamed successfully")
    except FileNotFoundError:
        change_filename_logger.info(f"{old_name}.pdf not found.")
    except OSError as e:
        change_filename_logger.info(f"Error: {e}")
