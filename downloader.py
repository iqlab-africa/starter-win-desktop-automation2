from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
import pandas as pd

CSV_FILE_TYPE = "csv"
EXCEL_FILE_TYPE = "excel"

# Load environment variables from .env file
load_dotenv()

app_container_name = "appcontainer"
orders_container_name = "ordercontainer"

local_app_folder = "app_folder"
local_orders_folder = "orders_folder"

orders_excel_file = "orders.xlsx"
orders_csv_file = "orders.csv"
tag = "File Downloader"


def download_app_folder():
    print(f"\n\n{tag}... download_app_folder starting ...")
    try:
        connection_string = os.getenv("AZURE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("Connection string not found in environment variables")
        else:
            print(f"{tag} We good with AZURE_CONNECTION_STRING ...")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container_client = blob_service_client.get_container_client(app_container_name)
        blob_list = container_client.list_blobs()
        # Convert the ItemPaged object to a list
        blob_list = list(container_client.list_blobs())
        print(f"{tag} ..... app blobs found: {len(blob_list)}")
        for blob in blob_list:
            print(f"{tag}  - blob.name: {blob.name}")
        print("\n")
        count = 0
        error_count = 0
        for blob in blob_list:
            local_path = os.path.join(local_app_folder, blob.name)
            # Replace backslashes with forward slashes
            modified_path = local_path.replace("\\", "/")
            print(f"\n{tag} processing blob: #{count} - {blob.name} modified path: {modified_path}")

            try:
                local_dir = os.path.dirname(modified_path)
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                blob_client = container_client.get_blob_client(blob.name)
                with open(modified_path, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
                print(f"{tag} App file downloaded OK!! local path: {modified_path}")
                count = count + 1
            except Exception as e:
                print(
                    f"\n{tag} Error downloading file: {modified_path} - {e}\n"
                )
                error_count = error_count + 1
                continue

        print(f"{tag} Application files downloaded OK: {count}, errors: {error_count}")
        return blob_list
    
    except Exception as e:
        print(f'{tag} Errors here! succeeded: {count} errors: {error_count}')
        print(f"\n\n{tag} Downloading app files stumbling and bumbling, Boss! Error: {e}")


def download_orders_files():
    try:
        print(
            f"\n\n{tag} ... download_orders_files starting ... files: {orders_excel_file} {orders_csv_file}"
        )
        connection_string = os.getenv("AZURE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("Connection string not found in environment variables")
        else:
            print(f"{tag} We good with AZURE_CONNECTION_STRING ...")

        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )

        csv = do_download(
            blob_service_client=blob_service_client, filename=orders_csv_file
        )
        excel = do_download(
            blob_service_client=blob_service_client, filename=orders_excel_file
        )

        print(f"{tag} Order files downloaded OK? csv: {csv} excel: {excel}\n")

    except Exception as e:
        print(f"{tag} download_orders_file: Error: {e}")


def do_download(blob_service_client, filename):
    try:
        container_client = blob_service_client.get_container_client(
            orders_container_name
        )
        blob_client = container_client.get_blob_client(filename)

        # Download the blob
        download_stream = blob_client.download_blob()
        file_content = download_stream.readall()

        # Define the local path and ensure the directory exists
        local_path = os.path.join(local_orders_folder, filename)
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        # Write the file content to the local path
        with open(local_path, "wb") as file:
            file.write(file_content)

        # Print the file name and length in bytes
        file_size = len(file_content)
        print(
            f"{tag} do_download: local_path: {local_path} fileName: {filename} size: {file_size} bytes"
        )
        print(f"\n")
        return local_path

    except Exception as e:
        print(f"{tag} Error downloading orders: {e}")


def load_csv_files_to_json():
    json_list = do_the_work(CSV_FILE_TYPE)
    return json_list


def load_excel_files_to_json():
    json_list = do_the_work(EXCEL_FILE_TYPE)
    return json_list


def do_the_work(file_type):
    print(f"\n\n{tag} loading {file_type} file contents and creating json list")
    json_list = []

    try:
        for root, _, files in os.walk(local_orders_folder):
            for file in files:
                file_path = os.path.join(root, file)

                if (
                    file_path.endswith(".xlsx") and file_type == EXCEL_FILE_TYPE
                ):  # Load the Excel file into a DataFrame, ignoring the header row
                    df = pd.read_excel(file_path, header=None)
                    # Convert the DataFrame to a list of dictionaries (JSON format)
                    # The first row is the header; hence, ignore it by starting from the second row
                    json_list = df.iloc[1:].to_dict(orient="records")

                    print(f"{tag} Loaded {len(json_list)} records from {file_path}")
                    return json_list
                    print(f"\n{tag} Loaded {len(json_list)} {file_type} records")

                if file_path.endswith(".csv") and file_type == CSV_FILE_TYPE:
                    df = pd.read_csv(file_path, header=None)
                    json_list = df.iloc[1:].to_dict(orient="records")
                    print(f"\n{tag} Loaded {len(json_list)} {file_type} records")

    except Exception as e:
        print(f"{tag} We hit a tree this time, Boss! - {e}")

    print(f"\n{tag} returning {len(json_list)} json records from {file_type} file \n")
    return json_list
