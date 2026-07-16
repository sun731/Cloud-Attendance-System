class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:nandu2255@attendance-db.c5o42uuse1jb.ap-south-1.rds.amazonaws.com/attendance_system"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = "attendance_secret_key"
