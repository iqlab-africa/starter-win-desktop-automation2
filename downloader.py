from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

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
        for blob in blob_list:
            blob_path = blob.name
            local_path = os.path.join(local_app_folder, blob_path)
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            blob_client = container_client.get_blob_client(blob_path)
            with open(local_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            print(f"{tag} Downloaded OK!! : {local_path}")

        return blob_list
    except Exception as e:
        print(f"{tag} Downloading stumbled here, Boss! Error: {e}")


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

        print(f"{tag} Order files downloaded OK? csv: {csv} excel: {excel}\n\n")

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


import pandas as pd

CSV_FILE_TYPE = "csv"
EXCEL_FILE_TYPE = "excel"


def load_csv_files_to_json():
    print(f"\n\n{tag} loading file contents and creating json list; \n")
    json_list = do_the_work(CSV_FILE_TYPE)
    return json_list


def load_excel_files_to_json():
    json_list = do_the_work(EXCEL_FILE_TYPE)
    return json_list


def do_the_work(fileType):
    print(f"\n\n{tag} loading Excel file contents and creating json list; \n")
    json_list = []

    try:
        for root, _, files in os.walk(local_orders_folder):
            for file in files:
                file_path = os.path.join(root, file)

                if file.endswith(".xlsx") and fileType == EXCEL_FILE_TYPE:
                    print(
                        f"{tag} reading excel spreadsheet: {file_path} into pandas DataFrame ..."
                    )
                    df = pd.read_excel(file_path)
                    json_data = df.to_dict(orient="records")
                    json_list.extend(json_data)
                    print(f"\n{tag} Loaded {len(json_list)} records")

                if file.endswith(".csv") and fileType == CSV_FILE_TYPE:
                    print(
                        f"{tag} reading csv file: {file_path} into pandas DataFrame ..."
                    )
                    df = pd.read_csv(file_path)
                    json_data = df.to_dict(orient="records")
                    json_list.extend(json_data)
                    print(f"\n{tag} Loaded {len(json_list)} records")

    except Exception as e:
        print(f"{tag} We hit a tree this time, Boss! - {e}")

    print(f"\n{tag} returning {len(json_list)} json records from {fileType} file \n\n")
    return json_list
