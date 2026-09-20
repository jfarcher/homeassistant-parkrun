# parkrun for Home Assistant

<p align="center">
  <img src="custom_components/parkrun/brand/logo.png" alt="parkrun" width="300" />
</p>

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

### HACS

Use this link to directly go to the repository in HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jfarcher&repository=homeassistant-parkrun&category=integration)

_or_

1. Install [HACS](https://hacs.xyz) if you don't have it already
2. Open HACS in Home Assistant
3. Add `jfarcher/homeassistant-parkrun` as a custom repository (Integration)
4. Search for "parkrun"
5. Click the download button

Then restart Home Assistant, go to **Settings → Devices & services → Add integration**, and search for **parkrun**. Enter your barcode ID (`A1234567` or `1234567`) and the country site you normally use.

### Manual

1. Copy `custom_components/parkrun` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **parkrun**.
4. Enter your barcode ID (`A1234567` or `1234567`) and the country site you normally use.

## Notes

parkrun sometimes shows a bot check to datacentre IPs. A Home Assistant install on your home network usually works because it looks like a normal browser visit. If setup fails with a connection error, wait and try again.
