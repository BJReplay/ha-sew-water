from datetime import datetime  # noqa: D100, INP001
import json
import os
from pathlib import Path

import requests

MAINS_WATER_SERIAL = "mains_water_serial"
RECYCLED_WATER_SERIAL = "recycled_water_serial"
SEW_USERNAME = "sew_username"
SEW_PASSWORD = "sew_password"
TARGET_DATE = "target_date"
CODE = "code"
CONTEXT = "context"
GET_RECYCLED = False


@service  # noqa: F821
def import_water_usage(
    mains_water_stat_id,
    mains_water_serial,
    sew_username,
    sew_password,
    target_date: datetime,
    browserless: str,
    token: str,
    recycled_water_stat_id: str = "",
    recycled_water_serial: str = "",
):
    """Get Water Usage for Date.

    description: Imports Water Usage from South East Water's
    Website.  Logs In, Navigates to Water Usage Summary,
    Downloads Data for given date, Imports into Sensor(s).

    Arguments:
        mains_water_stat_id: The sensor to return the mains water usage to. Example: sensor.water_usage_mains
        mains_water_serial: The serial number of the mains water meter. Example: SAHA000000
        sew_username: Your Username for the South East Water (SEW) website. Example: myusername@gmail.com
        sew_password: Your Password for the South East Water (SEW) website. Example: myC0mpl3xP@55w0rd
        target_date: The date you want to import data for. Example: 2024-11-27
        browserless: The URL that the browserless instance is running on. Example: http://localhost:3000
        token: The browserless token to use. Example: 6R0W53R135510

    Keyword Arguments:
        recycled_water_stat_id: The sensor to return the mains water usage to. Example: sensor.water_usage_recycled (default: {""})
        recycled_water_serial: The serial number of the mains water meter. Example: RAHA000000 (default: {""})

    """

    # Open the puppeteer JS file - have to use OS open functions to bypass HASS blocking IO restriction
    js_exec_path = f"{hass.config.config_dir}/pyscript/get_target_date_water_usage.js"  # noqa: F821
    fd = os.open(js_exec_path, os.O_RDONLY)
    js_exec_str = os.read(fd, Path(js_exec_path).stat().st_size)
    js_executable = js_exec_str.decode()
    os.close(fd)

    context = {
        MAINS_WATER_SERIAL: mains_water_serial,
        RECYCLED_WATER_SERIAL: recycled_water_serial,
        SEW_USERNAME: sew_username,
        SEW_PASSWORD: sew_password,
        TARGET_DATE: target_date,
        GET_RECYCLED: False,
    }

    headers = {"Content-Type": "application/json"}
    data = json.dumps({CODE: js_executable, CONTEXT: context})

    usage_response = task.executor(  # noqa: F821
        requests.request,
        method="POST",
        url=f"{browserless}/function?token={token}",
        headers=headers,
        data=data,
    )
    usage_response_data = json.loads(usage_response.text)

    # Import the data to statistics
    import_water_usage_data(mains_water_stat_id, "mains", usage_response_data)


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

    readings = data[type]["Readings"]

    tally = starting_point

    for reading in readings:
        litres = reading["Measurement"]

        if litres is None:
            continue  # skip value if no usage

        data_date = reading["Date"].replace(".000Z", "").replace("T", " ")
        datetime_object = datetime.strptime(data_date, "%Y-%m-%d %H:%M:%S")

        start = str(datetime_object.astimezone())
        tally += litres

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
