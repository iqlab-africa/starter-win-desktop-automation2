import os

from downloader import (
    download_app_folder,
    download_orders_files,
    load_csv_files_to_json,
    load_excel_files_to_json,
)

tag = "Handyman : "


def set_up() -> list:
    try:
        download_orders_files()
        use_excel = os.getenv("USE_EXCEL")
        if use_excel == "1":
            json_list = load_excel_files_to_json()
        else:
            json_list = load_csv_files_to_json()

        # get the desktop app files ....
        app_files = download_app_folder()

        print(f"\n\n{tag} number of orders in json_list : {len(json_list)}")
        print(f"{tag} number of app files: {len(app_files)}")
        return json_list

    except Exception as e:
        print(f"\n\n{tag} We hit a wall here, Boss! - {e}")
