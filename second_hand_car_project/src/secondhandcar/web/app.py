# src/secondhandcar/web/app.py
import sys
import os

# --- Start of sys.path modification ---
# Get the directory of the current script (app.py)
# e.g., /path/to/second_hand_car_project/src/secondhandcar/web
app_script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the 'secondhandcar' package directory
secondhandcar_package_dir_from_app = os.path.dirname(app_script_dir)
# Get the 'src' directory
src_dir_from_app = os.path.dirname(secondhandcar_package_dir_from_app)

if src_dir_from_app not in sys.path:
    sys.path.insert(0, src_dir_from_app)
# --- End of sys.path modification ---

from secondhandcar.web import create_app # Now this import should work

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
