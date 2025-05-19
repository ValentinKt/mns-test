from flask import current_app, render_template, request, redirect, url_for, flash, jsonify
from uuid import UUID, uuid4

# To access the app instance and its configured services/repositories
from flask import current_app as app

from secondhandcar.models import Car
from secondhandcar.utils.custom_exceptions import VehicleNotFoundError

# Helper to get the repository
def get_repo():
    return app.vehicle_repo

@app.route('/')
def index():
    return redirect(url_for('list_cars'))

@app.route('/cars')
def list_cars():
    try:
        cars = get_repo().get_all_vehicles()
        return render_template('cars_list.html', cars=cars)
    except Exception as e:
        flash(f"Error fetching cars: {str(e)}", 'danger')
        return render_template('cars_list.html', cars=[])

@app.route('/cars/new', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        try:
            new_car = Car(
                brand=request.form['brand'],
                model=request.form['model'],
                year=int(request.form['year']),
                price=float(request.form['price']),
                km_driven=int(request.form['km_driven']),
                fuel_type=request.form['fuel_type'],
                transmission=request.form['transmission'],
                owner_type=request.form['owner_type'],
                ecological_bonus_eligible= 'ecological_bonus_eligible' in request.form
            )
            get_repo().add_vehicle(new_car)
            flash('Car added successfully!', 'success')
            return redirect(url_for('list_cars'))
        except ValueError as ve: # Specific error for bad form data
            flash(f"Invalid data: {str(ve)}", 'danger')
        except Exception as e:
            flash(f"Error adding car: {str(e)}", 'danger')
    return render_template('car_form.html', car=None, action_url=url_for('add_car'), form_title="Add New Car")

@app.route('/cars/edit/<uuid:car_id>', methods=['GET', 'POST'])
def edit_car(car_id: UUID):
    repo = get_repo()
    car_to_edit = repo.get_vehicle_by_id(car_id)

    if not car_to_edit:
        flash('Car not found.', 'danger')
        return redirect(url_for('list_cars'))

    if request.method == 'POST':
        try:
            car_to_edit.brand = request.form['brand']
            car_to_edit.model = request.form['model']
            car_to_edit.year = int(request.form['year'])
            car_to_edit.price = float(request.form['price'])
            car_to_edit.km_driven = int(request.form['km_driven'])
            car_to_edit.fuel_type = request.form['fuel_type']
            car_to_edit.transmission = request.form['transmission']
            car_to_edit.owner_type = request.form['owner_type']
            car_to_edit.ecological_bonus_eligible = 'ecological_bonus_eligible' in request.form
            # Potentially update is_sold, is_available if forms for these exist
            
            repo.update_vehicle(car_to_edit)
            flash('Car updated successfully!', 'success')
            return redirect(url_for('list_cars'))
        except ValueError as ve:
            flash(f"Invalid data: {str(ve)}", 'danger')
        except Exception as e:
            flash(f"Error updating car: {str(e)}", 'danger')
    
    return render_template('car_form.html', car=car_to_edit, action_url=url_for('edit_car', car_id=car_id), form_title="Edit Car")

@app.route('/cars/delete/<uuid:car_id>', methods=['POST']) # Use POST for delete for safety
def delete_car(car_id: UUID):
    try:
        get_repo().delete_vehicle(car_id)
        flash('Car deleted successfully!', 'success')
    except VehicleNotFoundError:
        flash('Car not found for deletion.', 'warning')
    except Exception as e:
        flash(f"Error deleting car: {str(e)}", 'danger')
    return redirect(url_for('list_cars'))

@app.route('/cars/view/<uuid:car_id>')
def view_car(car_id: UUID):
    car = get_repo().get_vehicle_by_id(car_id)
    if not car:
        flash('Car not found.', 'danger')
        return redirect(url_for('list_cars'))
    return render_template('car_detail.html', car=car)


# --- API Endpoints ---
@app.route('/api/cars', methods=['GET'])
def api_get_cars():
    try:
        cars = get_repo().get_all_vehicles()
        # Convert Car objects to dictionaries for JSON serialization
        cars_data = [car_to_dict(car) for car in cars]
        return jsonify(cars_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cars/<uuid:car_id>', methods=['GET'])
def api_get_car(car_id: UUID):
    car = get_repo().get_vehicle_by_id(car_id)
    if car:
        return jsonify(car_to_dict(car))
    return jsonify({"error": "Car not found"}), 404

@app.route('/api/cars', methods=['POST'])
def api_add_car():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    try:
        new_car = Car(
            brand=data['brand'], model=data['model'], year=int(data['year']),
            price=float(data['price']), km_driven=int(data['km_driven']),
            fuel_type=data['fuel_type'], transmission=data['transmission'],
            owner_type=data['owner_type'],
            ecological_bonus_eligible=data.get('ecological_bonus_eligible', False)
        )
        get_repo().add_vehicle(new_car)
        return jsonify(car_to_dict(new_car)), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cars/<uuid:car_id>', methods=['PUT'])
def api_update_car(car_id: UUID):
    repo = get_repo()
    car_to_update = repo.get_vehicle_by_id(car_id)
    if not car_to_update:
        return jsonify({"error": "Car not found"}), 404
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()

    try:
        car_to_update.brand = data.get('brand', car_to_update.brand)
        car_to_update.model = data.get('model', car_to_update.model)
        car_to_update.year = int(data.get('year', car_to_update.year))
        car_to_update.price = float(data.get('price', car_to_update.price))
        car_to_update.km_driven = int(data.get('km_driven', car_to_update.km_driven))
        car_to_update.fuel_type = data.get('fuel_type', car_to_update.fuel_type)
        car_to_update.transmission = data.get('transmission', car_to_update.transmission)
        car_to_update.owner_type = data.get('owner_type', car_to_update.owner_type)
        car_to_update.ecological_bonus_eligible = data.get('ecological_bonus_eligible', car_to_update.ecological_bonus_eligible)
        car_to_update.is_sold = data.get('is_sold', car_to_update.is_sold)
        car_to_update.is_available = data.get('is_available', car_to_update.is_available)
        
        repo.update_vehicle(car_to_update)
        return jsonify(car_to_dict(car_to_update))
    except ValueError as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cars/<uuid:car_id>', methods=['DELETE'])
def api_delete_car(car_id: UUID):
    try:
        get_repo().delete_vehicle(car_id)
        return jsonify({"message": "Car deleted successfully"}), 200
    except VehicleNotFoundError:
        return jsonify({"error": "Car not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def car_to_dict(car: Car) -> dict:
    """Helper function to convert Car object to dictionary for JSON."""
    return {
        "id": str(car.id),
        "brand": car.brand,
        "model": car.model,
        "year": car.year,
        "price": car.price,
        "km_driven": car.km_driven,
        "fuel_type": car.fuel_type,
        "transmission": car.transmission,
        "owner_type": car.owner_type,
        "ecological_bonus_eligible": car.ecological_bonus_eligible,
        "full_description": car.full_description,
        "is_sold": car.is_sold,
        "is_available": car.is_available
    }
