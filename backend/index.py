from app import app
from utils.db import db
from models.contact import Users
import os, jwt, bcrypt, datetime

with app.app_context():
    db.create_all()
    if not Users.query.filter_by(username=os.environ['ADMIN_ACCOUNT']).first():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(os.environ['ADMIN_PASSWORD'].encode('utf-8'), salt)
        db.session.add(Users(username=os.environ['ADMIN_ACCOUNT'],
                               password=hashed_password.decode('utf-8'),))
    if not Users.query.filter_by(username="not user").first():
        db.session.add(Users(id=-1,username="not user",
                               password=1,))        
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=False, port=5000)
