from time import sleep
from robocorp.tasks import task
from robocorp import workitems

from RPA.Desktop import Desktop

from downloader import (
    download_app_folder,
    download_orders_files,
    load_csv_files_to_json,
    load_excel_files_to_json,
)

from environment_util import get_user_name, get_user_password
from handyman import get_robot_downloads


tag = "Windows Desktop Robot : "
app_path = "app_folder/app/testapp.exe"

@task
def example_orders_task():
    """Example Robot to show how to integrate Azure functionality and dependency externalization"""
    print(
        f"\n\n{tag} ...... Task starting .... will start downloading app and orders from Azure Storage"
    )
    # Set up the Robot by downloading artifacts from Azure Storage
    raw_list = get_robot_downloads()
    # Remove top 2 rows
    json_list = []
    if len(raw_list) > 2:
        json_list = raw_list[2:]

    # Create the desktop that will run the app
    # Open the Windows desktop app - the app_folder contains everything the app needs to run

    desktop = Desktop(locators_path="locators.json")
    # app = desktop.open_application(r"C:\Users\aubreym\Desktop\Dannys\app\testapp.exe")
    app = desktop.open_application(app_path)
    if app:
        print(f"\n{tag} the Windows desktop app has been opened: {app}")
    sleep(1)

    try:
        # Run the login process on the Windows desktop app
        _handle_login(desktop)
        # app has navigated to order screen, set image elements
        count, error_count = _drive_order_screen(
            app=app, desktop=desktop, json_list=json_list
        )

        print(f"{tag} {count} orders should be cool!; errors: {error_count}")
        # Create work items to be ingested by the next step in the process
        create_work_items(json_list=json_list)
        # TODO Sleeping just for dev/testing ...
        sleep(5)
        close = desktop.wait_for_element("close")
        desktop.click(close)
        sleep(1)
        print(
            f"\n\n{tag} desktop application should be closed because the work is done!\n"
        )
        try:
            if app.is_running:
                desktop.close_application(app)
        except Exception as e:
            print(
                f"{tag} could not close app, probably already closed by the click: {e}"
            )

    except Exception as e:
        print(f"{tag} Ran into the wall, Boss! probably image locator problem - {e}")
        if app.is_running:
            desktop.close_application(app)
            print(f"\n\n{tag} application should be closed because of error: {e}")
            raise ValueError(f"Probable locator error: {e}")

def _drive_order_screen(app, desktop: Desktop, json_list: list):
    customer_id = desktop.wait_for_element("customer_id")
    product_id = desktop.wait_for_element("product_id")
    quantity = desktop.wait_for_element("quantity")
    checkbox = desktop.wait_for_element("checkbox")
    send_order = desktop.wait_for_element("send_order")
    count = 0
    error_count = 0
    # create orders from the spreadsheet or csv downloaded from Azure Storage
    # For each row in the data, use the opened Windows app and do the dance
    try:
        for order_json in json_list:

            try:
                _handle_order(
                    desktop,
                    count,
                    customer_id,
                    product_id,
                    quantity,
                    checkbox,
                    send_order,
                    order_json,
                )
                count = count + 1
                sleep(1)
            except Exception as e:
                print(
                    f"\n{tag} The accelerator seems to be stuck! What we gonna do, Boss? - {e}\n"
                )
                error_count = error_count + 1
                continue

    except Exception as e:
        print(f"{tag} The tree moved and we crashed into it :) - {e}")
        if app.is_running:
            desktop.close_application(app)
            raise ValueError("Unable to drive the Order screen")

    return count, error_count

def _handle_order(
    desktop, count, customer_id, product_id, quantity, checkbox, send_order, order_json
):
    """Feed the Desktop app"""

    # Get the values from the dictionary
    customer_id_value = order_json[0]
    product_id_value = order_json[1]
    quantity_value = order_json[2]

    print(
        f"\n{tag} handling order #{count + 1}: customer: {customer_id_value} product: {product_id_value} quantity: {quantity_value}"
    )

    desktop.type_text_into(customer_id, f"{customer_id_value}", True, False)
    desktop.type_text_into(product_id, f"{product_id_value}", True, False)
    desktop.type_text_into(quantity, f"{quantity_value}", True, False)
    desktop.click(checkbox)
    desktop.click(send_order)

    print(
        f"{tag} Send Order button clicked!! - customer: {customer_id_value} product: {product_id_value} quantity: {quantity_value}"
    )

def _handle_login(desktop: Desktop):
    login = desktop.wait_for_element("login")
    print(f"{tag} login screen established; {login}")
    username = desktop.wait_for_element("username")
    password = desktop.wait_for_element("password")

    username_env = get_user_name()
    password_env = get_user_password()

    print(f"{tag} VAULT: username: {username_env} password: {password_env}")

    desktop.type_text_into(username, username_env, True, False)
    desktop.type_text_into(password, password_env, True, False)

    submit = desktop.wait_for_element("submit")
    desktop.click(submit)
    print(f"{tag} Submit button clicked!!")

    desktop.click("go_to_sales")
    print(f"{tag} Go to Orders button clicked!!\n")

def create_work_items(json_list: list):
    """Create work_items for next step"""
    print(f"{tag} creating work items from json_list: {len(json_list)}")
    for m in json_list:
        print(f"{tag} work item: {m}")
        workitems.outputs.create(payload=m)

    print(f"\n\n{tag} work items created: {len(workitems.outputs)} ....\n\n")
