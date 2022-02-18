[![Miele](https://img.shields.io/github/v/release/astrandb/miele)](https://github.com/astrandb/miele/releases/latest) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Validate with hassfest](https://github.com/astrandb/miele/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2022.svg) [![Miele_downloads](https://img.shields.io/github/downloads/astrandb/miele/total)](https://github.com/astrandb/miele) [![Miele_downloads](https://img.shields.io/github/downloads/astrandb/miele/latest/total)](https://github.com/astrandb/miele)

# Miele Integration for Home Assistant

_Work in progress - not feature complete_

The capabilities are based on Miele API version 1.0.5. The official capability overview is here https://www.miele.com/developer/assets/API_V1.x.x_capabilities_by_device.pdf . Note that this matrix is not entirely correct. Some device lack support and some devices support features that are not marked.

All supported appliances will show a status sensor, some appliances will show more sensors, however only freezers, refridgerators, dishwashers and washer/dryers will have a more complete support. Changes on the appliances will be pushed to HA and displayed immediately. As a backup the status is read from the cloud every 60 seconds.

In upcoming releases there will be support for more appliance types and more complete support for existing appliances.

Known limitations: There is only limited error and exception handling in this release.

## Installation

Make sure you have the credentials available for your account with Miele cloud. You have to register on https://www.miele.com/developer/

### Preferred download method

- Use HACS, add this repo as a custom repository and install Miele integration.
- Restart Home Assistant

### Manual download method

- Copy all files from custom_components/miele in this repo to your config custom_components/miele
- Restart Home Assistant

### Setup

Request a client_id and client_secret from the manufacturer and
enter following lines to `configuration.yaml`

```yaml
miele:
  client_id: your_client_id
  client_secret: your_client_secret
```

Goto Integrations->Add and select Miele

Follow instructions to authenticate with Miele cloud server. Allow full access for Home Assistant client.

### Development

There are many ways to setup a development environment.
Following procedure works fine in the hands of the maintainer developing with VS Code on WSL2/Windows.

- Make sure you have python3.9 installed on your WSL.
- Create a fork on github

```
$ git clone https://github.com/{your_user}/miele
$ cd miele
$ make install_dev
```

Home Assistant has defined a code style. Run `make lint` before pushing your changes to align with the peferred style.

There are many ways to test the integration, two examples are:

- copy all files in `custom_comonents/miele` to `custom_components/miele` in your HA configuration directory
- mount `custom_components/miele` into a HA development container

### Debugging and filing issues

If you find bugs or other issues please download diagnostic information from the Miele integration card or from the device page and attach the file to your issue report.
One recurring issue is the translation of Program name and phases. This is due to sparse, if any, documentation from Miele. One way to assist with the fact collection is to install a blueprint automation that will log states from the selected sensor with some additional information to the Home Assistant log.

The blueprint can be found here https://gist.github.com/astrandb/2F5ec47d6979b590639d23144142ae3100

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgist.github.com%2Fastrandb%2F5ec47d6979b590639d23144142ae3100)

## Disclaimer

The package and its author are not affiliated with Miele. Use at your own risk.

## License

The package is released under the MIT license.
