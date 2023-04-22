"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Returns all of the Accounts"""
    app.logger.info("Request for Account list")
    accounts = []

    # Process the query string if any
    name = request.args.get("name")
    if name:
        accounts = Account.find_by_name(name)
    else:
        accounts = Account.all()

    # Return as an array of dictionaries
    results = [account.serialize() for account in accounts]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Retrieve a single Account
    This endpoint will return an Account based on it's id
    """
    app.logger.info("Request for Account with id: %s", account_id)

    # See if the account exists and abort if it doesn't
    account = Account.find(account_id)
    if not account:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{account_id}' could not be found.",
        )

    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")

    # Create the account
    account = Account()
    account.deserialize(request.get_json())
    account.create()

    # Create a message to return
    message = account.serialize()
    location_url = url_for("get_accounts", account_id=account.id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    Update an Account
    This endpoint will update an Account based the body that is posted
    """
    app.logger.info("Request to update account with id: %s", account_id)
    check_content_type("application/json")

    # See if the account exists and abort if it doesn't
    account = Account.find(account_id)
    if not account:
        abort(
            status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found."
        )

    # Update from the json in the body of the request
    account.deserialize(request.get_json())
    account.id = account_id
    account.update()

    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """
    Delete an Account
    This endpoint will delete an Account based the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", account_id)

    # Retrieve the account to delete and delete it if it exists
    account = Account.find(account_id)
    if account:
        account.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
