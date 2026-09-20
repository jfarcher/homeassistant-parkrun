# parkrun for Home Assistant

Custom integration that pulls public parkrun statistics into Home Assistant as sensors.

Setup is only your barcode ID and country website. parkrun barcodes are not accounts with passwords; the [official app API](https://developer.parkrun.com/#!/) needs a profile login that most parkrunners never create. This integration reads the same public results page anyone can open in a browser.

## What you get

After setup, Home Assistant creates a device for the athlete and sensors including:

- Total parkruns, junior parkruns, volunteer credits, events attended
- Personal best and best age grade
- Latest event, date, time, positions, age grade, and age category
- First parkrun and date, and the event you run most often
- Current run / volunteer club and how many to the next milestone
- Binary sensors for “latest run was a PB” and “latest run was a first timer at that event”

Results are polled every 6 hours.

## Install

1. Copy `custom_components/parkrun` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **parkrun**.
4. Enter your barcode ID (`A1234567` or `1234567`) and the country site you normally use.

## Notes

parkrun sometimes shows a bot check to datacentre IPs. A Home Assistant install on your home network usually works because it looks like a normal browser visit. If setup fails with a connection error, wait and try again.
