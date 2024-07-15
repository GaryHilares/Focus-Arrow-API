from liberty_arrow.app import create_app
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(".env")
    app = create_app()
    app.run()
