import glob
import os
import shutil
import subprocess


class ApkHandler:
    """
    Class responsible for interacting with the apk file and the its extracted resources.
    """

    def __init__(self, file_apk, output=None, no_resources=False, no_sources=False):
        self.__file_apk = file_apk
        self.__no_res = no_resources
        self.__no_src = no_sources
        if output is None:
            self.__output = "apk.out"
        else:
            self.__output = output
        self.__smali_paths = None
        self.__was_decoded = False

    def decode_apk(self):
        """
        Decodes the apk using apktool's decode function with the parameters passed in the constructor and returns
        the output of the command line process.
        TODO: throw error if extraction fails
        """
        command = "apktool decode"
        if self.__no_res:
            command = command + " --no-res"

        if self.__no_src:
            command = command + " --no-src"

        command = command + " --output " + self.__output
        command = command + " --force "
        command = command + " " + self.__file_apk

        self.__was_decoded = True
        apktool_output = subprocess.getoutput(command)

        return apktool_output

    def was_decoded(self):
        return self.__was_decoded

    def get_manifest_file_path(self):
        """
        Concatenates the output location with the manifest file default path.

        :return: The relative path of the manifest file.
        :raises: IOError If manifest file is not present at the location.
        """
        path = self.__output + "/AndroidManifest.xml"
        if os.path.isfile(path):
            return path
        else:
            raise IOError("Manifest file not found")

    def get_smali_file_path(self, canonical_name):
        if self.__smali_paths is None:
            self.__build_class_canonical_name_file_path_dict()
        return self.__smali_paths.get(canonical_name, None)

    def __build_class_canonical_name_file_path_dict(self):
        smali_paths = []

        top_level_directories = list(
            map(lambda x: self.__output + "/" + x,
                filter(lambda x: x.startswith("smali"),
                       os.listdir(self.__output))))

        for directory in top_level_directories:
            result = glob.glob(directory + '/**/*.smali', recursive=True)
            smali_paths.extend(result)

        name_path_dict = dict()
        for smali_path in smali_paths:
            parts = smali_path.split("/")
            del parts[0]
            del parts[0]
            canonical_name = ".".join(parts).replace(".smali", "")
            name_path_dict[canonical_name] = smali_path

        self.__smali_paths = name_path_dict

    def cleanup(self):
        """
        Deletes the resources created by the extract function.
        """
        shutil.rmtree(self.__output)
