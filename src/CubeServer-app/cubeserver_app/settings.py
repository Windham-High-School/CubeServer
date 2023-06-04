import os

API_WRAPPER_GIT_URL_ARDUINO = os.environ.get(
    "API_WRAPPER_GIT_URL_ARDUINO",
    "https://github.com/snorklerjoe/CubeServer-api-arduino.git",
)
API_WRAPPER_ZIP_FILENAME_ARDUINO = os.environ.get(
    "API_WRAPPER_ZIP_FILENAME_ARDUINO", "CubeServer-api-arduino.zip"
)
API_WRAPPER_GIT_URL_PYTHON = os.environ.get(
    "API_WRAPPER_GIT_URL_PYTHON",
    "https://github.com/snorklerjoe/CubeServer-api-python.git",
)
API_WRAPPER_ZIP_FILENAME_PYTHON = os.environ.get(
    "API_WRAPPER_ZIP_FILENAME_PYTHON", "CubeServer-api-python.zip"
)
API_WRAPPER_GIT_URL_CIRCUITPYTHON = os.environ.get(
    "API_WRAPPER_GIT_URL_CIRCUITPYTHON",
    "https://github.com/snorklerjoe/CubeServer-api-python.git",
)
API_WRAPPER_ZIP_FILENAME_CIRCUITPYTHON = os.environ.get(
    "API_WRAPPER_ZIP_FILENAME_CIRCUITPYTHON", "CubeServer-api-python.zip"
)
API_WRAPPER_PEM_FILENAME = os.environ.get("API_WRAPPER_PEM_FILENAME", "cert.pem")
BEACON_CODE_GIT_URL = os.environ.get(
    "BEACON_CODE_GIT_URL", "https://github.com/snorklerjoe/CubeServer-beacon.git"
)
