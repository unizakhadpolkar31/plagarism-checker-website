from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure MongoDB URI and database name
app.config["MONGO_URI"] = os.getenv("MONGO_URI")  # Ensure this is correctly set in .env
app.config["MONGO_DBNAME"] = os.getenv("DB_NAME")  # Add this line to specify the database name

print(f"Connecting to MongoDB at {app.config['MONGO_URI']}")  # Debug print

# Initialize PyMongo
mongo = PyMongo(app)  # Initialize after the app configuration

# Configure allowed file upload path (make sure this folder exists)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Get form data and validate fields
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        hours = request.form.get('hours')
        pages = request.form.get('pages')
        education = request.form.get('education')

        if not all([username, email, mobile, hours, pages, education]):
            return jsonify({"success": False, "message": "All fields are required."}), 400
        
        # Convert hours and pages to integers
        hours = int(hours)
        pages = int(pages)

        # Handle PDF upload
        pdf_file = request.files.get('pdf')
        if pdf_file:
            # Ensure it's a valid file
            if not pdf_file.filename.endswith('.pdf'):
                return jsonify({"success": False, "message": "Only PDF files are allowed."}), 400

            filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(pdf_path)
        else:
            return jsonify({"success": False, "message": "PDF file is required."}), 400

        # Prepare submission data
        submission_data = {
            "username": username,
            "email": email,
            "mobile": mobile,
            "hours": hours,
            "pages": pages,
            "education": education,
            "pdf_path": pdf_path  # Save the file path to MongoDB
        }

        # Insert data into MongoDB
        result = mongo.db.submissions.insert_one(submission_data)

        return jsonify({"success": True, "message": "Data inserted successfully", "id": str(result.inserted_id)})

    except Exception as e:
        # Log the error and return failure message
        print(f"Error: {str(e)}")  # Log the error on the server console
        return jsonify({"success": False, "message": "An error occurred while processing the form.", "error": str(e)}), 500

@app.route('/history')
def history():
    try:
        submissions = list(mongo.db.submissions.find())  # Use mongo to access the collection
        print(f"Retrieved submissions: {submissions}")  # Log the retrieved submissions for debugging
        return render_template('history.html', submissions=submissions)
    except Exception as e:
        print(f"Error retrieving submissions: {str(e)}")  # Log the error on the server console
        return render_template('history.html', submissions=[])


if __name__ == '__main__':
    app.run(debug=True)
