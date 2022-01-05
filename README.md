[![Miele](https://img.shields.io/github/v/release/astrandb/miele)](https://github.com/astrandb/miele/releases/latest) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Validate with hassfest](https://github.com/astrandb/miele/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2021.svg) [![Miele_downloads](https://img.shields.io/github/downloads/astrandb/miele/total)](https://github.com/astrandb/miele)

# Miele Integration for Home Assistant

_Work in progress_

This is a first release / Proof of Concept

The capabilities are based on Miele API version 1.0.5

All supported appliances will show a status sensor, some appliances will show more sensors, however only freezers and refridgerators will have a more complete support. Changes on the appliances will be pushed to HA and displayed immediately. As a backup the status is read from the cloud every 60 seconds.

In an upcoming release there will be support for more appliance types.


Known limitations: There is only limited error and exception handling in this pre-release.



## Installation

Make sure you have the credentials available for your account with Miele cloud.

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
