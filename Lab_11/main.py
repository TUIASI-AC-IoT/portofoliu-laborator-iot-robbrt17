# LABORATOR 11 - BALAN

from flask import Flask, jsonify, request, render_template_string
import os

app = Flask(__name__)

create_file_form = """
    <h1>Create a New File</h1>
    <form method="POST" action="/create_file">
        <label>Filename:</label><br>
        <input type="text" name="filename" required><br><br>
        <label>Content:</label><br>
        <textarea name="content" rows="10" cols="50"></textarea><br><br>
        <input type="submit" value="Create File">
    </form>
    {% if message %}
        <p><strong>{{ message }}</strong></p>
    {% endif %}
"""

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/dir_contents", methods=['GET'])
def get_contents():
    dir_list = os.listdir()
    print("Directory contents:")
    print(dir_list)
    return jsonify(dir_list)

@app.route("/file_contents/<filename>", methods=['GET'])
def file_contents(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content})
    else:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/create_file', methods=['GET'])
def show_form():
    return render_template_string(create_file_form)

@app.route("/create_file", methods=['POST'])
def create_file():
    filename = request.form.get('filename')
    content = request.form.get('content', '')

    if not filename:
        return render_template_string(create_file_form, message="Filename is required")
    
    with open(filename, 'w') as f:
        f.write(content)
    message = f"File {filename} created successfully"

    return render_template_string(create_file_form, message=message)

####
# Test with curl: curl -X DELETE http://127.0.0.1:5000/delete_file/filename
####
@app.route('/delete_file/<filename>', methods=['DELETE'])
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return jsonify({"message": f"File {filename} deleted successfully"})
    else:
        return jsonify({"error": "File not found"}), 404
    
####
# Test with curl: curl -X PUT http://127.0.0.1:5000/update_file/whatever.txt -H "Content-Type: application/json" -d "{\"content\": \"Text nou.\"}"
####    
@app.route('/update_file/<filename>', methods=['PUT'])
def update_file(filename):
    if os.path.exists(filename):
        data = request.get_json()
        content = data.get('content', '')

        with open(filename, 'w') as f:
            f.write(content)
        return jsonify({"message": f"File {filename} updated successfully"})
    else:
        return jsonify({"error": "File not found"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)