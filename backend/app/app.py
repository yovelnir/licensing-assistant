import os
from dotenv import load_dotenv
from app import create_app

app = create_app()

def main() -> None:
    load_dotenv()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
