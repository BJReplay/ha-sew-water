# ha-sew-water

Home Assistant HACS integration to provide water meter readings for South East Water digital water meters

## Not yet ready to install as an integration

This is an unfinished work in progress.

You can manually set up the building blocks as described below.

## Manual Set Up

1. Install the pyscript integration from HACS
2. Install the spook integration from HACS
3. Install the Browserless addon if you're using a version of home assistant that supports addons https://github.com/alexbelgium/hassio-addons/tree/master/browserless_chrome or another way (typically docker - https://github.com/browserless/browserless/pkgs/container/base).
4. Restart Home Assistant
5. Create a folder called `pyscript` under your home assistant `config` directory (create the folder in the same folder that you can see `configuration.yaml`)
6. Copy the two files from the pyscript folder under code in this repo to that directory.
7. Create a datetime helper called `input_datetime.last_water_date` - it must be called Last Water Date so that the sensor is named `input_datetime.last_water_date` which is what the automation expects.
   ![image](https://github.com/user-attachments/assets/ea1b7a54-c27a-45f5-a41d-3050688aa349)
8. Create a template sensor called `sensor.next_water_date` - it must be called Next Water Date so that the sensor is named `sensor.next_water_date` which is what the automation needs to automatically fetch water readings.  Paste the `nextwaterdate.jinja` from the `sensors` folder into the template field.

   ![image](https://github.com/user-attachments/assets/1ac0679b-4606-4db6-874e-f8ae334c68bd)
   
9. Add the snippet from `configuration.yaml` in the `configuration` folder to your `configuration.yaml` in your home assistant
10. Create a folder callled `packages` if one does not yet exist under your home assistant `config` directory (create the folder in the same folder that you can see `configuration.yaml`)
11. Copy `sew.yaml` from the `automations` folder into the `packages` folder
12. If you don't have a `secrets.yaml` in your `config` folder, create one.
13. Add the secrets from `secrets.yaml` in the `configuration` folder to your `secrets.yaml` in your home assistant
14. Edit the secrets as required - your SEWL login details and browserless configuration.
15. Check that you can reach your browserless URL - e.g. http://192.168.1.125:3000/config and http://192.168.1.125:3000/docs, otherwise the rest won't work.
16. Restart home assistant
17. Set the Last Water Date to 11am on the day before your digital water meter was installed.
18. Go to Developer Tools, Actions, and paste in the following yaml, and run it by clicking on `Perform action` and confirm you get a green tick.
``` yaml
action: pyscript.force_water_state
data:
  stat_id: sensor.water_usage_mains
  tally: 0
```
  <img width="1746" height="492" alt="image" src="https://github.com/user-attachments/assets/3b72a8e4-e67a-4f9c-b91e-32e6c0c00cd3" />

19. Run the `Import water usage` automation.
20. This should trigger the automation to get water readings day by day up to yesterday.  It waits one minute before each run to ensure that the last total is updated in the home assistant database so that it doesn't mess up totals, given the way that this integration inserts historical stats.
21. Add the water usage sensors to your energy dashboard.
