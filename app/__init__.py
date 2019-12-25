from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager
from flask_ckeditor import CKEditor
#from flask_uploads import UploadSet, IMAGES, DOCUMENTS configure_uploads
from flask_uploads import UploadSet, IMAGES, DOCUMENTS, DEFAULTS, configure_uploads,patch_request_class

from flask_admin import Admin, BaseView, expose

#import logging

ckeditor = CKEditor()


app = Flask(__name__)
#app = Flask(__name__, static_url_path='/static')

#logging.basicConfig(level=logging.DEBUG)

app.config.from_object(Config)

ckeditor.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)

#uploadSet = UploadSet('files')
uploadSet = UploadSet('files', DEFAULTS)
configure_uploads(app, uploadSet)
#patch_request_class(app,size=None)
patch_request_class(app)

#admin = Admin(app)
admin = Admin(name="", template_mode="bootstrap3")
#admin = Admin(name="HKIST Admin Area", template_mode="bootstrap3", index_view="AdminModelView")
admin.init_app(app)


from app import routes, models
#from app import routes, models, admin_routes
