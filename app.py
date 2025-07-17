from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from models import db, Student
from config import Config
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)  # Optional: CORS(app, origins=["https://your-vercel-url.vercel.app"])

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/api/register-student", methods=["POST"])
def register_student():
    data = request.form
    file = request.files.get("student-photo")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
    else:
        return jsonify({"error": "Invalid or missing file"}), 400

    student = Student(
        registration_number=data.get("registration_number"),
        firstname=data.get("firstname"),
        middlename=data.get("middlename"),
        lastname=data.get("lastname"),
        date_of_birth=data.get("date-picker"),
        gender=data.get("gender"),
        nationality=data.get("nationality"),
        previous_school=data.get("previous-school"),
        admission_number=data.get("admission-number"),
        photo_filename=filename
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201

@app.route("/api/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([
        {
            "id": s.id,
            "registrationNumber": s.registration_number,
            "firstName": s.firstname,
            "middleName": s.middlename,
            "lastName": s.lastname,
            "admissionNumber": s.admission_number,
            "photo": s.photo_filename
        }
        for s in students
    ])

# Do NOT run debug mode in production
if __name__ == "__main__":
    app.run()
