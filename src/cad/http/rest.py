from flask import Flask, request, send_from_directory
import os

app = Flask(__name__, static_url_path='')

@app.route('/html/<path:path>')
def send_js(path):

    print(path)
    print(os.path.exists("html/" + path))
    return send_from_directory('html', "./", filename="index.html")

if __name__ == "__main__":
    app.run()
