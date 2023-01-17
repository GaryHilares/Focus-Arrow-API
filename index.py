from flask import Flask, render_template, request
from utils.email import Gmail
from utils.pin import generate_pin
from dotenv import load_dotenv
from os import environ

app = Flask(__name__)

@app.route('/block-screens/<block_screen_name>')
def render_block_screen(block_screen_name):
    block_screens = {
        "default",
        "minimalist"
    }
    message = request.args.get("message", "You're not allowed to enter this site")
    if block_screen_name not in block_screens:
        block_screen_name = "default"
    return render_template(f'block-screens/{block_screen_name}.html', message=message)

@app.route('/create-pin')
def create_pin():
    pin = generate_pin()
    to_address = request.args.get("email")
    if not to_address:
        return {"message": "No email address included"}, 400
    Gmail.send_email(environ["GMAIL_USERNAME"], environ["GMAIL_APP_PASSWORD"], to_address, "Liberty Arrow pin", pin)
    return pin

if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)