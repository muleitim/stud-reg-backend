from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from models import db, Student
from config import Config
import os
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

cloudinary.config(
    cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
    api_key=app.config["CLOUDINARY_API_KEY"],
    api_secret=app.config["CLOUDINARY_API_SECRET"],
    secure=True
)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route("/api/register-student", methods=["POST"])
def register_student():
    data = request.form
    file = request.files.get("student-photo")

    registration_number = data.get("registration_number")
    if not registration_number:
        return jsonify({"error": "Missing registration number"}), 400

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    # Generate filename from registration number (slashes replaced)
    sanitized_reg_no = registration_number.replace("/", "_")
    file_ext = os.path.splitext(file.filename)[1]  # keep file extension
    filename = f"{sanitized_reg_no}{file_ext}"

    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(
        file,
        public_id=f"students/{sanitized_reg_no}",  # no extension
        overwrite=True,
        resource_type="image"
    )

    cloudinary_url = upload_result["secure_url"]
    print("\nCloudinary url:", cloudinary_url, "\n")

    # Save student record
    student = Student(
        registration_number=registration_number,
        firstname=data.get("firstname"),
        middlename=data.get("middlename"),
        lastname=data.get("lastname"),
        date_of_birth=data.get("date-picker"),
        gender=data.get("gender"),
        nationality=data.get("nationality"),
        previous_school=data.get("previous-school"),
        admission_number=data.get("admission-number"),
        photo_filename=cloudinary_url  # store the URL
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
            "photo": s.photo_filename  # Full Cloudinary URL
        }
        for s in students
    ])

if __name__ == "__main__":
    app.run()
