# SSIS_Web/extensions.py
from flask_wtf.csrf import CSRFProtect
from flask_mysql_connector import MySQL
from flask_bootstrap import Bootstrap

csrf = CSRFProtect()
mysql = MySQL()
bootstrap = Bootstrap()
