# ha-sew-water

Home Assistant HACS integration to provide water meter readings for South East Water digital water meters

## Not yet ready to install as an integration

This is an unfinished work in progress.

You can manually set up the building blocks as described below.

## Manual Set Up

1. Install the pyscript integration from HACS
2. Install the spook integration from HACS
3. Install Browserless - either the addon if you're using a version of home assistant that supports addons https://github.com/alexbelgium/hassio-addons/tree/master/browserless_chrome or another way (typically docker - https://github.com/browserless/browserless/pkgs/container/base).
4. Restart Home Assistant
5. Create a folder called `pyscript` under your home assistant config directory (create the folder in the same folder that you can see `configuration.yaml`)
6. Copy the two files from the pyscript folder under code in this repo to that directory.
7. Create a datetime helper called `input_datetime.last_water_date` - it must be called Last Water Date so that the sensor is named `input_datetime.last_water_date` which is what the automation expects.![image](https://github.com/user-attachments/assets/ea1b7a54-c27a-45f5-a41d-3050688aa349)

8. Create a template sensor called - it must bec alled Next Water Date so that the sensor is named which is what the automation needs to automatically fetch water readings.  Paste the `nextwaterdate.jinja` from the `sensors` folder into the template field.![image](https://github.com/user-attachments/assets/1ac0679b-4606-4db6-874e-f8ae334c68bd)

9. Add the snippet from `configuration.yaml` in the `configuration` folder to your `configuration.yaml` in your home assistant
10. Restart home assistant
11. Create an automation using the `importwaterusage.yaml` in the `automations` folder.
12. Set the settings in the automation - water meter serial, South East Water userid and password, Browserless URL and Token
13. Set the Last Water Date to 11am on the day before your digital water meter was installed.
14. This should trigger the automation to get water readings day by day up to yesterday.  It waits one minute before each run to ensure that the last total is updated in the home assistant database so that it doesn't mess up totals, given the way that this integration inserts historical stats.
15. Add the water usage sensors to your energy dashboard.
