[![Miele](https://img.shields.io/github/v/release/astrandb/miele)](https://github.com/astrandb/miele/releases/latest) [![hacs_badge](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/integration) ![Validate with hassfest](https://github.com/astrandb/miele/workflows/Validate%20with%20hassfest/badge.svg) ![Maintenance](https://img.shields.io/maintenance/yes/2024.svg) [![Miele_downloads](https://img.shields.io/github/downloads/astrandb/miele/total)](https://github.com/astrandb/miele) [![Miele_downloads](https://img.shields.io/github/downloads/astrandb/miele/latest/total)](https://github.com/astrandb/miele)

# Miele Integration for Home Assistant

The capabilities are based on Miele API version 1.0.7. The official capability overview is here https://www.miele.com/developer/assets/API_V1.x.x_capabilities_by_device.pdf . Note that this matrix is not entirely correct. Some devices lack support and some devices support features that are not marked.

All supported appliances will show a status sensor, some appliances will show more sensors, however only freezers, refridgerators, coffee machines, dishwashers and washer/dryers will have a more complete support. Changes on the appliances will be pushed to HA and displayed immediately. As a backup the status is read from the cloud every 60 seconds.

Read more on design philosophy etc in the [Wiki](https://github.com/astrandb/miele/wiki)

## Installation

Make sure you have the app credentials available for your account with Miele cloud. You have to register on https://www.miele.com/developer/.
If you have an existing integration with the name "miele" you are recommended to remove it before attemping to install this one.

### Preferred download method

- Use HACS, search for Miele integration and download it.
- Restart Home Assistant

### Manual download method

- Copy all files from custom_components/miele in this repo to your config custom_components/miele
- Restart Home Assistant

### Setup

Goto `Integrations` > `Add Integration` and select `Miele`. Sometimes you must refresh the browser cache to find the integration.

Follow instructions to authenticate with Miele cloud server. First, you'll provide the app credentials acquired at https://www.miele.com/developer/.
Next, you'll sign in using your Miele account. Allow full access for the Home Assistant client.

### Support - Wiki - Documentation

Documentation (at least some...) can be found in the [wiki](https://github.com/astrandb/miele/wiki)

[Discussion forum](https://github.com/astrandb/miele/discussions)

[Discord chat](https://discord.gg/Us4PSG74vw)

### Development

There are many ways to setup a development environment.

#### Dev Container

The recommended option is to use the VS Code Dev Container. You need to have Docker installed.

1. For best performance, clone the repo in a named volume.
1. Open a new, empty window in VS Code.
1. Press `Ctrl`+`Shift`+`P` and select `Dev Containers: Clone Respository in Named Container Volume`
1. Fill in your repo and your chosen names at the prompts
1. Wait for the container to be built

1. Press `Ctrl`+`Shift`+`P` and select `Tasks: Run Task` > `Run Home Assistant on port 9123`.
1. Wait for Home Assistant to start and go to http://localhost:9123/.
1. Walk through the Home Assistant first-launch UI.
1. Go to http://localhost:9123/config/integrations, click `Add Integration` and add the `Miele` integration.
1. To debug, press `F5` to attach to the Home Assistant running in the container.
1. Your configuration.yaml will be persistent (survives rebuild of container).

#### Without a Dev Container

Alternatively, you can run Home Assistant directly on your machine/WSL2. The following procedure works fine in the hands of the maintainer developing with VS Code on WSL2/Windows.

- Make sure you have at least python3.11 installed on your WSL.
- Create a fork on github

```
$ git clone https://github.com/{your_user}/miele
$ cd miele
$ make install_dev
```

Home Assistant has defined a code style. Run `make lint` before pushing your changes to align with the peferred style.

There are many ways to test the integration, three examples are:

- run Home Assistant in the development container as described above

- copy all files in `custom_comonents/miele` to `custom_components/miele` in your HA configuration directory
- mount `custom_components/miele` into a HA development container

### Translation
To handle submission of translations we are using [Lokalise](https://lokalise.com/login/). They provide us with an amazing platform that is easy to use and maintain.

To help out with the translation of Miele integration  you need an account on Lokalise, the easiest way to get one is to [click here](https://lokalise.com/login/)  then select "Log in with GitHub".

When you have created the account, [click here](https://app.lokalise.com/public/50153460650965e9a01e21.29484567/) to join the project. If you want to add a new language, please open an issue.

The translations are pulled when a new release of the integration is prepared. So you must wait until there is a new release before you look for your updates.

If you want to add new elements that need translation you should enter them in /translations/en.json and submit a PR. The new keys will appear in Lokalise when the PR is merged.

### Debugging and filing issues

If you find bugs or other issues please download diagnostic information from the Miele integration card or from the device page and attach the file to your issue report.
One recurring issue is the translation of Program name and phases. This is due to sparse, if any, documentation from Miele. One way to assist with the fact collection is to install a blueprint automation that will log states from the selected sensor with some additional information to the Home Assistant log. Create one automation for each sensor you want to monitor

The blueprint can be found here https://gist.github.com/astrandb/5ec47d6979b590639d23144142ae3100

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgist.github.com%2Fastrandb%2F5ec47d6979b590639d23144142ae3100)

## Disclaimer

The package and its author are not affiliated with Miele. Use at your own risk.

## License

The package is released under the MIT license.

## Support and cooperation
This project is supported by

[<img src="https://raw.githubusercontent.com/astrandb/documents/fef0776bbb7924e0253b9755d7928631fb19d5c7/img/Lokalise_logo_colour_black_text.svg" width=120>](https://lokalise.com)
