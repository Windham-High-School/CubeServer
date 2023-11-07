import os

API_WRAPPER_GIT_URL_CIRCUITPYTHON = os.environ.get(
    "API_WRAPPER_GIT_URL_CIRCUITPYTHON",
    "https://github.com/Windham-High-School/CubeServer-api-python.git",
)
API_WRAPPER_ZIP_FILENAME_CIRCUITPYTHON = os.environ.get(
    "API_WRAPPER_ZIP_FILENAME_CIRCUITPYTHON", "CubeServer-api-python.zip"
)
API_WRAPPER_PEM_FILENAME = os.environ.get("API_WRAPPER_PEM_FILENAME", "cert.pem")
