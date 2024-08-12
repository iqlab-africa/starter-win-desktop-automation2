from time import sleep
from robocorp.tasks import task
from robocorp import workitems

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
    count = 0
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
       
        try:
            for order_json in json_list:
                if count < 2:
                    count = count + 1
                    print(f'\n{tag} ignored order_json: {order_json}\n')
                    continue
                print(f'{tag} order json: {order_json}')
                try:
                    customer_id_value = order_json[0]
                    product_id_value = order_json[1]
                    quantity_value = order_json[2]
                    print(f'{tag} customer_id_value: {customer_id_value} - product_id_value: {product_id_value} quantity_value: {quantity_value}')
                   
                    desktop.type_text_into(customer_id, f'{customer_id_value}', True, False)
                    desktop.type_text_into(product_id, f'{product_id_value}', True, False)
                    desktop.type_text_into(quantity, f'{quantity_value}', True, False)
                    desktop.click(checkbox)
                    desktop.click(send_order)
                    
                    print(f"{tag} Send Order button clicked!! - product: {product_id_value} quantity: {quantity_value}")        
                    count = count + 1
                    sleep(1)
                except Exception as e:
                    print(f'\n{tag} The accelerator seems to be stuck! What we gonna do, Boss? - {e}\n')
                    continue
        
        except Exception as e:
            print(f'{tag} The tree moved and we crashed into it :) - {e}')
            if app.is_running:
                appx = desktop.close_application(app)
                return
            
        print(f"{tag} all {len(json_list)} orders should be cool!")
        create_work_items(json_list=json_list)
        # TODO Sleeping just for testing ...
        sleep(5)
        desktop.click(close)
        sleep(1)
        try:
            if app.is_running:
                appx = desktop.close_application(app)
        except Exception as e:
            print(f'{tag} could not close app, probably already closed by the click: {e}')
            print(f'{tag} application should be closed because the work is done!: {appx}')
    except Exception as e:
        print(f"{tag} Ran into the wall, Boss! - {e}")
        if app.is_running:
            appx = desktop.close_application(app)
            print(f'{tag} application should close because of error: {appx}')

def create_work_items(json_list: list):
    """Create work_items for next step"""
    workitems.outputs.create(payload={"orders": json_list})
    print(f"\n\n{tag} work items created: {len(json_list)} ....\n\n")

