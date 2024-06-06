import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from random import randint, choice
from urllib.parse import quote as url_quote
from dotenv import load_dotenv

# Load environment variables from .env file, if it exists
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Read database URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")

    # Print the DATABASE_URL for debugging purposes
    print(f"DATABASE_URL: {database_url}")

    # Ensure the URL uses the 'postgresql' dialect
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Define the StorageSystem model within the application context
    with app.app_context():
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
        

    # Endpoint to delete all records from the database
    @app.route('/delete', methods=['DELETE'])
    def delete_all():
        try:
            num_deleted = db.session.query(StorageSystem).delete()
            db.session.commit()
            return jsonify({"message": f"Deleted {num_deleted} records."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500
        

    # Endpoint to provide data in JSON format
    @app.route('/data')
    def data():
        storage_systems = StorageSystem.query.all()
        storage_systems_list = [
            {
                "id": system.id,
                "company": system.company,
                "capacity_used": system.capacity_used,
                "error_status": system.error_status
            }
            for system in storage_systems
        ]
        return jsonify(storage_systems_list)

    
    # Endpoint to display all database records
    @app.route('/')
    def index():
        storage_systems = StorageSystem.query.all()
        return render_template('index.html', storage_systems=storage_systems)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
