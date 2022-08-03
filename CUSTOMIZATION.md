# Customization

# Customizing the build/installation
Build variables are found in [.env](./.env)

## Customizing the game:
To customize the game rules and elements beyond the options available in the admin panel, see the following files:

- [config.py](./src/webapp/app/config.py)

    This file describes the "hard-coded" configuration for the server. Things such as the name, description, credits, etc. are set here, in addition to other similar constants.

- [team.py](./src/webapp/app/models/team.py)

    This file defines the model classes for storing team data, laying out the structure for what applies to individual teams