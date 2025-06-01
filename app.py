# app.py
from SSIS_Web import create_app
from dotenv import load_dotenv
from SSIS_Web.extensions import csrf  

load_dotenv('.env')

app = create_app()
csrf.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
