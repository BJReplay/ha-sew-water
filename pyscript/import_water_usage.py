from datetime import datetime, timedelta, date  # noqa: D100, INP001
import json
import os
from pathlib import Path
import logging
import requests

SEW_USERNAME = "sew_username"
SEW_PASSWORD = "sew_password"
SEW_BAID = "sew_baid"
SEW_METERID = "sew_meterid"
TARGET_DATE = "target_date"
CODE = "code"
CONTEXT = "context"
GET_RECYCLED = False

_LOGGER = logging.getLogger(__name__)

@service  # noqa: F821
def import_yesterdays_water_usage(
    mains_water_stat_id,
    sew_username,
    sew_password,
    browserless: str,
    token: str = "",
):
    """Get Water Usage for Yesterday.

    description: Imports Water Usage from South East Water's
    Website.  Logs In, Navigates to Water Usage Summary,
    Downloads Data for given date, Imports into Sensor(s).

    Arguments:
        mains_water_stat_id: The sensor to return the mains water usage to. Example: sensor.water_usage_mains
        sew_username: Your Username for the South East Water (SEW) website. Example: myusername@gmail.com
        sew_password: Your Password for the South East Water (SEW) website. Example: myC0mpl3xP@55w0rd
        browserless: The URL that the browserless instance is running on. Example: http://localhost:3000

    Keyword Arguments:
        token: The browserless token to use. Example: 6R0W53R135510, or BLANK if running on the HASS addon

    """
    yesterday = date.today() - timedelta(days = 1)

    import_water_usage(
        mains_water_stat_id=mains_water_stat_id,
        sew_username=sew_username,
        sew_password=sew_password,
        target_date=yesterday,
        browserless=browserless,
        token=token)

@service  # noqa: F821
def import_water_usage(
    mains_water_stat_id,
    sew_username,
    sew_password,
    target_date: datetime,
    browserless: str,
    token: str = "",
    default_sew_baId: str = "",
    default_sew_meterId: str = "",
):
    """Get Water Usage for Date.

    description: Imports Water Usage from South East Water's
    Website.  Logs In, Navigates to Water Usage Summary,
    Downloads Data for given date, Imports into Sensor(s).

    Arguments:
        mains_water_stat_id: The sensor to return the mains water usage to. Example: sensor.water_usage_mains
        sew_username: Your Username for the South East Water (SEW) website. Example: myusername@gmail.com
        sew_password: Your Password for the South East Water (SEW) website. Example: myC0mpl3xP@55w0rd
        target_date: The date you want to import data for. Example: 2024-11-27
        browserless: The URL that the browserless instance is running on. Example: http://localhost:3000

    Keyword Arguments:
        token: The browserless token to use. Example: 6R0W53R135510, or blank if running on the HASS addon
        default_sew_baId: The default SEW internal Account ID (baId) to pass in. Retrieve from Local Storage using developer tools. Example: b02341111112b5EITGY
        default_sew_meterId: The default SEW internal Meter ID (meterId) to pass in. Retrieve from Local Storage using developer tools. Example: c2E82222222ZG1FEBT

    """

    # Open the puppeteer JS file - have to use OS open functions to bypass HASS blocking IO restriction
    js_exec_path = f"{hass.config.config_dir}/pyscript/get_target_date_water_usage.js"  # noqa: F821
    fd = os.open(js_exec_path, os.O_RDONLY)
    js_exec_str = os.read(fd, Path(js_exec_path).stat().st_size)
    js_executable = js_exec_str.decode()
    os.close(fd)

    if not target_date or target_date == "":
        target_date = datetime.now() - timedelta(days=1)
    initial_date: datetime = datetime.strptime(target_date, "%Y-%m-%d")
    current_date: datetime = datetime.strptime(target_date, "%Y-%m-%d")
    current_date_str: str = current_date.strftime("%Y-%m-%d")
    retrieved_date: datetime = current_date - timedelta(days = 1)

    while retrieved_date < current_date:

        context = {
            SEW_USERNAME: sew_username,
            SEW_PASSWORD: sew_password,
            TARGET_DATE: current_date_str,
            GET_RECYCLED: False,
            SEW_BAID: default_sew_baId,
            SEW_METERID: default_sew_meterId
        }

        headers = {"Content-Type": "application/json"}
        data = json.dumps({CODE: js_executable, CONTEXT: context})
        if token == "" or token is None:
            url = f"{browserless}/function"
        else:
            url = f"{browserless}/function?token={token}"

        usage_response = task.executor(  # noqa: F821
            requests.request,
            method="POST",
            url=url,
            headers=headers,
            data=data,
        )

        usage_response_data = json.loads(usage_response.text)
        retrieved_date: datetime = datetime.strptime(usage_response_data["mains"]["apiDate"].replace("T00:00:00+00:00", ""), "%Y-%m-%d")

        if retrieved_date >= initial_date:
            # Import the data to statistics
            import_water_usage_data(mains_water_stat_id, "mains", usage_response_data)
        else:
            # bump forward a day to account for SEW retrieving a day prior to request, and loop
            current_date = current_date + timedelta(days = 1)
            current_date_str: str = current_date.strftime("%Y-%m-%d")
        
        if not target_date or target_date == "":
            break
        
        if retrieved_date >= initial_date:
            break

@service  # noqa: F821
def import_file_water_usage(stat_id, file_path_under_config):
    """Get Water Usage by loading file.  Concatenates Config Dir / File Path.

    fields:
        stat_id:
            example: sensor.water_usage_mains
            required: true
        file_path_under_config:
            example: pyscript/my-southeastwater-com-au.json
            required: true
    """
    # Open the JSON file downloaded via the browserless debugger
    json_file_path = f"{hass.config.config_dir}/{file_path_under_config}"  # noqa: F821
    fd = os.open(json_file_path, os.O_RDONLY)
    json_file_data = os.read(fd, Path(json_file_path).stat().st_size)
    os.close(fd)

    usage_response_data = json.loads(json_file_data)

    # Import the data to statistics
    import_water_usage_data(stat_id, "mains", usage_response_data)

def import_water_usage_data(stat_id, type, data):
    """Import Water Usage Data.

    fields:
        stat_id:
            example: sensor.water_usage_mains
            required: true
        type:
            example: mains
            required: true
        data:
            example: json data returned from South East Water
            required: true
    """
    starting_point = float(state.get(stat_id))  # noqa: F821

    readings = data[type]["readings"]

    tally = starting_point

    for idx, reading in enumerate(readings):
        litres = reading

        if litres is None:
            continue  # skip value if no usage

        data_date = data[type]["apiDate"].replace("+00:00", "").replace("T", " ")
        datetime_object = datetime.strptime(data_date, "%Y-%m-%d %H:%M:%S") + timedelta(hours=idx)

        start = str(datetime_object.astimezone())
        tally += litres #TODO

        statistic_element = {"start": start, "state": tally, "sum": tally, "max": tally}

        # Import recorder statistics
        recorder.import_statistics(  # noqa: F821
            statistic_id=stat_id,
            source="recorder",
            unit_of_measurement="L",
            has_sum=True,
            has_mean=False,
            stats=[statistic_element],
        )

    log.info("Imported statistics")  # noqa: F821
    if tally > starting_point:
        state.set("input_datetime.last_water_date", start)

@service  # noqa: F821
def force_water_state(stat_id, tally):
    """Force State.

    fields:
        stat_id:
            description: the mains water stat id to force
            example: sensor.water_usage_mains
            required: true
        tally:
            description: the tally to force
            example: 123
            required: true
    """
    state.set(stat_id, tally)  # noqa: F821
