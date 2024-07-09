import os

PATH_ECODMS_EXPORT_FILE = os.getenv("PATH_ECODMS_EXPORT_FILE")


if __name__ == "__main__":
    print(f"Path to EcoDMS export file {PATH_ECODMS_EXPORT_FILE}")
