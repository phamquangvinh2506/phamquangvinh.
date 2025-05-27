from flask import Flask, render_template_string, request, send_file, redirect, flash, url_for
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib, os, webbrowser, threading

app = Flask(__name__)
app.secret_key = 'secretkey'
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def get_aes_cipher(key: str, mode=AES.MODE_ECB):
    hashed_key = hashlib.sha256(key.encode()).digest()[:16]  # AES-128 key
    return AES.new(hashed_key, mode)

def encrypt_file(data: bytes, key: str) -> bytes:
    cipher = get_aes_cipher(key)
    return cipher.encrypt(pad(data, AES.block_size))

def decrypt_file(data: bytes, key: str) -> bytes:
    cipher = get_aes_cipher(key)
    return unpad(cipher.decrypt(data), AES.block_size)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        key = request.form.get('key')
        action = request.form.get('action')

        if not file or file.filename == '':
            flash(('warning', 'Vui lòng chọn một file.'))
            return redirect(url_for('index'))

        if not key:
            flash(('warning', 'Vui lòng nhập khóa.'))
            return redirect(url_for('index'))

        data = file.read()

        try:
            if action == 'encrypt':
                result = encrypt_file(data, key)
                output_filename = 'encrypted_' + file.filename
            elif action == 'decrypt':
                result = decrypt_file(data, key)
                output_filename = 'decrypted_' + file.filename
            else:
                flash(('danger', 'Thao tác không hợp lệ.'))
                return redirect(url_for('index'))

            output_path = os.path.join(RESULT_FOLDER, output_filename)
            with open(output_path, 'wb') as f:
                f.write(result)

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            flash(('danger', f'Lỗi xử lý file: {str(e)}'))
            return redirect(url_for('index'))

    return render_template_string(HTML_TEMPLATE)

# Tự động mở trình duyệt khi chạy server
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run(debug=True)
