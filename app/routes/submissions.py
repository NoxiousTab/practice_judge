from flask import Blueprint, request, jsonify, render_template, redirect, session, url_for
from flask_login import login_required
from app.models import User, Submission, db
from datetime import datetime
import os
import subprocess

submissions_bp = Blueprint('submissions', __name__)

UPLOAD_FOLDER = './user_submissions'
INPUT_FOLDER = './input_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(INPUT_FOLDER, exist_ok=True)

@submissions_bp.route('/')
def home():
    if 'user_id' in session:
        # Redirect to the dashboard if logged in
        return redirect(url_for('submissions.dashboard'))
    else:
        # Render the default index.html for non-logged-in users
        return render_template('home.html')
    #return render_template('index.html')

@submissions_bp.route('/upload', methods=['POST'])
def upload_files():
    # Save multiple input and output files
    print("hit")
    input_files = request.files.getlist('input_files')
    output_files = request.files.getlist('output_files')

    # Save each input-output pair
    for i, (input_file, output_file) in enumerate(zip(input_files, output_files), start=1):
        input_file.save(os.path.join(INPUT_FOLDER, f'input{i}.txt'))
        output_file.save(os.path.join(INPUT_FOLDER, f'correct_output{i}.txt'))

    return "Files uploaded successfully!", 200

@submissions_bp.route('/submit', methods=['POST'])
def submit_code():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access. Please log in."}), 403

    user_id = session['user_id']  # Get the logged-in user's ID
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

    executable_path = os.path.join(UPLOAD_FOLDER, executable_filename) if executable_filename else None

    verdict = "Accepted"
    total_test_cases = len(os.listdir(INPUT_FOLDER)) // 2
    passed_test_cases = 0

    for i in range(1, total_test_cases + 1):
        input_path = os.path.join(INPUT_FOLDER, f'input{i}.txt')
        correct_output_path = os.path.join(INPUT_FOLDER, f'correct_output{i}.txt')
        user_output_path = os.path.join(UPLOAD_FOLDER, f'user_output{i}.txt')

        try:
            print("hit")
            with open(input_path, 'r') as infile, open(user_output_path, 'w') as outfile:
                if language == 'cpp':
                    compile_result = subprocess.run(['g++', code_path, '-o', executable_path],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if compile_result.returncode != 0:
                        verdict = "Compilation Error"
                        break
                    run_result = subprocess.run([executable_path], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, timeout=5)
                elif language == 'python':
                    run_result = subprocess.run(['python3', code_path], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, timeout=5)
                elif language == 'java':
                    compile_result = subprocess.run(['javac', code_path],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if compile_result.returncode != 0:
                        verdict = "Compilation Error"
                        break
                    run_result = subprocess.run(['java', '-cp', UPLOAD_FOLDER, 'submission'], stdin=infile, stdout=outfile, stderr=subprocess.PIPE, timeout=5)

                if run_result.returncode != 0:
                    verdict = f"Runtime Error on input{i}.txt"
                    break

                with open(correct_output_path, 'r') as correct_output, open(user_output_path, 'r') as user_output:
                    user_op = user_output.read().strip()
                    correct_op = correct_output.read().strip()
                    if user_op != correct_op:
                        verdict = f"Wrong Answer on input{i}.txt"
                        break
                    else:
                        passed_test_cases += 1

        except subprocess.TimeoutExpired:
            verdict = f"Time Limit Exceeded on input{i}.txt"
            break
        except Exception as e:
            verdict = f"Error on input{i}.txt: {str(e)}"
            break

    # Save submission details to the database
    new_submission = Submission(
        user_id=user_id,
        title=f"Submission {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
        content=f"Code submitted in {language}",
        created_at=datetime.utcnow(),
        language=language,
        test_cases=total_test_cases,
        verdict=verdict
    )
    db.session.add(new_submission)
    db.session.commit()

    # Return the verdict
    return jsonify({
        "verdict": verdict,
        "passed": passed_test_cases,
        "total": total_test_cases
    }), 200



@submissions_bp.route('/dashboard')
def dashboard():
    # Ensure the user is logged in
    #print(user_id)
    if 'user_id' not in session:
        return redirect(url_for('submissions.home'))  # Redirect to home if not logged in
    # Fetch user data from the database using session['user_id']
    user_id = session['user_id']
    user = User.query.get(user_id)  # Replace with your user model
    print(user)
    # Example user-specific data
    submissions = Submission.query.filter_by(user_id=user_id).order_by(Submission.created_at.desc()).all()
    print(submissions)
    # Pass data to the dashboard template
    return render_template(
        'dashboard.html',
        username=user.username,  # Replace with your user attribute
        submissions=submissions
    )
@submissions_bp.route('/profile')
def profile():
    return render_template('profile.html')
