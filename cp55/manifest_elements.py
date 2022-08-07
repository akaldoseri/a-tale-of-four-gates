from untangle import Element


def prepend_android(text):
    return "android:" + text


class ManifestElement:

    def __init__(self):
        self.name = ""
        self.permission = None
        self.foreground_service_type = None
        self.grant_uri_permission = None
        self.authorities = None
        self.read_permission = None
        self.write_permission = None
        self.enabled = True
        self.exported = False
        self.direct_boot_aware = False

    def set_defaults(self):
        if self.enabled is None or self.enabled == "true":
            self.enabled = True
        else:
            self.enabled = False

        if self.exported is None or self.exported == "false":
            self.exported = False
        else:
            self.exported = True

        if self.direct_boot_aware is None or self.direct_boot_aware == "false":
            self.direct_boot_aware = False
        else:
            self.direct_boot_aware = True

    def __str__(self):
        properties = list(filter(lambda x: x[1] is not None, vars(self).items()))
        return "{" + ','.join("\n    %s: %s" % item for item in properties) + "\n}"


class Activity(ManifestElement):

    def __init__(self, xml_element: Element):
        super().__init__()
        self.allow_embedded = xml_element.get_attribute(prepend_android("allowEmbedded"))
        self.allow_task_reparenting = xml_element.get_attribute(prepend_android("allowTaskReparenting"))
        self.always_retain_task_state = xml_element.get_attribute(prepend_android("alwaysRetainTaskState"))
        self.auto_remove_from_recents = xml_element.get_attribute(prepend_android("autoRemoveFromRecents"))
        self.banner = xml_element.get_attribute(prepend_android("banner"))
        self.clear_task_on_launch = xml_element.get_attribute(prepend_android("clearTaskOnLaunch"))
        self.color_mode = xml_element.get_attribute(prepend_android("colorMode"))
        self.config_changes = xml_element.get_attribute(prepend_android("configChanges"))
        self.direct_boot_aware = xml_element.get_attribute(prepend_android("directBootAware"))
        self.document_launch_mode = xml_element.get_attribute(prepend_android("documentLaunchMode"))
        self.enabled = xml_element.get_attribute(prepend_android("enabled"))
        self.exclude_from_recents = xml_element.get_attribute(prepend_android("excludeFromRecents"))
        self.exported = xml_element.get_attribute(prepend_android("exported"))
        self.finish_on_task_launch = xml_element.get_attribute(prepend_android("finishOnTaskLaunch"))
        self.hardware_accelerated = xml_element.get_attribute(prepend_android("hardwareAccelerated"))
        self.icon = xml_element.get_attribute(prepend_android("icon"))
        self.immersive = xml_element.get_attribute(prepend_android("immersive"))
        self.label = xml_element.get_attribute(prepend_android("label"))
        self.launch_mode = xml_element.get_attribute(prepend_android("launchMode"))
        self.lock_task_mode = xml_element.get_attribute(prepend_android("lockTaskMode"))
        self.max_recents = xml_element.get_attribute(prepend_android("maxRecents"))
        self.max_aspect_ratio = xml_element.get_attribute(prepend_android("maxAspectRatio"))
        self.multiprocess = xml_element.get_attribute(prepend_android("multiprocess"))
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.no_history = xml_element.get_attribute(prepend_android("noHistory"))
        self.parent_activity_name = xml_element.get_attribute(prepend_android("parentActivityName"))
        self.persistable_mode = xml_element.get_attribute(prepend_android("persistableMode"))
        self.permission = xml_element.get_attribute(prepend_android("permission"))
        self.process = xml_element.get_attribute(prepend_android("process"))
        self.relinquish_task_identity = xml_element.get_attribute(prepend_android("relinquishTaskIdentity"))
        self.resizeable_activity = xml_element.get_attribute(prepend_android("resizeableActivity"))
        self.screen_orientation = xml_element.get_attribute(prepend_android("screenOrientation"))
        self.show_for_all_users = xml_element.get_attribute(prepend_android("showForAllUsers"))
        self.state_not_needed = xml_element.get_attribute(prepend_android("stateNotNeeded"))
        self.supports_picture_in_picture = xml_element.get_attribute(prepend_android("supportsPictureInPicture"))
        self.task_affinity = xml_element.get_attribute(prepend_android("taskAffinity"))
        self.theme = xml_element.get_attribute(prepend_android("theme"))
        self.ui_options = xml_element.get_attribute(prepend_android("uiOptions"))
        self.window_soft_input_mode = xml_element.get_attribute(prepend_android("windowSoftInputMode"))

        self.set_defaults()


class BroadcastReceiver(ManifestElement):

    def __init__(self, xml_element: Element):
        super().__init__()

        self.direct_boot_aware = xml_element.get_attribute(prepend_android("directBootAware"))
        self.enabled = xml_element.get_attribute(prepend_android("enabled"))
        self.exported = xml_element.get_attribute(prepend_android("exported"))
        self.icon = xml_element.get_attribute(prepend_android("icon"))
        self.label = xml_element.get_attribute(prepend_android("label"))
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.permission = xml_element.get_attribute(prepend_android("permission"))
        self.process = xml_element.get_attribute(prepend_android("process"))

        self.set_defaults()


class ContentProvider(ManifestElement):

    def __init__(self, xml_element: Element):
        super().__init__()

        self.authorities = xml_element.get_attribute(prepend_android("authorities"))
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.grant_uri_permission = xml_element.get_attribute(prepend_android("grantUriPermission"))
        self.permission = xml_element.get_attribute(prepend_android("permission"))
        self.read_permission = xml_element.get_attribute(prepend_android("readPermission"))
        self.write_permission = xml_element.get_attribute(prepend_android("writePermission"))
        self.enabled = xml_element.get_attribute(prepend_android("enabled"))
        self.exported = xml_element.get_attribute(prepend_android("exported"))
        self.init_order = xml_element.get_attribute(prepend_android("initOrder"))
        self.multi_process = xml_element.get_attribute(prepend_android("multiProcess"))
        self.process = xml_element.get_attribute(prepend_android("process"))
        self.syncable = xml_element.get_attribute(prepend_android("syncable"))
        self.icon = xml_element.get_attribute(prepend_android("icon"))
        self.label = xml_element.get_attribute(prepend_android("label"))

        self.set_defaults()


class Service(ManifestElement):
    def __init__(self, xml_element: Element):
        super().__init__()

        self.description = xml_element.get_attribute(prepend_android("description"))
        self.direct_boot_aware = xml_element.get_attribute(prepend_android("directBootAware"))
        self.enabled = xml_element.get_attribute(prepend_android("enabled"))
        self.exported = xml_element.get_attribute(prepend_android("exported"))
        self.foreground_service_type = xml_element.get_attribute(prepend_android("foregroundServiceType"))
        self.icon = xml_element.get_attribute(prepend_android("icon"))
        self.isolated_process = xml_element.get_attribute(prepend_android("isolatedProcess"))
        self.label = xml_element.get_attribute(prepend_android("label"))
        self.name = xml_element.get_attribute(prepend_android("name"))
        self.permission = xml_element.get_attribute(prepend_android("permission"))
        self.process = xml_element.get_attribute(prepend_android("process"))

        self.set_defaults()


class UsesPermission(ManifestElement):
    def __init__(self, xml_element: Element):
        super().__init__()

        self.name = xml_element.get_attribute(prepend_android("name"))
        self.max_sdk_version = xml_element.get_attribute(prepend_android("maxSdkVersion"))
