# hass_cc_template

Template repository for Home Assistant Custom Component

Change "hass_template" and "hass_cc_template" in all files and direcory names to appropriate name

[![hass_template](https://img.shields.io/github/v/release/astrandb/hass_cc_template)](https://github.com/astrandb/hass_cc_template/releases/latest) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) ![Validate with hassfest](https://github.com/astrandb/hass_cc_template/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2021.svg) [![hass_template_downloads](https://img.shields.io/github/downloads/astrandb/hass_cc_template/total)](https://github.com/astrandb/hass_cc_template)

# hass_template Integration for Home Assistant

_Work in progress_

Known limitations: There is only limited error and exception handling in this pre-release.

This integration will represent .......

## Installation

Make sure you have the credentials available for your account with hass_template cloud.

### Preferred download method

- Use HACS, add this repo as a custom repository and install hass_template integration.
- Restart Home Assistant

### Manual download method

- Copy all files from custom_components/hass_template in this repo to your config custom_components/hass_template
- Restart Home Assistant

### Setup

Request a client_id and client_secret from the manufacturer and
enter following lines to `configuration.yaml`

```yaml
hass_template:
  client_id: your_client_id
  client_secret: your_client_secret
```

Goto Integrations->Add and select hass_template

Follow instructions to authenticate with hass_template cloud server. Allow full access for Home Assistant client.

## Disclaimer

The package and its author are not affiliated with hass_template. Use at your own risk.

## License

The package is released under the MIT license.
