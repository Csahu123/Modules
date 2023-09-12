from flask import Flask, jsonify, request
from pymongo import  errors
import os
import hashlib
from bson import ObjectId
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

app.config["MONGO_URI"] = "mongodb://localhost:27017/Students"
mongo_S = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Quizes'
mongo_q = PyMongo(app)

UPLOAD_FOLDER = 'static'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}  # Allowed file extensions for images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Create unique indexes for user_id, personal_info.contact.phone, and personal_info.contact.email
mongo_S.db.student_profile.create_index([("user_id", 1)], unique=True)
mongo_S.db.student_profile.create_index([("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})
mongo_S.db.student_profile.create_index([("personal_info.contact.email", 1)], unique=True, partialFilterExpression={"personal_info.contact.email": {"$exists": True}})


# functions to support API's
def is_user_id_unique(user_id):
    # Query your database to check if the user_id already exists
    user = get_student(user_id)
    return user

def get_student(user_id):
    user = mongo_S.db.student_profile.find_one({'user_id': user_id})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to a string
    return jsonify(user)

def search_by_mobile_number():
    pass

def search_by_email():
    pass

def search_by_username_or_user_id():
    pass

def get_students():
    return list(mongo_S.db.student_profile.find())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(image):
    if image and allowed_file(image.filename):
        filename = f"{ObjectId()}.{image.filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Image uploaded successfully.", "filename": filename}), 200
    else:
        return jsonify({"message": "Invalid image or file format."}), 400


def hash_password(password):
    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password  


# Create student profile 
@app.route('/create_student_profile', methods=['POST'])
def create_student_profile():
    user_id = request.form.get('user_id', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    hashed_password = hash_password(password)
    user_class = request.form.get('user_class', '')
    # unknown_field = request.form.get('do not know yet')
    status_title = request.form.get('status_title', '')
    status_description = request.form.get('status_description', '')
    about = request.form.get('about', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    parents = request.form.get('parents', '')

    if not is_user_id_unique(user_id):
        return jsonify({'error': 'User ID already exists'}), 400
    
    user_image = ''
    if request.form.get('image',''):
        image = request.form.get('image','')
        user_image = upload_image(image)

    performance = {} 
    Attendance = {}
    Interest = {}
    parents = {}

    user_data = {
        "_id": str(ObjectId()),
        'user_id':user_id,
        'password': hashed_password,
        'username': username,
        'user_class': user_class,
        'user_image': user_image,
        'status_title': status_title,
        'status_description': status_description,
        'personal_info': {
            'about': about,
            'contact': {
                'phone': phone,
                'email': email,
                'address': address
            }
        },
        'performance': performance,
        'Attendance': Attendance,
        'Interest': Interest,
        'parents': parents
    }
    try:
        inserted_id = mongo_S.db.student_profile.insert_one(user_data).inserted_id
        inserted = mongo_S.db.student_profile.find_one({"_id": inserted_id})
        return jsonify({"_id": str(inserted["_id"])})
    except Exception as e:
        return jsonify({"error": "Error occurred while creating the class"}), 500

# Get student profile using user_id
@app.route('/get_user/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    return get_student(user_id)

# update user profiledata requires user_id which is Unique
@app.route('/update_student_profile/<string:user_id>', methods=['PUT'])
def update_student_profile(user_id):
    try:
        user_data = mongo_S.db.student_profile.find_one({'user_id': user_id})
        _id = user_data['_id']
        # Get user data from the request
        username = request.form.get('username', user_data['username'])
        password = request.form.get('password', user_data['password'])
        hashed_password = hash_password(password)
        user_id = request.form.get('user_id', user_data['user_id'])

        user_class = request.form.get('user_class', user_data['user_class'])
        status_title = request.form.get('status_title', user_data['status_title'])
        status_description = request.form.get('status_description', user_data['status_description'])
        about = request.form.get('about', user_data['personal_info']['about'])
        phone = request.form.get('phone', user_data['personal_info']['contact']['phone'])
        email = request.form.get('email', user_data['personal_info']['contact']['email'])
        address = request.form.get('address', user_data['personal_info']['contact']['address'])
        performance = request.form.get('performance', user_data['performance'])
        Interest = request.form.get('Interest', user_data['Interest'])
        Attendance = request.form.get('Attendance', user_data['Attendance'])
        parents = request.form.get('parents', user_data['parents'])

        # Optional: Handle the user image update
        user_image = ''
        if request.form.get('image', user_data['user_image']):
            image = request.form.get('image','')
            user_image = upload_image(image)

        user_data ={
                'user_id':user_id,
                'username': username,
                'password':hashed_password,
                'user_class': user_class,
                'user_image': user_image,
                'status_title': status_title,
                'status_description': status_description,
                'personal_info': {
                    'about': about,
                    'contact': {
                        'phone': phone,
                        'email': email,
                        'address': address
                    }
                },
                'performance': performance,
                'Attendance': Attendance,
                'Interest': Interest,
                'parents': parents
            }
        result = mongo_S.db.student_profile.update_one({"_id":_id},
                                                    {"$set": user_data})
        if result.modified_count == 0:
            return jsonify({"error": "student_profile not found"}), 404
        updated_entity = mongo_S.db.student_profile.find_one({"_id": _id})
        return jsonify(updated_entity), 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# search other user using phone, email, userid, username
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()

    if query:
        # Check if the query is a valid mobile number (all digits)
        if query.isdigit() and len(query) == 10:
            # Search for mobile number in all collections (student, parents, teacher)
            result = search_by_mobile_number(query)
        elif '@' in query:
            # Check if the query contains "@" (likely an email)
            # Search for email in all collections
            result = search_by_email(query)
        else:
            # Search for username or user ID in all collections
            result = search_by_username_or_user_id(query)
    return result


# setting status of quiz after click by user on quiz 
@app.route('/setting_status/<string:quiz_id>/<string:student_id>', methods = ['PUT'])
def setting_status_of_quizz(quiz_id, student_id):

    new_quiz = {
        "quiz_id": quiz_id,
        "status": "seen"
    }

    # Define the update operation to add the new quiz to the quiz_data array
    update = {
        '$push': {
            'quiz_data': {
                '$each': [new_quiz],
            }
        }
    }

    result = mongo_S.db.student_profile.update_one({'_id': student_id}, update)
    return "Quizz seen",200


#adding quizz in student profile
@app.route('/update_student_quiz_data/<string:quiz_id>/<string:student_id>/<string:result>/<string:click>', methods=['PUT'])
def update_student_quiz_data(quiz_id, student_id, result, click):
    try:
        # Find the student by student_id
        student = mongo_S.db.student_profile.find_one({"_id": student_id})
        print(student)
        if student:
            # Check if the quiz_id already exists in quiz_data
            quiz_entry = next((entry for entry in student['quiz_data'] if entry.get('quiz_id') == quiz_id), None)
            if quiz_entry:
                quiz = mongo_q.db.quizes.find_one({"_id": quiz_id})
                # Update the existing quiz entry
                quiz_entry['subject'] = quiz.get('subject', '')
                quiz_entry['topic'] = quiz.get('topic', '')
                quiz_entry['class'] = quiz.get('class', '')
                quiz_entry['subtopic'] = quiz.get('subtopic', '')
                quiz_entry['language'] = quiz.get('language', '')            
                quiz_entry['result'] = result
                quiz_entry['clicked_on'] = click

                # Update the student's document with the modified quiz_data
                mongo_S.db.student_profile.update_one({"_id": student_id}, {"$set": student})

                return jsonify({"message": "Student quiz data updated successfully."}), 200
            else:
                return jsonify({"message": "Quiz not found in student data."}), 404
        else:
            return jsonify({"message": "Student not found."}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500


# getting accuracy of student
@app.route('/getting_accuracy/<string:student_id>', methods=['GET'])
def getting_accuracy(student_id):
    try:
        student = mongo_S.db.student_profile.find_one({"_id": student_id})
        result = []
        for res in student.get("quiz_data", []):
            try:
                result.append(res['result'])
            except KeyError:
                # Key 'result' not found in this quiz data, continue to the next iteration
                continue
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)