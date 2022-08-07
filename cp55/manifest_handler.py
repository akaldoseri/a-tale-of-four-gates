from typing import List

import untangle

from cp55.manifest_elements import UsesPermission, ContentProvider, Service, BroadcastReceiver, Activity, \
    ManifestElement


class ManifestHandler:
    """
    Class responsible for parsing the AndroidManifest.xml file.
    The app properties are extracted in the constructor.
    """

    def __init__(self, manifest_path):
        manifest = untangle.parse(manifest_path).manifest

        try:
            self.__uses_permissions = list(map(lambda x: UsesPermission(x), manifest.uses_permission))
        except AttributeError:
            self.__uses_permissions = []

        try:
            self.__services = list(map(lambda x: Service(x), manifest.application.service))
        except AttributeError:
            self.__services = []

        try:
            self.__providers = list(map(lambda x: ContentProvider(x), manifest.application.provider))
        except AttributeError:
            self.__providers = []

        try:
            self.__receivers = list(map(lambda x: BroadcastReceiver(x), manifest.application.receiver))
        except AttributeError:
            self.__receivers = []

        try:
            self.__activities = list(map(lambda x: Activity(x), manifest.application.activity))
        except AttributeError:
            self.__activities = []

    def get_permissions(self) -> List[ManifestElement]:
        return self.__uses_permissions

    def get_activities(self) -> List[ManifestElement]:
        return self.__activities

    def get_providers(self) -> List[ManifestElement]:
        return self.__providers

    def get_services(self) -> List[ManifestElement]:
        return self.__services

    def get_receivers(self) -> List[ManifestElement]:
        return self.__receivers
