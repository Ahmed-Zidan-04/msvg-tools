1. Install Python: Ensure you have Python 3.6 or newer installed on the machine. You can download it from the official Python website.


2. Install Required Libraries: Open a terminal or command prompt and install the pywebview and PyInstaller libraries using pip:

pip install pywebview
pip install PyInstaller


3. Run the Script: You can run the script directly from the command line:

python viewer.py

Alternatively, you can create a standalone executable that doesn't require Python to be installed on the machine. Use PyInstaller to create this file from the terminal:

pyinstaller --onefile --noconsole --name "MSVG Viewer" viewer.py

This will create an executable file in a new dist folder.