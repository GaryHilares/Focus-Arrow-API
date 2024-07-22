from flask import Flask, render_template, request, Response
from liberty_arrow import bootstrap
from liberty_arrow.domain.commands import (
    ConfirmEmail,
    SendCodeToEmail,
    SendConfirmationEmail,
)
from liberty_arrow.domain.model import (
    ConfirmationEmailRateExceeded,
    ConfirmationLinkNotValid,
    EmailNotVerified,
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/block-screens/<block_screen_name>")
    def render_block_screen(block_screen_name):
        block_screens = {"default", "minimalist"}
        message = request.args.get("message", "You're not allowed to enter this site")
        if block_screen_name not in block_screens:
            block_screen_name = "default"
        return render_template(
            f"block-screens/{block_screen_name}.html", message=message
        )

    @app.route("/email-code")
    def email_code():
        to_address = request.args.get("email")
        if not to_address:
            return {"error": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        try:
            result = bus.handle_message(SendCodeToEmail(to_address))
            response = Response(
                {"result": result[0]}, 201, {"Access-Control-Allow-Origin": "*"}
            )
            return response
        except EmailNotVerified:
            return {
                "error": "The given email has to be verified before being used."
            }, 403

    @app.route("/email-confirmation")
    def email_confirmation():
        to_address = request.args.get("email")
        if not to_address:
            return {"error": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        try:
            bus.handle_message(SendConfirmationEmail(to_address))
            return "OK", 201
        except ConfirmationEmailRateExceeded:
            return {
                "error": "Too many confirmation emails have been sent to this address. Try again later."
            }, 429

    @app.route("/confirm-email")
    def confirm_email():
        token = request.args.get("token")
        if not token:
            return {"error": "No token included"}, 400
        bus = bootstrap.bootstrap()
        try:
            bus.handle_message(ConfirmEmail(token))
            return "OK", 201
        except ConfirmationLinkNotValid:
            return {"error": "Confirmation token does not exist or has expired."}, 404

    return app
