from flask import *

app = Flask(__name__)
from functions import *
import pymysql

connection = pymysql.connect(host='localhost', user='root',
                             password='', database='FleetDB')

import pymysql.cursors

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
                response = jsonify({'msg': 'Login Success', 'data': row})
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



@app.route('/change_password', methods=['POST'])
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
            hashed_password = row[6]
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
                        sql = "update users set password = %s where user_id = %s"
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




app.run(debug=True)