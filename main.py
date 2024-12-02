import os
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
UPLOAD_FOLDER = './user_submissions'
INPUT_FOLDER = './input_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Save multiple input and output files
    input_files = request.files.getlist('input_files')
    output_files = request.files.getlist('output_files')

    # Save each input-output pair
    for i, (input_file, output_file) in enumerate(zip(input_files, output_files), start=1):
        input_file.save(os.path.join(INPUT_FOLDER, f'input{i}.txt'))
        output_file.save(os.path.join(INPUT_FOLDER, f'correct_output{i}.txt'))
    
    return "Files uploaded successfully!", 200

@app.route('/submit', methods=['POST'])
def submit_code():
    # Save the submitted code
    code_file = request.files['code']
    language = request.form['language']

    # Set the file extension based on the selected language
    if language == 'cpp':
        code_filename = 'submission.cpp'
        executable_filename = 'submission.exe'
    elif language == 'python':
        code_filename = 'submission.py'
        executable_filename = None  # No compilation for Python
    elif language == 'java':
        code_filename = 'submission.java'
        executable_filename = 'submission.class'  # Java class file after compilation

    code_path = os.path.join(UPLOAD_FOLDER, code_filename)
    code_file.save(code_path)

    # Paths for execution
    executable_path = os.path.join(UPLOAD_FOLDER, executable_filename) if executable_filename else None

    # Test against all input-output file pairs
    for i in range(1, len(os.listdir(INPUT_FOLDER)) // 2 + 1):  # Assuming input/output pairs are equal
        input_path = os.path.join(INPUT_FOLDER, f'input{i}.txt')
        correct_output_path = os.path.join(INPUT_FOLDER, f'correct_output{i}.txt')
        user_output_path = os.path.join(UPLOAD_FOLDER, f'user_output{i}.txt')

        try:
            with open(input_path, 'r') as infile, open(user_output_path, 'w') as outfile:
                if language == 'cpp':
                    compile_result = subprocess.run(['g++', code_path, '-o', executable_path],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if compile_result.returncode != 0:
                        return jsonify({"verdict": "Compilation Error", "details": compile_result.stderr.decode()}), 400
                    run_result = subprocess.run([executable_path], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, timeout=5)
                elif language == 'python':
                    run_result = subprocess.run(['python3', code_path], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, timeout=5)
                elif language == 'java':
                    compile_result = subprocess.run(['javac', code_path],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if compile_result.returncode != 0:
                        print(compile_result.stderr.decode())
                        return jsonify({"verdict": "Compilation Error", "details": compile_result.stderr.decode()}), 400
                    run_result = subprocess.run(['java', '-cp', UPLOAD_FOLDER, 'submission'], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, timeout=5)

                if run_result.returncode != 0:
                    print(run_result.stderr.decode())
                    return jsonify({"verdict": f"Runtime Error on input{i}.txt", "details": run_result.stderr.decode()}), 400

                # Compare user output with correct output
                with open(correct_output_path, 'r') as correct_output, open(user_output_path, 'r') as user_output:
                    user_op = user_output.read().strip()
                    correct_op = correct_output.read().strip()
                    print(user_op == correct_op)
                    if user_op != correct_op:
                        return jsonify({"verdict": f"Wrong Answer on input{i}.txt"}), 200

        except subprocess.TimeoutExpired:
            return jsonify({"verdict": f"Time Limit Exceeded on input{i}.txt"}), 400
        except Exception as e:
            return jsonify({"verdict": f"Error on input{i}.txt", "details": str(e)}), 400

    return jsonify({"verdict": "Accepted"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
