from sre_constants import OP_UNICODE_IGNORE
from flask import Flask
import os
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24) # For flash messages

web_dir = os.path.dirname(os.path.abspath(__file__))
secondhandcar_package_dir = os.path.dirname(web_dir)
src_dir = os.path.dirname(secondhandcar_package_dir)
project_root_dir = os.path.dirname(src_dir) # This should be second_hand_car_project
app.config['DATA_DIR'] = os.path.join(project_root_dir, 'data')
app.config['CSV_FILE'] = os.path.join(app.config['DATA_DIR'], 'car_dekho_details.csv')
app.config['DB_FILE'] = os.path.join(app.config['DATA_DIR'], 'secondhandcar.db')

#app.config['TEMPLATES_AUTO_RELOAD', OP_UNICODE_IGNORE] = True # Enable auto-reload for templates

# Configuration
# Correctly determine project_root and then data_dir
#project_root_dir = os.path.dirname(src_dir) # This should be second_hand_car_project
#DATA_DIR = os.path.join(project_root_dir, 'data')

#CSV_FILE = os.path.join(DATA_DIR, 'car_dekho_details.csv') # Original CSV for loading
#PANDAS_REPO_CSV_FILE = os.path.join(DATA_DIR, 'pandas_repo_cars.csv') # CSV for Pandas repo state
#DB_FILE = os.path.join(DATA_DIR, 'secondhandcar.db')

def create_app():
    # --- Start of sys.path modification for Flask context ---
    # Get the directory of the current package (web)
    # e.g., /path/to/second_hand_car_project/src/secondhandcar/web
    #web_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the 'secondhandcar' package directory
    # e.g., /path/to/second_hand_car_project/src/secondhandcar
    #secondhandcar_package_dir = os.path.dirname(web_dir)
    # Get the 'src' directory
    # e.g., /path/to/second_hand_car_project/src
    #src_dir = os.path.dirname(secondhandcar_package_dir)

    #if src_dir not in sys.path:
    #    sys.path.insert(0, src_dir)
    # --- End of sys.path modification ---

    #app = Flask(__name__)
    #app.secret_key = os.urandom(24) # For flash messages

#    Initialize services and repositories (or pass them to routes)
    # This is a simplified way; dependency injection frameworks are better for larger apps
    from secondhandcar.repositories import SQLiteVehicleRepository
    from secondhandcar.services import FinancialTransactionService # Import other services as needed

    # Configuration (can be moved to a config.py file later)
    #project_root_dir = os.path.dirname(os.path.dirname(src_dir)) # Up three levels from web dir
    #app.config['DATA_DIR'] = os.path.join(project_root_dir, 'data')
    #app.config['DB_FILE'] = os.path.join(app.config['DATA_DIR'], 'secondhandcar.db')
    #app.config['CSV_FILE'] = os.path.join(app.config['DATA_DIR'], 'car_dekho_details.csv')
    
    # Ensure data directory exists
    if not os.path.exists(app.config['DATA_DIR']):
        os.makedirs(app.config['DATA_DIR'])

    
    setattr(app, 'vehicle_repo', SQLiteVehicleRepository(app.config['DB_FILE']))
    if not getattr(app, 'vehicle_repo').get_all_vehicles():
        if os.path.exists(app.config['CSV_FILE']):
            print(f"Flask App: DB empty, loading from {app.config['CSV_FILE']}")
            vehicle_repo = getattr(app, 'vehicle_repo')
            vehicle_repo.load_from_csv(app.config['CSV_FILE'])
        else:
            print(f"Flask App: DB empty, and CSV {app.config['CSV_FILE']} not found.")
            
    setattr(app, 'financial_service', FinancialTransactionService(getattr(app, 'vehicle_repo')))
    # Add other services like InventoryManagementService, ReportingService if their functionality is exposed via web

    with app.app_context():
        from . import routes  # Import routes after app is created and configured
    
    return app
