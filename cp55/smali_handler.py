import re


def find_methods(methods_section):
    methods = {}
    method_signature = None
    method_lines = []

    for line in methods_section:
        if line.startswith(".method"):
            method_signature = line.replace(".method ", "")
            method_lines = []
        elif line.startswith(".end method"):
            methods[method_signature] = method_lines
        else:
            method_lines.append(line)

    return methods


def split_file_sections(smali_file):
    sections = {}

    section_title = "class definition"
    section_lines = []

    for line in smali_file:
        if line.startswith("#"):
            sections[section_title] = section_lines
            section_title = line.replace("# ", "")
            section_lines = []
        else:
            section_lines.append(line)

    sections[section_title] = section_lines

    return sections


def find_invoked_methods(code_snippet):
    invoked_methods = {}

    for line in code_snippet:
        if line.__contains__("invoke"):
            objects = re.findall("L.*?;", line)
            if len(objects) == 0:
                continue
            called_object = objects[0][1:-1].replace("/", ".")

            method = re.findall("->.*\\)", line)
            if len(method) != 1:
                continue
            method = method[0][2:].split("(")[0]

            invoked_method = invoked_methods.get(called_object)
            if invoked_method is None:
                methods = set()
                methods.add(method)
                invoked_methods[called_object] = methods
            else:
                invoked_method.add(method)

    return invoked_methods


def find_canonical_name(class_definition_section):
    for line in class_definition_section:
        if line.startswith(".class"):
            tokens = line.split(" ")
            for token in tokens:
                if token.startswith("L"):
                    token = token[1:]
                    canonical_name = token.replace(";", "").replace("/", ".")
                    return canonical_name
    return None


def find_method_name(method_signature):
    parts = method_signature.split(" ")
    for part in parts:
        if re.match(".*\\(.*\\).*", part):
            return part.split("(")[0]


class SmaliHandler:

    def __init__(self, smali_path):
        smali_file = open(smali_path, 'r')
        content = smali_file.readlines()
        smali_file.close()

        content = list(filter(lambda x: x != "",
                              map(lambda x: x.replace("\n", "").lstrip(" "),
                                  content)))

        file_sections = split_file_sections(content)

        self.canonical_name = find_canonical_name(file_sections["class definition"])

        self.methods = find_methods(file_sections.get("direct methods", {}))
        self.methods.update(find_methods(file_sections.get("virtual methods", {})))

        self.invoked_methods = {}
        for method_signature, code in self.methods.items():
            method_name = find_method_name(method_signature)
            self.invoked_methods[method_name] = find_invoked_methods(code)

    def get_invoked_methods(self):
        return self.invoked_methods

    def get_methods(self):
        return self.methods

    def get_method(self, method_name):
        """
        Returns the lines/content of the method given the method name

        :param method_name: can have the following form
                            "insert(Landroid/net/Uri;Landroid/content/ContentValues;)Landroid/net/Uri;"
        :return: the content of the method
        """
        for name, lines in self.methods.items():
            if method_name in name:
                return lines
        return None
