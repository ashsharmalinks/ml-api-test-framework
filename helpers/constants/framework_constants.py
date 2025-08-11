# helpers/constants/framework_constants.py
import os

class FrameworkConstants:
    root = os.path.abspath(os.getcwd())
    artifacts_dir = os.path.join(root, "artifacts")
    logs_dir = os.path.join(artifacts_dir, "logs")
    screenshots_dir = os.path.join(artifacts_dir, "screenshots")
    details_file = os.path.join(root, "details.ini")  # adjust if you keep it elsewhere
