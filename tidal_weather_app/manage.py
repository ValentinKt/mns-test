from flask.cli import FlaskGroup
from app import app

cli = FlaskGroup(create_app=lambda: app)

if __name__ == '__main__':
    cli()
