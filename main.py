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


app.run(debug=True)
