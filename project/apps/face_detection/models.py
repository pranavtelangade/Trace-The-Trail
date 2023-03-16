from project.core.models import BaseModel, db

class UserProfile(BaseModel):
    user_name = db.Column(db.String(255),nullable=False, unique=True)
    password = db.Column(db.String(255),nullable=False)
    
class PersonDetection(BaseModel):
    username = db.Column(db.String(255),nullable=False,)
    age = db.Column(db.String(255),nullable=False)
    gender = db.Column(db.String(255),nullable=False)
    identification = db.Column(db.String(255),nullable=True)
    