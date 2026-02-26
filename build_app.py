import PyInstaller.__main__
import sys
import os

# Define the name of your final executable
APP_NAME = "SmartFactory_OS"

# Define your module paths
# We use ';' for Windows and ':' for Linux
sep = ';' if sys.platform == 'win32' else ':'

params = [
    'main_app.py',             # Your entry point
    '--name=%s' % APP_NAME,    # Final EXE name
    '--onefile',               # Bundle everything into one file
    '--windowed',              # No console window
    '--noconfirm',             # Overwrite existing build
    '--clean',                 # Clean cache before build
    
    # INCLUDE MODULES FOLDER
    f'--add-data=modules{sep}modules', 
    
    # INCLUDE DATABASE MANAGER
    f'--add-data=db_manager.py{sep}.',
    
    # HIDDEN IMPORTS (Forces PyInstaller to see your dynamic modules)
    '--hidden-import=modules.building',
    '--hidden-import=modules.curing',
    '--hidden-import=modules.qc',
    '--hidden-import=modules.despatch',
    '--hidden-import=modules.lab',
    '--hidden-import=modules.crm',
    '--hidden-import=modules.admin_dashboard',
    '--hidden-import=modules.global_dashboard',
    '--hidden-import=modules.production_log',
    '--hidden-import=reportlab',
    '--hidden-import=reportlab.pdfgen.canvas',
    '--hidden-import=reportlab.lib.pagesizes',
]

PyInstaller.__main__.run(params)