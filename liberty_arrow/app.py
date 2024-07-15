from flask import Flask, render_template, request
from liberty_arrow import bootstrap
from liberty_arrow.domain.commands import (
    ConfirmEmail,
    SendCodeToEmail,
    SendConfirmationEmail,
)


def create_app():
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
            return {"message": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        result = bus.handle_message(SendCodeToEmail(to_address))
        return {"result": result[0]}, 201

    @app.route("/email-confirmation")
    def email_confirmation():
        to_address = request.args.get("email")
        if not to_address:
            return {"message": "No email address included"}, 400
        bus = bootstrap.bootstrap()
        bus.handle_message(SendConfirmationEmail(to_address))
        return "OK", 201

    @app.route("/confirm-email")
    def confirm_email():
        token = request.args.get("token")
        if not token:
            return {"message": "No token included"}, 400
        bus = bootstrap.bootstrap()
        bus.handle_message(ConfirmEmail(token))
        return "OK", 201

    return app
