# a-tale-of-four-gates
A Tale of Four Gates | Privilege Escalation and Permission Bypasses on Android through App Components

=======
### Overview
There are 2 executable scripts in the project:
* `python3 ./apk_analyser.py [app.apk]`:
  * works with either the apps listed in `package_names.json` or with local apks
  * with local apks, the path of the apk must be the first argument of the program
  * with `package_names.json`, the app are downloaded from the PlayStore by the script
  * stores analysis data in a MySQL database whose details are in the `database_interface.py` file 
    or prints them to the console if the password env variable is not set


* `python3 ./scraper.py`:
  * fetches app names from the PlayStore based on territory, category, and popularity

### Requirements
For the apk_analyser script, the system must have the following tools installed:
* Docker: https://docs.docker.com/desktop/
* apktool: https://github.com/skylot/jadx
* PlaystoreDownloader: https://github.com/ClaudiuGeorgiu/PlaystoreDownloader

For the scraper script, the system must have the following tools installed:
* MongoDB: https://www.mongodb.com/try/download/community

### How to run
For the apk analyser:
* Edit the filter.json file as desired
  * possible targets are "providers", "services", and "activities"
  * the format for object filters is the canonical name of the class e.g. "java.lang.StringBuilder"
  * the format for the method filter is canonical name:method name e.g. "java.lang.StringBuilder:append"
* Edit the package_names.json file with the apps you want to test
* Normally the script saves the results on a cloud hosted db with the user password taken as an env var
  * if env var is not set, then the output should be printed
