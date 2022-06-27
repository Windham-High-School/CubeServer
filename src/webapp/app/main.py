"""Allows running/serving the web application."""

import app

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=8080)
