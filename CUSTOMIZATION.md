# Customization

# Customizing the build/installation
Build variables are found in [.env](./.env)

## Customizing the game:
To customize the game rules and elements beyond the options available in the admin panel, see the following files:

- [config.py](./config.py)

    This file describes the "hard-coded" configuration for the server. Things such as the name, description, credits, etc. are set here, in addition to other similar constants. This is installed to a location in CubeServer-common by [configure.sh](./tools/configure.sh) prior to the build.

- [team.py](./src/CubeServer-common/cubeserver_common/models/team.py)

    This file defines the model classes for storing team data, laying out the structure for what applies to individual teams.

- [rules.py](./src/CubeServer-common/cubeserver_common/models/config/rules.py)

    This file defines the model class for storing the game ruleset, and handles the actual scoring of points.

- [scoring](./src/CubeServer-common/cubeserver_common/models/scoring/)

    This package contains miscellaneous scoring utility classes, such as for calculating multipliers.
