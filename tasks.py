from time import sleep
from robocorp.tasks import task
from RPA.Desktop import Desktop

import os

from downloader import (
    download_app_folder,
    download_orders_files,
    load_csv_files_to_json,
    load_excel_files_to_json,
)
from dotenv import load_dotenv

load_dotenv()

tag = "Windows Desktop Robot : "
app_path = 'app_folder/app/testapp.exe'

@task
def example_orders_task():
    """Example Robot to show how to integrate Azure functionality and dependency externalization"""
    print(
        f"\n\n{tag} ...... Task starting .... will start downloading app and orders from Azure Storage"
    )
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
    
    except Exception as e:
        print(f"\n\n{tag} We hit a wall here, Boss! - {e}")

    desktop = Desktop(locators_path="locators.json")
    #app = desktop.open_application(r"C:\Users\aubreym\Desktop\Dannys\app\testapp.exe")
    app = desktop.open_application(app_path)
    print(f"{tag} have we opened the RobotTester app? {app}")
    sleep(1)
    try:
        login = desktop.wait_for_element("login")
        print(f"{tag} login screen established; {login}")
        username = desktop.wait_for_element("username")
        password = desktop.wait_for_element("password")

        username_env = os.getenv("USER_NAME")
        password_env = os.getenv("PASSWORD")
        print(f"username element: {username_env} password: {password_env}")

        desktop.type_text_into(username, username_env, True, False)
        desktop.type_text_into(password, password_env, True, False)

        submit_creds = desktop.wait_for_element("submit")
        print(f"submit_creds: {submit_creds}")
        desktop.click("submit")
        print("Submit button clicked!!")
        desktop.click("go_to_sales")
        print("Go to Sales button clicked!!")
        # app has navigated to order screen
        customer_id = desktop.wait_for_element("customer_id")
        product_id = desktop.wait_for_element("product_id")
        quantity = desktop.wait_for_element("quantity")
        checkbox = desktop.wait_for_element("checkbox")
        send_order = desktop.wait_for_element("send_order")
        close = desktop.wait_for_element("close")

        desktop.type_text_into(customer_id, "1102999", True, False)
        desktop.type_text_into(product_id, "5466$", True, False)
        desktop.type_text_into(quantity, "98", True, False)
        desktop.click(checkbox)
        print("Customer, Product, Qty and checkbox should be cool!")
        desktop.click(send_order)
        print("Send Order button clicked!!")
        create_work_items()
        # Sleeping just for testing ...
        sleep(10)
        desktop.click(close)
    except Exception as e:
        print(f"{tag} Ran into the wall, Boss! - {e}")
        appx = desktop.close_application(app_path)
        print(f'{tag} application should close because of error: {appx}')

def create_work_items():
    """Create work_items for next step"""
    print(f"\n\n{tag} will be creating work items here in the near future ....\n\n")
