from flask_sqlalchemy import SQLAlchemy
import uuid
from flask_migrate import Migrate
import os

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


class BaseModel(db.Model):
    """Base Model class to add a id, created_at and updated_at field as common for all models.
    properties: id (uuid), created_at, updated_at (timestamp)
    """
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __str__(self):
        """print: {id}/created_date
        :return:
        """
        return '{}-{}'.format(self.id, self.created_at)


def init_app(app):
    migrate = Migrate()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_CONNECTION_STRING')
    db.init_app(app)
    migrate.init_app(app, db)
