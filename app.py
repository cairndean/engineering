from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice

app = Flask(__name__)

# Configure the database URI: replace with your Render.com database path
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dino:dino@localhost:5432/engineering'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
  database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()



# Define the StorageSystem model
class StorageSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(50), nullable=False)
    capacity_used = db.Column(db.Float, nullable=False)
    error_status = db.Column(db.String(200), nullable=False)

    def __init__(self, company, capacity_used, error_status):
        self.company = company
        self.capacity_used = capacity_used
        self.error_status = error_status

# Create the database tables if they do not exist
with app.app_context():
    db.create_all()

# Endpoint to populate the database with random records
@app.route('/populate')
def populate_db():
    companies = ['Dell', 'IBM', 'NetApp']
    error_statuses = ['No errors', 'Overheating detected', 'Disk failure', 'Network issue']

    for _ in range(10):  # Adjust the range for the desired number of records
        company = choice(companies)
        capacity_used = round(randint(10, 90) + randint(0, 99) / 100.0, 2)  # Random capacity usage between 10.00 and 90.99
        error_status = choice(error_statuses) if randint(0, 9) > 1 else 'No errors'  # 80% chance of 'No errors'

        storage_system = StorageSystem(company, capacity_used, error_status)
        db.session.add(storage_system)
        db.session.commit()

    return jsonify({"message": "Database populated with random records."})

# Endpoint to display all database records
@app.route('/')
def index():
    storage_systems = StorageSystem.query.all()
    return render_template('index.html', storage_systems=storage_systems)

if __name__ == '__main__':
    app.run(debug=True)
