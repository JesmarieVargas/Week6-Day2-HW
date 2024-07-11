from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connect_db, Error

app = Flask(__name__)
ma = Marshmallow(app)

# Create the member table schema, to define the structure of the data
class MemberSchema(ma.Schema):
    id = fields.Int(dump_only= True) # We do not have to input data for this field
    member_name = fields.String(required= True) # To be valid, this needs a value
    email = fields.String(required= True)
    phone = fields.String(required= True)
    
    class Meta:
        fields = ('member_name', 'email', 'phone')

member_schema = MemberSchema
members_schema = MemberSchema(many= True)

@app.route('/') # default landing page
def home():
    return "Hello, Flask!"

Reads all customer data via a GET request
@app.route("/members/<int:id>", methods = ['GET'])
def get_members(id):
    conn = connect_db()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary= True) # returns us a dictionary of table data instead of a tuple, our schema meta class with cross check the contents of the dictionaries that are returned

            # Write our query to GET all users
            query = "SELECT * FROM member;"

            cursor.execute(query, (id,))

            members = cursor.fetchall()

        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                return members_schema.jsonify(members)
            

# Create a new customer with a POST request
@app.route("/members", methods= ["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400
    
    conn = connect_db()
    if conn is not None:
        try:
           cursor = conn.cursor()
           
           # New member data
           new_member = (member_data["member_name"], member_data["email"], member_data["phone"])
           
           # query
           query = "INSERT INTO member (member_name, email, phone) VALUES (%s, %s, %s)"
           
           # Execute the query with new_customer data
           cursor.execute(query, new_member, (id,))
           conn.commit()
           
           return jsonify({'message': 'New member added successfully!'}), 200
        
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Databse connection failed"}), 500

@app.route("/members/<int:id>", methods= ["PUT"]) # dynamic route that will change based off of different query parameters
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connect_db()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM members WHERE id = %s"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Member was not found."}), 404
            
            # unpack customer info
            updated_member = (member_data['customer_name'], member_data['email'], member_data['phone'], id)

            query = "UPDATE member SET member_name = %s, email = %s, phone = %s WHERE id = %s"

            cursor.execute(query, updated_member)
            conn.commit()

            return jsonify({'message': f"Successfully updated member {id}"}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500


@app.route("/members/<int:id>", methods=['DELETE'])
def delete_member(id):
    
    conn = connect_db()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM member WHERE id = %s"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Member not found"})
            
            query = "DELETE FROM member WHERE id = %s"
            cursor.execute(query, (id,))
            conn.commit()

            return jsonify({"message": f"Member {id} was successfully deleted!"})
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500
    
    

if __name__ == "__main__":
    app.run(debug=True)