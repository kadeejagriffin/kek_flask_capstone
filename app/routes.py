from flask import jsonify, request
from app import app, db
from app.models import User
from app.auth import basic_auth, token_auth
from app.models import User, Retreat, Booking
from datetime import datetime
from flask_login import current_user




# USER ENDPOINTS
@app.route("/token")
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return {"token": token, 
            "tokenExpiration":user.token_expiration}
    
#Create New User
@app.route('/users', methods=['POST'])
def create_user():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    
    # Get the data from the request body
    data = request.json
    # Validate that the data has all of the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    # Get the values from the data
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Check to see if any current users already have that username and/or email
    check_users = db.session.execute(db.select(User).where((User.username==username)|(User.email==email))).scalars().all() 
    # If the list is not empty then someone alrady has that username or email
    if check_users:
        return {'error': ' A user with that username and/or email already exists'}, 400
    # Create a new user dict instance which will add it to the database
    new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
    return new_user.to_dict(), 201

    #update 
@app.route('/users/<int:user_id>', methods=['POST'])
@token_auth.login_required
def edit_user(user_id):
    #check if they sent the data correctly
    if not request.is_json:
        return {'error': 'Your content type must be application/json!'}, 400
    # get user based off id
    user = db.session.get(User, user_id)
    # make sure it exists
    if user is None:
        return {'error': f"user with {user_id} does not exist"}, 404
    # get their token 
    current_user = token_auth.current_user()
    # make sure they are the person logged in 
    if user is not current_user:
        return {'error': 'You cannot change this user as you are not them!'}, 403
    # then we update! 
    data = request.json
    user.update(**data)
    return user.to_dict()

# delete
@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    # get the user based on the id
    user = db.session.get(User, user_id)
    # get token
    current_user = token_auth.current_user()
    # make sure its a real user
    if user is None:
        return {'error': f"User with {user_id} not found!"}, 404
    # make sure user to delete is current user
    if user is not current_user:
        return {'error': 'You cant do that, delete yourself only'}, 403
    # delete user
    user.delete()
    return {'success': f"{user.username} has been deleted"}

# retrieve
@app.route("/users/<int:user_id>")
def get_user(user_id):
    #get the user
    user = db.session.get(User, user_id)
    #if no user let them know
    if user:
        return user.to_dict()
    else:
        return {'error': f"user with id:{user_id} not found"}, 404
    
    
    # RETREAT ENDPOINTS 
@app.route('/retreats', methods=['POST'])
def create_retreat():
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate that the data has all of the required fields
    required_fields = ['name', 'location', 'date', 'description', 'duration', 'cost']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    # Get the values from the data
    name = data.get('name')
    location = data.get('location')
    date = data.get('date')
    description = data.get('description')
    duration = data.get('duration')
    cost = data.get('cost')
    
    # Create a new retreat instance which will add it to the database
    new_retreat = Retreat(name=name, location=location, date=date, description=description, duration=duration, cost=cost)
    return new_retreat.to_dict(), 201

@app.route('/retreats/<int:retreat_id>', methods=['GET'])
def get_retreat_by_id(retreat_id):
    retreat = Retreat.query.get(retreat_id)

    if not retreat:
        return{'error':f"Retreat with ID {retreat_id} not found"}, 404

    return {
        'id': retreat.id,
        'name': retreat.name,
        'location': retreat.location,
        'date': retreat.date,  
        'description': retreat.description,
        'duration': retreat.duration,
        'cost': retreat.cost
    }

@app.route('/retreats', methods=['GET'])
def get_all_retreats():
    retreats = Retreat.query.all()
    return [{'id': retreat.id, 'name': retreat.name, 'location': retreat.location} for retreat in retreats]

#BOOKINGS
@app.route('/bookings', methods=['GET'])
@token_auth.login_required
def get_user_bookings():
    user_id = token_auth.current_user().id
    bookings = Booking.query.filter_by(user_id=user_id).all()
    bookings_data = [{'id': booking.id, 'retreat_id': booking.retreat_id} for booking in bookings]
    return {'bookings': bookings_data}

@app.route('/retreats/book/<int:retreat_id>', methods=['POST'])
@token_auth.login_required
def book_retreat(retreat_id):
    retreat = Retreat.query.get(retreat_id)
    if not retreat:
        return {'error': f'Retreat with ID {retreat_id} not found'}, 404
    # Check if the user has already booked the retreat
    existing_booking = Booking.query.filter_by(user_id=current_user.id, retreat_id=retreat.id).first()
    if existing_booking:
        return {'message': f'You have already booked the retreat: {retreat.name}'}

    new_booking = Booking(user_id=current_user.id, retreat_id=retreat.id)
    db.session.add(new_booking)
    db.session.commit()

    return {'message': f'You have booked the retreat: {retreat.name}'}

@app.route('/bookings/<int:booking_id>', methods=['DELETE'])
@token_auth.login_required
def delete_booking(booking_id):
    # Check if the booking exists
    booking = Booking.query.get(booking_id)
    if not booking:
        return {'error': f'Booking with ID {booking_id} not found'}, 404

    # Check if the current user is authorized to delete this booking
    if booking.user_id != token_auth.current_user().id:
        return {'error': 'You are not authorized to delete this booking'}, 403

    # Delete from the database
    db.session.delete(booking)
    db.session.commit()

    return {'message': 'Booking deleted successfully'}



    


