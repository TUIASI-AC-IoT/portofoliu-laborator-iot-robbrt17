import io
from flask import Flask, send_file
import os.path

app = Flask(__name__)

@app.route('/firmware.bin')
def firm():
    with open(".pio\\build\\esp-wrover-kit\\firmware.bin", 'rb') as bites:
        print(bites)
        return send_file(
                     io.BytesIO(bites.read()),
                     mimetype='application/octet-stream'
               )
    
@app.route('/version')
def version():
    # with open("include\\version.h", 'r', encoding='utf-8') as bytes:
    #     print(bytes)
    #     return send_file(
    #                  io.BytesIO(bytes.read()),
    #                  mimetype='application/octet-stream'
    #            )

    # version = open("include\\version.h", 'r', encoding='utf-8')
    # words_string = version.readlines()

    with open("versioning") as f:
        v = f.readline()
        print(v)
        return v

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(host='192.168.89.24', ssl_context=('ca_cert.pem', 'ca_key.pem'), debug=True)