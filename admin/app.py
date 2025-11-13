from web import create_app

if __name__ == "__main__":
    app = create_app()
    import os

    for key, value in os.environ.items():
        print(f"{key} = {value}")
    app.run()
