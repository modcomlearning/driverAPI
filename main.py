from flask import *

app = Flask(__name__)
from functions import *
import pymysql

connection = pymysql.connect(host='localhost', user='root',
                             password='', database='FleetDB')

import pymysql.cursors
import jwt
from datetime import datetime, timedelta
app.config['SECRET_KEY'] = "a3R_60uH#200y7nK"
@app.route('/login', methods=['POST'])
def login():
    try:
        json = request.json
        email = json['email']
        password = json['password']
        sql = "select * from drivers where email = %s"
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, email)
        if cursor.rowcount == 0:
            response = jsonify({'msg': 'Invalid Email'})
            response.status_code = 400
            return response
        else:
            row = cursor.fetchone()
            hashed_password = row['password']
            status = password_verify(password, hashed_password)
            if status:
                token = jwt.encode({
                    'public_id': row['driver_id'],
                    'exp': datetime.utcnow() + timedelta(minutes=1)
                }, app.config['SECRET_KEY'], algorithm = "HS256")

                response = jsonify({'msg': 'Login Success', 'data': row, 'token':token})
                response.status_code = 200
                return response
            else:
                response = jsonify({'msg': 'login failed'})
                response.status_code = 401
                return response
    except:
        response = jsonify({'msg': 'Something went wrong'})
        response.status_code = 500
        return response



# justpaste.it/572y9
# Decorators in python, they allow to add new functionalities to an existing function
from functools import wraps
def token_required(f):
     @wraps(f)
     def decorated(*args, **kwargs):
         token = None
         if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]  # Bearer JKHJKHJKHJK
         if not token:
             return {
             "message": "Authentication Token is missing!",
             "data": None,
             "error": "Unauthorized"
             }, 401
         try:
            data=jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
         except Exception as e:
             return {
             "message": "Something went wrong",
             "data": None,
             "error": str(e)
             }, 500

         return f(*args, **kwargs) # F should be True if Token Is Ok, else false

     return decorated  # This returns the inner function

@app.route('/change_password', methods=['POST'])
@token_required
def change_password():
            json = request.json
            driver_id = json['driver_id']
            current_password = json['current_password']
            new_password =json['new_password']
            confirm_password = json['confirm_password']

            sql = "select * from drivers where driver_id = %s"
            cursor = connection.cursor()
            cursor.execute(sql, (driver_id))
            # get row containing the current password from DB
            row = cursor.fetchone()
            hashed_password = row[11]
            status = password_verify(current_password, hashed_password)
            if status:
                print("Current is okay")
                response = passwordValidity(new_password)
                print("tttttttttt", response)
                if response == True:
                    print("New is okay")
                    if new_password != confirm_password:
                        response = jsonify({'msg': 'Password Do Not Match'})
                        response.status_code = 401
                        return response
                    else:
                        print("Confirm is okay")
                        sql = "update drivers set password = %s where driver_id = %s"
                        cursor = connection.cursor()
                        try:
                            cursor.execute(sql, (password_hash(new_password), driver_id))
                            connection.commit()
                            response = jsonify({'msg': 'password Changed'})
                            response.status_code = 200
                            return response
                        except:
                            connection.rollback()
                            response = jsonify({'msg': 'Password was Not Changed'})
                            response.status_code = 401
                            return response
                else:
                    response = jsonify({'msg': response})
                    response.status_code = 401
                    return response

            else:
                response = jsonify({'msg': 'Current Password is Wrong'})
                response.status_code = 401
                return response

#https://github.com/modcomlearning/driverAPI

def getmakes():
    sql = "select * from vehicle_make order by make_name asc"
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    makes = cursor.fetchall()
    return makes

@app.route('/allocatedvehicle', methods = ['POST'])
def allocatedvehicle():
    try:
        json = request.json
        driver_id = json['driver_id']
        sql = "select * from driver_allocations where driver_id = %s and allocation_status =%s"
        cursor = connection.cursor()
        cursor.execute(sql, (driver_id, 'active'))
        row = cursor.fetchone()
        reg_no = row[2] # pull out vehicle reg no

        # query again to find car details
        sql2 = "select * from vehicles where reg_no = %s"
        cursor2 = connection.cursor(pymysql.cursors.DictCursor)
        cursor2.execute(sql2, (reg_no))
        if cursor2.rowcount == 0:
            response = jsonify({'msg': 'Not found'})
            response.status_code = 404
            return response
        else:
           vehicle = cursor2.fetchone()
           makes = getmakes()
           response = jsonify({'msg':'Success', 'data': vehicle, 'makes': makes})
           response.status_code = 200
           return response

    except:
        response = jsonify({'msg': 'Sever error'})
        response.status_code = 500
        return response



# Get all assignments by driver_id
@app.route('/myassignments/<driver_id>', methods= ['GET'])
def myassignments(driver_id):
    try:
        sql2 = '''select * from vehicle_task_allocation where driver_id = %s order by
        reg_date DESC'''
        cursor2 = connection.cursor(pymysql.cursors.DictCursor)
        cursor2.execute(sql2, (driver_id))
        if cursor2.rowcount == 0:
            response = jsonify({'msg': 'Not Assignments'})
            response.status_code = 404
            return response
        else:
            assignments = cursor2.fetchall()
            print(assignments)
            response = jsonify({'msg': 'Success', 'data': assignments})
            response.status_code = 200
            return response
    except:
        response = jsonify({'msg': 'Server error'})
        response.status_code = 500
        return response


@app.route('/TripOngoing', methods = ['PUT'])
def TripOngoing():
    json = request.json
    task_id = json['task_id']
    sql = 'select * from vehicle_task_allocation where task_id = %s'
    cursor = connection.cursor()
    cursor.execute(sql, task_id)
    if cursor.rowcount == 0:
        response = jsonify({'msg': 'Not Such Task'})
        response.status_code = 404
        return response
    else:
        row = cursor.fetchone()
        status = row[7]
        if status == 'Pending':
            sqlUpdate = '''update vehicle_task_allocation set trip_complete_status = %s where task_id
            =%s'''
            cursor = connection.cursor()
            try:
                cursor.execute(sqlUpdate, ('Ongoing', task_id))
                connection.commit()
                response = jsonify({'msg': 'Ongoing'})
                response.status_code = 200
                return response
            except:
                connection.rollback()
                response = jsonify({'msg': 'Server Error'})
                response.status_code = 500
                return response
        else:
             response = jsonify({'msg': 'Cannot be Completed Status is {}'.format(status)})
             response.status_code = 417
             return response



@app.route('/TripCompleted', methods = ['PUT'])
def TripCompleted():
    json = request.json
    task_id = json['task_id']
    sql = 'select * from vehicle_task_allocation where task_id = %s'
    cursor = connection.cursor()
    cursor.execute(sql, task_id)
    if cursor.rowcount == 0:
        response = jsonify({'msg': 'Not Such Task'})
        response.status_code = 404
        return response
    else:
        row = cursor.fetchone()
        status = row[7]
        if status == 'Ongoing':
            sqlUpdate = '''update vehicle_task_allocation set trip_complete_status = %s where task_id
            =%s'''
            cursor = connection.cursor()
            try:
                cursor.execute(sqlUpdate, ('Completed', task_id))
                connection.commit()
                response = jsonify({'msg': 'Completed'})
                response.status_code = 200
                return response
            except:
                connection.rollback()
                response = jsonify({'msg': 'Server Error'})
                response.status_code = 500
                return response
        else:
             response = jsonify({'msg': 'Cannot be Started Status is {}'.format(status)})
             response.status_code = 417
             return response



@app.route('/TripDelete', methods = ['DELETE'])
def TripDelete():
    json = request.json
    task_id = json['task_id']
    sql = 'select * from vehicle_task_allocation where task_id = %s'
    cursor = connection.cursor()
    cursor.execute(sql, task_id)
    if cursor.rowcount == 0:
        response = jsonify({'msg': 'Not Such Task'})
        response.status_code = 404
        return response
    else:
        sql = "delete from vehicle_task_allocation where task_id = %s"
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (task_id))
            connection.commit()
            response = jsonify({'msg': 'Trip Deleted'})
            response.status_code = 200
            return response
        except:
            connection.rollback()
            response = jsonify({'msg': 'Server Error'})
            response.status_code = 500
            return response


# https://github.com/modcomlearning/driverAPI
# JWT Token
app.run(debug=True)
