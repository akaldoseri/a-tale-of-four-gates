#!/usr/bin/env python3

import json
import os
import sys
from glob import glob

from cp55.apk_handler import ApkHandler
from cp55.component_inspector import ComponentInspector
from database_interface import DatabaseInterface

manifest_file_name = "/AndroidManifest.xml"
output_directory = "output/"
apk_file_extension = ".apk"


def download_apk(package_name):
    docker_command = "docker run \
    -u $(id -u):$(id -g) \
    -v \"${PWD}/credentials.json\":\"/app/credentials.json\" \
    -v \"${PWD}/\"" + output_directory + ":\"/app/Downloads/\" \
    -p 5000:5000 \
    --entrypoint=python3 \
    --rm downloader download.py -c /app/credentials.json \"" + package_name + "\""

    os.system(docker_command)

    downloaded_apk_file = glob(output_directory + "*" + package_name + apk_file_extension)[0]
    apk_file = output_directory + package_name + apk_file_extension

    os.rename(downloaded_apk_file, apk_file)


def process_apk(apk_path, input_package, inspection_filter, db):
    apk_handler = ApkHandler(apk_path)

    try:
        apk_handler.decode_apk()

        component_inspector = ComponentInspector(apk_handler, inspection_filter)
        background_results, analysis_status = component_inspector.inspect_background_components()

        app_id = db.insert_app(input_package, analysis_status)
        db.insert_components(app_id, background_results)

        if analysis_status == "full":
            os.remove(apk_path)
            print("Finished analyzing app " + input_package + " with status " + analysis_status +
                  ". Summary: " + str(len(background_results)) + " component(s).")

        elif analysis_status == "background":
            sql_results = component_inspector.inspect_providers_for_sql_injection()

            db.insert_sql_checks(app_id, sql_results)
            db.update_app_analysis_status(app_id, "full")

            print("Finished analyzing app " + input_package + " with status " + analysis_status +
                  ". Summary: " + str(len(background_results)) + " component(s). Also analyzed " +
                  str(len(sql_results)) + " methods for sql vulnerabilities.")

        apk_handler.cleanup()

    except Exception:
        apk_handler.cleanup()
        db.insert_app(input_package, "failed")
        print("Failed to inspect app " + input_package + " or to store the results in the database.")
        raise Exception


def main():
    db = DatabaseInterface()

    inspection_filter_file = open("filter.json", "r")
    inspection_filter = json.load(inspection_filter_file)

    if len(sys.argv) < 2:
        # Using the package_names.json file
        print("Working with the package_names.json file.")

        package_list_file = open("package_names.json", "r")
        packages = json.load(package_list_file)

        for input_package in packages:
            try:
                download_apk(input_package)
            except Exception:
                db.insert_app(input_package, "download_failed")
                print("Failed to download app " + input_package + ".")
                continue

            apk_path = output_directory + input_package + apk_file_extension

            try:
                process_apk(apk_path, input_package, inspection_filter, db)
            except Exception:
                os.remove(apk_path)
                continue
    else:
        # Using a local apk file
        print("Working with a local apk.")

        apk_path = sys.argv[1]

        if not os.path.exists(apk_path):
            print("The argument provided is not a valid file path.")
            exit(0)

        if not apk_path.endswith(".apk"):
            print("The argument provided does not have the '.apk' file extension.")
            exit(0)

        input_package = apk_path.split("/")[-1][:-4]

        process_apk(apk_path, input_package, inspection_filter, db)


if __name__ == "__main__":
    main()
