# ha-sew-water

Home Assistant package and additional components to provide water meter readings for South East Water digital water meters

## Not yet ready to install as an integration

This started off as plans for an integration, but is currently just a package that includes the key components.

You can manually set up the building blocks as described below.

## Manual Set Up

1. Install the pyscript integration from HACS
2. Install the spook integration from HACS
3. Install the Browserless addon if you're using a version of home assistant that supports addons https://github.com/alexbelgium/hassio-addons/tree/master/browserless_chrome or another way (typically docker - https://github.com/browserless/browserless/pkgs/container/base).
4. Restart Home Assistant
5. Create a folder called `pyscript` under your home assistant `config` directory (create the folder in the same folder that you can see `configuration.yaml`)
6. Copy the two files from the pyscript folder under code in this repo to that directory.
7. Check to see if you have section in your  `configuration.yaml` called `homeassistant:`
8. If not, add a section header starting in the first column with the contents `homeassistant:` and under that, indented two spaces, add an entry

``` yaml
  packages: !include sew_package.yaml
```

9. If you already had a `homeassistant:` entry, check to see if you have an entry under that specifying `packages:`
10. If so, check to see whether it uses the format `!include_dir_merge_named packages/` or `!include packages.yaml`
11. If the format is `!include_dir_merge_named packages/` then copy `sew.yaml` into the folder specified in the include line.
12. You don't need to modify the configuration file ifyou have `!include_dir_merge_named packages/` as it looks for all files in the folder.
13. If the format is `!include packages.yaml` copy `sew_package.yaml` into the configuration folder and an include line:

``` yaml
  packages: !include sew_package.yaml
```

13. Create a datetime helper called `input_datetime.last_water_date` - it must be called Last Water Date so that the sensor is named `input_datetime.last_water_date` which is what the automation expects.

   ![image](https://github.com/user-attachments/assets/ea1b7a54-c27a-45f5-a41d-3050688aa349)

14. Create a template sensor called `sensor.next_water_date` - it must be called Next Water Date so that the sensor is named `sensor.next_water_date` which is what the automation needs to automatically fetch water readings.  Paste the `nextwaterdate.jinja` from the `sensors` folder into the template field.

   ![image](https://github.com/user-attachments/assets/1ac0679b-4606-4db6-874e-f8ae334c68bd)
   
15. If you don't have a `secrets.yaml` in your `config` folder, create one.
16. Add the secrets from `secrets.yaml` in the `configuration` folder to your `secrets.yaml` in your home assistant
17. Edit the secrets as required - your SEWL login details and browserless configuration.  **Make sure you do not use localhost or 127.0.0.1 as the browserless location.**
18. You can either retrieve your billingAccountId and meterId from Local Storage under Application Data while browsing the South East Water site, and save them, or leave the entries in the secrets file with no date - either will work:

Either: Using Developer Tools (usually hit F12 while browsing your South East Water account page), click on Application, then Local Storage, then https://my.southeastwater.com.au, then look at the LSSIndex:LOCAL{"namespace":"c""} to confirm which items labled 1 thorugh 5 are your BillingAccountID and meterID - usually 1 and 2, then copy those values and save them in Secrets

<img width="1127" height="1101" alt="image" src="https://github.com/user-attachments/assets/539cbda5-009f-4dca-801c-cd3742ecc128" />

<img width="428" height="80" alt="image" src="https://github.com/user-attachments/assets/92af91df-4c8d-495b-93b2-4b7abbe02a2a" />

Or: Don't bother retrieving this data, just save your South East Water userid and password in secrets, and leave the sew_billing_account_id and sew_meter_id blanks:

<img width="430" height="80" alt="image" src="https://github.com/user-attachments/assets/89532c97-43ee-4840-b191-53781ec23c6d" />


19. Check that you can reach your browserless URL - e.g. http://192.168.1.125:3000/config and http://192.168.1.125:3000/docs, otherwise the rest won't work.
20. **Restart home assistant**
21. Set the Last Water Date to 11am on the day before your digital water meter was installed.
22. Go to Developer Tools, Actions, and paste in the following yaml, and run it by clicking on `Perform action` and confirm you get a green tick.

``` yaml
action: pyscript.force_water_state
data:
  stat_id: sensor.water_usage_mains
  tally: 0
```
  <img width="1746" height="492" alt="image" src="https://github.com/user-attachments/assets/3b72a8e4-e67a-4f9c-b91e-32e6c0c00cd3" />

22. Run the `Import water usage` automation.
23. This should trigger the automation to get water readings day by day up to yesterday.  It waits one minute before each run to ensure that the last total is updated in the home assistant database so that it doesn't mess up totals, given the way that this integration inserts historical stats.
24. Add the water usage sensors to your energy dashboard.
