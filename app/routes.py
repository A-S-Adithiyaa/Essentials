# from flask import Blueprint, request, render_template, send_file
# from datetime import datetime
# from werkzeug.utils import secure_filename
# import zipfile
# import shutil
# import tempfile
# import os, shutil, tempfile, zipfile
# from datetime import datetime
# from pathlib import Path
# import random, string

# main = Blueprint('main', __name__)
# BASE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
# os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)

# def generate_code(length=6):
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# @main.route('/', methods=['GET', 'POST'])
# def index():
#     message = ""
#     share_code = None

#     if request.method == 'POST':
#         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         upload_path = os.path.join(BASE_UPLOAD_FOLDER, timestamp)
#         os.makedirs(upload_path, exist_ok=True)

#         anything_uploaded = False

#         text = request.form.get('text')
#         if text and text.strip():
#             with open(os.path.join(upload_path, "message.txt"), "w", encoding="utf-8") as f:
#                 f.write(text.strip())
#             message += "Text saved successfully! "
#             anything_uploaded = True

#         uploaded_files = [
#             file for file in request.files.getlist('files')
#             if file and file.filename.strip()
#         ]
#         if uploaded_files:
#             for file in uploaded_files:
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(upload_path, filename))
#             message += f"{len(uploaded_files)} file(s) uploaded successfully!"
#             anything_uploaded = True

#         if anything_uploaded:
#             share_code = generate_code()
#             zip_path = os.path.join(BASE_UPLOAD_FOLDER, f"{share_code}.zip")
#             shutil.make_archive(zip_path.replace(".zip", ""), 'zip', upload_path)
#         else:
#             message = "⚠️ No text or valid files uploaded."

#     return render_template("index.html", message=message or None, share_code=share_code)

# @main.route('/retrieve', methods=['GET', 'POST'])
# def retrieve():
#     error = None
#     if request.method == 'POST':
#         code = request.form.get('code', '').strip().upper()
#         zip_path = os.path.join(BASE_UPLOAD_FOLDER, f"{code}.zip")
#         if os.path.exists(zip_path):
#             return send_file(zip_path, as_attachment=True)
#         else:
#             error = "❌ Invalid code. Please check and try again."

#     return render_template("retrieve.html", error=error)


# @main.route('/convert', methods=['GET', 'POST'])
# def convert_py_to_txt():
#     message = ""
#     if request.method == 'POST':
#         uploaded_files = request.files.getlist('uploads')
#         temp_input = tempfile.mkdtemp()
#         temp_output = tempfile.mkdtemp()

#         if len(uploaded_files) == 1 and uploaded_files[0].filename.endswith('.zip'):
#             # Handle ZIP upload
#             zip_path = os.path.join(temp_input, secure_filename(uploaded_files[0].filename))
#             uploaded_files[0].save(zip_path)

#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(temp_input)
#         else:
#             # Handle files/folders uploaded directly
#             for file in uploaded_files:
#                 rel_path = file.filename if hasattr(file, 'filename') else secure_filename(file.name)
#                 file_path = os.path.join(temp_input, rel_path)
#                 os.makedirs(os.path.dirname(file_path), exist_ok=True)
#                 file.save(file_path)

#         # Convert .py → .txt and copy other files
#         for root, _, files in os.walk(temp_input):
#             for fname in files:
#                 src = os.path.join(root, fname)
#                 rel = os.path.relpath(src, temp_input)
#                 dst = os.path.join(temp_output, rel)

#                 os.makedirs(os.path.dirname(dst), exist_ok=True)

#                 if fname.endswith('.py'):
#                     dst = dst.rsplit('.', 1)[0] + '.txt'
#                     with open(src, 'r', encoding='utf-8') as f_in, open(dst, 'w', encoding='utf-8') as f_out:
#                         f_out.write(f_in.read())
#                 else:
#                     shutil.copy2(src, dst)

#         zipname = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
#         zip_path = os.path.join(tempfile.gettempdir(), zipname)
#         shutil.make_archive(zip_path.replace(".zip", ""), 'zip', temp_output)

#         return send_file(zip_path, as_attachment=True)

#     return render_template("convert.html", message=message)


from flask import Blueprint, request, render_template, send_file
from datetime import datetime
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import os
import shutil
from io import BytesIO
import random
import string
import mysql.connector

main = Blueprint('main', __name__)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Ruby@56937",
        database="sample_db"

        # host=os.environ.get("DB_HOST"),
        # user=os.environ.get("DB_USER"),
        # password=os.environ.get("DB_PASSWORD"),
        # database=os.environ.get("DB_NAME")
    )

@main.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    share_code = None

    if request.method == 'POST':
        text = request.form.get('text')
        uploaded_files = [
            file for file in request.files.getlist('files')
            if file and file.filename.strip()
        ]

        anything_uploaded = bool(text and text.strip()) or bool(uploaded_files)

        if anything_uploaded:
            share_code = generate_code()
            conn = get_db_connection()
            cursor = conn.cursor()

            # Save text as a file
            if text and text.strip():
                cursor.execute("""
                    INSERT INTO uploads (share_code, filename, file_data, mimetype)
                    VALUES (%s, %s, %s, %s)
                """, (share_code, "message.txt", text.encode('utf-8'), "text/plain"))

            # Save uploaded files
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                file_data = file.read()
                mimetype = file.mimetype or "application/octet-stream"
                cursor.execute("""
                    INSERT INTO uploads (share_code, filename, file_data, mimetype)
                    VALUES (%s, %s, %s, %s)
                """, (share_code, filename, file_data, mimetype))

            conn.commit()
            cursor.close()
            conn.close()
            message = "Uploaded successfully!"
        else:
            message = "⚠️ No text or valid files uploaded."

    return render_template("index.html", message=message or None, share_code=share_code)

@main.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    error = None
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, file_data FROM uploads WHERE share_code = %s", (code,))
        files = cursor.fetchall()
        cursor.close()
        conn.close()

        if files:
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                for filename, file_data in files:
                    zf.writestr(filename, file_data)
            memory_file.seek(0)
            return send_file(memory_file, as_attachment=True, download_name=f"{code}.zip")
        else:
            error = "❌ Invalid code. Please check and try again."

    return render_template("retrieve.html", error=error)

@main.route('/convert', methods=['GET', 'POST'])
def convert_py_to_txt():
    message = ""
    if request.method == 'POST':
        uploaded_files = request.files.getlist('uploads')
        temp_input = tempfile.mkdtemp()
        temp_output = tempfile.mkdtemp()

        if len(uploaded_files) == 1 and uploaded_files[0].filename.endswith('.zip'):
            # Handle ZIP upload
            zip_path = os.path.join(temp_input, secure_filename(uploaded_files[0].filename))
            uploaded_files[0].save(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_input)
        else:
            # Handle files/folders uploaded directly
            for file in uploaded_files:
                rel_path = file.filename if hasattr(file, 'filename') else secure_filename(file.name)
                file_path = os.path.join(temp_input, rel_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)

        # Convert .py → .txt and copy other files
        for root, _, files in os.walk(temp_input):
            for fname in files:
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, temp_input)
                dst = os.path.join(temp_output, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)

                if fname.endswith('.py'):
                    dst = dst.rsplit('.', 1)[0] + '.txt'
                    with open(src, 'r', encoding='utf-8') as f_in, open(dst, 'w', encoding='utf-8') as f_out:
                        f_out.write(f_in.read())
                else:
                    shutil.copy2(src, dst)

        zipname = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(tempfile.gettempdir(), zipname)
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', temp_output)

        return send_file(zip_path, as_attachment=True)

    return render_template("convert.html", message=message)

@main.route('/chat')
def chat():
    return render_template('chatroom.html')
