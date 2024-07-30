import os
import sys
sys.path.insert(0, os.path.abspath('C:\Python Web\14_Testowanie_aplikacji_internetowych\homework\app'))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///contacts.db'
    JWT_SECRET_KEY = 'super-secret-key'
