import traceback
from flask import jsonify

def handle_error(message, status_code=400, log_error=True):
    """
    Handle errors consistently across all endpoints.
    :param message: Error message to return to the client.
    :param status_code: HTTP status code (default is 400).
    :param log_error: Whether to log the error (default is True).
    :return: JSON response with the error message and status code.
    """
    if log_error:
        print(f"Error: {message}")
        traceback.print_exc()  # Print the full traceback to the console

    # Optionally include the traceback in the response (only for debugging)
    return jsonify({
        "error": message,
        "traceback": traceback.format_exc()  # Include traceback in the response
    }), status_code