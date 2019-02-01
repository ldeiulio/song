from models import create_all
from create_app import app
import api

if __name__ == '__main__':
    create_all()
    app.run()
