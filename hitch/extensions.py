from flask_mailman import Mail
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy

mail = Mail()
db = SQLAlchemy()
security = Security()
