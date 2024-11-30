// test if string (e.g. recycled meter serial) is blank
const isBlank = function (str) {
    return (!!!str || /^\s*$/.test(str));
  };

// construct man body for aura including date and meter serial
const req_body = function (date_for, meter_serial) {
    return 'message=%7B%22actions%22%3A%5B%7B%22id%22%3A%222576%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2Fcm_AccountBillingUsageAURA%2FACTION%24getDigitalMeterUsage%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3APortalDataHub%22%2C%22params%22%3A%7B%22a'
        + 'DateFrom%22%3A' + date_for
        + '%2C%22a'
        + 'DateTo%22%3A' + date_for
        + '%2C%22aContext%22%3A%22Daily%22%2C%22'
        + 'meterSerialNos%22%3A%5B%22' + meter_serial
        + '%22%5D%2C%22billingAccIds%22%3A%5B%22a085K000003DW2kQAG%22%5D%2C%22aDataRequest%22%3A%22dataUsage%22%7D%7D%5D%7D'
        + '&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22eGx3MHlRT1lEMUpQaWVxbGRUM1h0Z2hZX25NdHFVdGpDN3BnWlROY1ZGT3cyNTAuOC40LTYuNC41%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%22wi0I2YUoyrm6Lo80fhxdzA%22%2C%22COMPONENT%40markup%3A%2F%2Finstrumentation%3Ao11ySecondaryLoader%22%3A%221JitVv-ZC5qlK6HkuofJqQ%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D'
        + '&aura.pageURI=%2Fs%2Fusage'
        + '&aura.token=';
}

export default async function ({ page, context }) {

  const { mains_water_serial, sew_username, sew_password, get_recycled, target_date, recycled_water_serial } = context;

  var target_unix_date = new Date()

  if (isBlank(target_date)) {
    // Use Yesterday's date
    let yesterdayDate = new Date();
    yesterdayDate.setDate(yesterdayDate.getDate() - 1);
    yesterdayDate.setHours(0, 0, 0 ,0);
    target_unix_date = yesterdayDate.valueOf();
  } else {
    // cast date parameter to date only and convert to unix format
    let date = new Date(target_date);
    date.setHours(0, 0, 0 ,0);
    target_unix_date = date.valueOf();
  }

  // only check for recycled if the flag is passed or the meter serial is non-blank
  let recycled = new Boolean();
  recycled = (!isBlank(recycled_water_serial)) || get_recycled;

  // Navigate to SEW website
  await page.goto('https://my.southeastwater.com.au/s/login/');

  // Type in username
  const username = await page.waitForSelector('input[name=\x22username\x22]', {timeout: 5000});
  await username.type(sew_username);

  // Type in password
  const password = await page.waitForSelector('input[name=\x22password\x22]', {timeout: 5000});
  await password.type(sew_password);

  // Perform login
  await Promise.all([
    page.keyboard.press('Enter'),
    page.waitForNavigation(),
  ]);

  await new Promise(res => setTimeout(res, 5000)); // wait for 5 seconds

  // get aura body query for mains water meter
  var body = req_body(target_unix_date, mains_water_serial);
  // get mains water meter readings
  var mains_usage_data = await page.evaluate((body) => {
    const getUsage = (body) => {
      var usage = fetch('https://my.southeastwater.com.au/s/sfsites/aura?r=100&other.cm_AccountBillingUsageAURA.getDigitalMeterUsage=1', {
        'headers': {
          'accept': '*/*',
          'accept-language': 'en-US,en;q=0.9,nb;q=0.8',
          'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'priority': 'u=1, i',
        },
        'referrer': 'https://my.southeastwater.com.au/s/usage',
        'referrerPolicy': 'origin-when-cross-origin',
        'body': body + localStorage.getItem('$AuraClientService.token$siteforce:communityApp'),
        'method': 'POST',
        'mode': 'cors',
        'credentials': 'include'
      })
      .then( response => {
        return response.text(); // convert response to JSON
      }) // changed through to next function
      .then(function(data) {
        return data; // make function return response data
      });
      return usage; // return raw usage data
    }
    return getUsage(body);
  }, body);

  // convert mains to json
  var mains_usage_data_json_string = JSON.parse(JSON.parse(mains_usage_data).actions[0].returnValue).usage;

  if (recycled) {
    // get aura body query for recycled water meter
    var body = req_body(target_unix_date, recycled_water_serial);
    // get recycled water meter readings
    var recycled_usage_data = await page.evaluate((body) => {
      const getUsage = (body) => {
        var usage = fetch('https://my.southeastwater.com.au/s/sfsites/aura?r=100&other.cm_AccountBillingUsageAURA.getDigitalMeterUsage=1', {
          'headers': {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,nb;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'priority': 'u=1, i',
          },
          'referrer': 'https://my.southeastwater.com.au/s/usage',
          'referrerPolicy': 'origin-when-cross-origin',
          'body': body + localStorage.getItem('$AuraClientService.token$siteforce:communityApp'),
          'method': 'POST',
          'mode': 'cors',
          'credentials': 'include'
        })
        .then( response => {
          return response.text(); // convert response to JSON
        }) // changed through to next function
        .then(function(data) {
          return data; // make function return response data
        });
        return usage; // return raw usage data
      }
      return getUsage(body);
    }, body);

    // convert recycled to json
    var recycled_usage_data_json_string = JSON.parse(JSON.parse(recycled_usage_data).actions[0].returnValue).usage;

    var combined_usage = {
      'mains': JSON.parse(mains_usage_data_json_string)[0],
      'recycled': JSON.parse(recycled_usage_data_json_string)[0]
    };
  } else {
    var combined_usage = {
      'mains': JSON.parse(mains_usage_data_json_string)[0]
    };
  }
  return combined_usage;
}