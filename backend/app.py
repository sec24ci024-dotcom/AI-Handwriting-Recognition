from flask import Flask, render_template, request
import mysql.connector
import os
import pytesseract
from PIL import Image

app = Flask(__name__)

# Tesseract Path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Upload Folder
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL Connection
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",
    database="handwriting_db"
)

cursor = db.cursor()

@app.route('/')
def home():
    return """
    <h1>AI Handwriting Recognition & Personalized Learning</h1>

    <a href='/teacher'>
        <button>Teacher Dashboard</button>
    </a>
    """

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']

        sql = "INSERT INTO students (name, email) VALUES (%s, %s)"
        values = (name, email)

        cursor.execute(sql, values)
        db.commit()

        return """
        <h2>Student Registered Successfully</h2>

        <a href='/teacher'>
            <button>Back to Dashboard</button>
        </a>
        """

    return render_template('register.html')

@app.route('/students')
def students():

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    return render_template(
        'students.html',
        students=data
    )

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':

        image = request.files['image']

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            image.filename
        )

        image.save(filepath)

        img = Image.open(filepath)

        extracted_text = pytesseract.image_to_string(
            img,
            config='--psm 6'
        )

        text_length = len(extracted_text.strip())

        if text_length > 30:
            quality = "Good"
            recommendation = "Excellent handwriting. Continue advanced writing exercises."

        elif text_length > 10:
            quality = "Average"
            recommendation = "Practice sentence writing and spacing."

        else:
            quality = "Poor"
            recommendation = "Practice alphabet writing for 15 minutes daily."

        # Save Report
        sql = """
        INSERT INTO reports
        (filename, recognized_text, quality, recommendation)
        VALUES (%s, %s, %s, %s)
        """

        values = (
            image.filename,
            extracted_text,
            quality,
            recommendation
        )

        cursor.execute(sql, values)
        db.commit()

        return f"""
        <h2>Image Uploaded Successfully</h2>

        <h3>Recognized Text:</h3>
        <pre>{extracted_text}</pre>

        <h3>Handwriting Quality: {quality}</h3>

        <h3>Recommendation:</h3>
        <p>{recommendation}</p>

        <br>

        <a href='/teacher'>
            <button>Back to Dashboard</button>
        </a>
        """

    return render_template('upload.html')

@app.route('/reports')
def reports():

    cursor.execute("SELECT * FROM reports")
    data = cursor.fetchall()

    return render_template(
        'reports.html',
        reports=data
    )

if __name__ == '__main__':
    app.run(debug=True)