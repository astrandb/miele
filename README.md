[![Miele](https://img.shields.io/github/v/release/astrandb/miele)](https://github.com/astrandb/miele/releases/latest) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Validate with hassfest](https://github.com/astrandb/miele/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2022.svg) [![Miele_downloads](https://img.shields.io/github/downloads/astrandb/miele/total)](https://github.com/astrandb/miele)

# Miele Integration for Home Assistant

_Work in progress - not feature complete_ 

The capabilities are based on Miele API version 1.0.5. The official capability overview is here https://www.miele.com/developer/assets/API_V1.x.x_capabilities_by_device.pdf . Note that this matrix is not entirely correct. Some device lack support and some devices support features that are not marked.

All supported appliances will show a status sensor, some appliances will show more sensors, however only freezers, refridgerators, dishwashers and washer/dryers will have a more complete support. Changes on the appliances will be pushed to HA and displayed immediately. As a backup the status is read from the cloud every 60 seconds.

In upcoming releases there will be support for more appliance types and more complete support for existing appliances.


Known limitations: There is only limited error and exception handling in this pre-release.



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

## Disclaimer

The package and its author are not affiliated with Miele. Use at your own risk.

## License

The package is released under the MIT license.
