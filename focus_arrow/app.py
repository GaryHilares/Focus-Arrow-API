from flask import Flask, render_template, request
from focus_arrow import bootstrap
from focus_arrow.domain.commands import (
    VerifyEmail,
    SendTokenToEmail,
    SendVerificationEmail,
    CheckEmailConfirmed,
    SendUninstallationEmail,
)
from focus_arrow.domain.model import (
    ConfirmationEmailRateExceeded,
    ConfirmationLinkNotValid,
    EmailNotVerified,
)
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.route("/block-screens/<block_screen_name>")
    def render_block_screen(block_screen_name):
        block_screens = {"default", "minimalist"}
        message = request.args.get("message", "You're not allowed to enter this site")
        if block_screen_name not in block_screens:
            block_screen_name = "default"
        return render_template(
            f"block-screens/{block_screen_name}.html", message=message
        )

    @app.route("/send-token")
    def email_token():
        to_address = request.args.get("email")
        if not to_address:
            return {"error": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        try:
            result = bus.handle_message(SendTokenToEmail(to_address))
            return {"result": result}, 201, {"Access-Control-Allow-Origin": "*"}
        except EmailNotVerified:
            return {
                "error": "The given email has to be verified before being used."
            }, 403

    @app.route("/check-email")
    def check_email_confirmed():
        to_address = request.args.get("email")
        if not to_address:
            return {"error": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        result = bus.handle_message(CheckEmailConfirmed(to_address))
        return {"confirmed": result}, 200

    @app.route("/send-verification")
    def email_verification():
        to_address = request.args.get("email")
        if not to_address:
            return {"error": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        try:
            bus.handle_message(SendVerificationEmail(to_address))
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
            bus.handle_message(VerifyEmail(token))
            return "OK", 201
        except ConfirmationLinkNotValid:
            return {"error": "Confirmation token does not exist or has expired."}, 404

    @app.route("/uninstall")
    def uninstall():
        email = request.args.get("email")
        if email:
            try:
                bus = bootstrap.bootstrap()
                bus.handle_message(SendUninstallationEmail(email))
            except EmailNotVerified:
                return "Email is not verified", 403
        return "OK", 201

    return app
