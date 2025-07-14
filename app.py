from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///note.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Note(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(200), nullable=False)
    Image = db.Column(db.String(200))  
    Date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()


@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image = request.files.get('image')

        note = Note(Title=title, Description=description  )

        if image and image.filename != '':
            filename = secure_filename(f"{datetime.now().timestamp()}_{image.filename}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            note.Image = filename

        db.session.add(note)
        db.session.commit()
        
    notes = Note.query.all()
    

    return render_template('index.html',notes=notes)


# @app.route('/note')
# def note_page():
#     notes = Note.query.all()
#     return render_template('notes.html', notes=notes)

@app.route("/update/<int:sno>", methods=['GET', 'POST'])
def update_note(sno):
    note = Note.query.filter_by(Sno=sno).first()

    if request.method == 'POST':
        note.Title = request.form.get('title')
        note.Description = request.form.get('description')
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(f"{datetime.now().timestamp()}_{image.filename}")
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            note.Image = filename

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('update.html', note=note)

@app.route('/delete/<int:sno>')
def delete(sno):
    note = Note.query.filter_by(Sno=sno).first()
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
