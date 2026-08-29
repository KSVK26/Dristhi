import os
script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch_swagger.py")
rc = os.system(f'"{os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", ".venv", "Scripts", "python.exe")}" "{script}"')
print("vendor_rc:", rc)