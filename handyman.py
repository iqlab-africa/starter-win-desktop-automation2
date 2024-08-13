import os

from downloader import (
    download_app_folder,
    download_orders_files,
    load_csv_files_to_json,
    load_excel_files_to_json,
)
from environment_util import get_excel_flag

tag = "Handyman : "


def get_robot_downloads() -> list:
    json_list = []
    try:
        download_orders_files()
        use_excel = get_excel_flag()
        if use_excel == "1":
            json_list = load_excel_files_to_json()
        else:
            json_list = load_csv_files_to_json()
            
        print(f"\n{tag} number of orders in json_list : {len(json_list)}")

        # get the desktop app files ....
        if not check_app_folder_contents():
            print(f'{tag} desktop app files have to be downloaded ')
            app_files = download_app_folder()
            print(f"{tag} number of app files: {len(app_files)}")

        else:
            print(f'{tag} desktop app files exist in the Robot. No need to download! ')

        return json_list

    except Exception as e:
        print(f"\n\n{tag} We hit a wall here, Boss! - {e}")


def check_app_folder_contents() -> True | False:
    """
    Check if app_folder exists and has the expected files"""

    # Check if folder A exists
    folder_a_path = "app_folder"
    if not os.path.isdir(folder_a_path):
        print(f"{tag} Top app folder not found. '{folder_a_path}' does not exist.")
        return False

    # Check if folder B exists within folder A
    folder_b_path = os.path.join(folder_a_path, "app")
    if not os.path.isdir(folder_b_path):
        print(f"{tag} app folder '{folder_b_path}' does not exist in app_folder folder")
        return False

    # Check if folder C exists within folder B
    folder_c_path = os.path.join(folder_b_path, "data")
    if not os.path.isdir(folder_c_path):
        print(f"{tag} data folder '{folder_c_path}' does not exist in app folder")
        return False

    # Count the number of files in folder B
    file_count = sum(
        [len(files) for r, d, 
         files in os.walk(folder_b_path) if r == folder_a_path]
    )
    
    expected_file_count = 8
    if file_count != expected_file_count:
        print(
            f"{tag} app folder contains {file_count} files, but {expected_file_count} files were expected."
        )
        if file_count >= expected_file_count:
            return True
        else:
            return False

    print(f'{tag} The app folder and files are here. So let us boogie!')
    return True
