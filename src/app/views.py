from app import app

@app.route('/')
def home():
   return "Hello World!"