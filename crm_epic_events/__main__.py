from .config import init_sentry
from .main import Application


def main():
    """Main entry point of the app"""
    init_sentry()
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
