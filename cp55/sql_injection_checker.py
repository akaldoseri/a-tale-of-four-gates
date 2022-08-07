import re

from cp55.apk_handler import ApkHandler
from cp55.smali_handler import SmaliHandler

sql_calls = {
    "android.database.sqlite.SQLiteDatabase:insert",
    "android.database.sqlite.SQLiteDatabase:insertOrThrow",
    "android.database.sqlite.SQLiteDatabase:insertWithOnConflict",
    "android.database.sqlite.SQLiteDatabase:delete",
    "android.database.sqlite.SQLiteDatabase:query",
    "android.database.sqlite.SQLiteDatabase:queryWithFactory",
    "android.database.sqlite.SQLiteDatabase:rawQuery",
    "android.database.sqlite.SQLiteDatabase:rawQueryWithFactory",
    "android.database.sqlite.SQLiteDatabase:update",
    "android.database.sqlite.SQLiteDatabase:updateWithOnConflict",
}


def is_sql_api_call(method_call):
    if method_call in sql_calls:
        return True
    return False


def split_sections(method):
    sections = {}

    if method is None:
        return sections

    current_section = list()
    current_section_name = "start"
    sections[current_section_name] = current_section
    previous_section_name = None

    in_pswitch_data = False
    for line in method:
        if line.startswith(":"):
            if not in_pswitch_data:
                sections[current_section_name] = current_section
                current_section = list()
                previous_section_name = current_section_name
                current_section_name = line
            else:
                current_section.append(line)

            if line.startswith(":goto") and (
                    previous_section_name.startswith(":pswitch") or previous_section_name.startswith(":sswitch")) \
                    and sections[previous_section_name][-1] == "nop":
                sections[previous_section_name][-1] = "goto " + current_section_name

        elif line.startswith("."):
            if line.startswith(".packed-switch"):
                in_pswitch_data = True
                current_section.append(line)
            elif line == ".end packed-switch":
                in_pswitch_data = False
                current_section.append(line)
            else:
                continue
        else:
            current_section.append(line)

    sections[current_section_name] = current_section

    sections = {key: value for (key, value) in sections.items()
                if not key.startswith(":try") and not key.startswith(":catch")}

    return sections


def build_execution_paths(method):
    sections = split_sections(method)

    if len(sections) == 0:
        return []

    visited_sections = set()
    visited_sections.add("start")

    execution_paths = list()
    execution_paths.append(sections["start"])

    old_visited_sections_number = -1
    while visited_sections != set(sections.keys()) and old_visited_sections_number != len(visited_sections):
        old_visited_sections_number = len(visited_sections)
        new_execution_paths = list()
        while len(execution_paths) > 0:
            path = execution_paths.pop(0)

            lines_in_section = len(path)
            new_path = list()
            for i in range(0, lines_in_section):
                line = path.pop(0)

                if line.startswith("if"):
                    # if-test vA, vB, +CCCC
                    # if-testz vAA, +BBBB

                    tokens = line.split()
                    if_cond = tokens[0]
                    first_register = tokens[1].replace(",", "")
                    dest_branch = tokens[-1]

                    if if_cond.endswith("z"):
                        second_register = str(0)
                    else:
                        second_register = tokens[2].replace(",", "")

                    true_path = list(new_path)
                    false_path = list(new_path)

                    if if_cond == "if-eq" or if_cond == "if-eqz":
                        true_path.append("c: " + first_register + " == " + second_register)
                        false_path.append("c: " + first_register + " != " + second_register)
                    elif if_cond == "if-ne" or if_cond == "if-nez":
                        true_path.append("c: " + first_register + " != " + second_register)
                        false_path.append("c: " + first_register + " == " + second_register)
                    elif if_cond == "if-lt" or if_cond == "if-ltz":
                        true_path.append("c: " + first_register + " < " + second_register)
                        false_path.append("c: " + first_register + " >= " + second_register)
                    elif if_cond == "if-ge" or if_cond == "if-gez":
                        true_path.append("c: " + first_register + " >= " + second_register)
                        false_path.append("c: " + first_register + " < " + second_register)
                    elif if_cond == "if-gt" or if_cond == "if-gtz":
                        true_path.append("c: " + first_register + " > " + second_register)
                        false_path.append("c: " + first_register + " <= " + second_register)
                    elif if_cond == "if-le" or if_cond == "if-lez":
                        true_path.append("c: " + first_register + " <= " + second_register)
                        false_path.append("c: " + first_register + " > " + second_register)

                    true_path.extend(sections[dest_branch])
                    false_path.extend(path)

                    new_execution_paths.append(true_path)
                    new_execution_paths.append(false_path)

                    visited_sections.add(dest_branch)
                    break

                elif line.startswith("goto"):
                    # goto +AA
                    # goto/16 +AAAA
                    # goto/32 +AAAAAAAA
                    target_branch = line.split()[-1]

                    new_path.extend(sections[target_branch])
                    new_execution_paths.append(new_path)

                    visited_sections.add(target_branch)

                elif line.startswith("sparse-switch"):
                    # sparse-switch vAA, +BBBBBBBB
                    sparse_switch_tokens = line.split()
                    register_to_test = sparse_switch_tokens[1].replace(",", "")
                    switch_table_offset = sparse_switch_tokens[-1]
                    switch_table_section = sections[switch_table_offset]

                    default_condition = []
                    for switch_table_entry in switch_table_section:
                        # 0x1 -> :sswitch_0
                        entry_tokens = switch_table_entry.split()
                        register_value = entry_tokens[0]
                        target_branch = entry_tokens[-1]
                        if target_branch in sections.keys():
                            default_condition.append("" + register_to_test + " != " + register_value)
                            switch_path = list(new_path)
                            switch_path.append("c: " + register_to_test + " == " + register_value)
                            switch_path.extend(sections[target_branch])
                            new_execution_paths.append(switch_path)
                            visited_sections.add(target_branch)

                    # the default path is taken when no switch condition is met
                    default_path = list(new_path)
                    default_path.append("c: " + " && ".join(default_condition))
                    default_path.extend(path)
                    new_execution_paths.append(default_path)

                    visited_sections.add(switch_table_offset)
                    break

                elif line.startswith("packed-switch"):
                    # packed-switch vAA, +BBBBBBBB
                    packed_switch_tokens = line.split()
                    register_to_test = packed_switch_tokens[1].replace(",", "")
                    switch_table_offset = packed_switch_tokens[-1]
                    switch_table_section = sections[switch_table_offset]

                    index = 0
                    first_case_value = None
                    for switch_table_entry in switch_table_section:
                        if switch_table_entry.startswith(".packed-switch"):
                            first_case_value = int(switch_table_entry.split()[1], 0)
                        elif switch_table_entry in sections.keys():
                            switch_path = list(new_path)
                            switch_path.append("c: " + register_to_test + " == " + str(index + first_case_value))
                            switch_path.extend(sections[switch_table_entry])
                            index = index + 1
                            new_execution_paths.append(switch_path)
                            visited_sections.add(switch_table_entry)

                    # the default path is taken when no switch condition is met
                    default_path = list(new_path)
                    default_path.append("c: " + register_to_test + " < " + str(first_case_value) + " && " +
                                        register_to_test + " >= " + str(index + first_case_value))
                    default_path.extend(path)
                    new_execution_paths.append(default_path)

                    visited_sections.add(switch_table_offset)
                    break
                else:
                    new_path.append(line)

            if len(new_path) == lines_in_section:
                new_execution_paths.append(new_path)

        execution_paths = new_execution_paths

    return execution_paths


class SqlInjectionChecker:

    def __init__(self, apk_handler: ApkHandler):
        self.apk_handler = apk_handler

    def check_method(self, method, tracked_variables):
        execution_paths = build_execution_paths(method)
        for path in execution_paths:
            is_terminal, variables_dict, secondary_conditions = self.check_execution_path(path, tracked_variables)
            if is_terminal:
                primary_conditions = 0
                for variable, conditions in variables_dict.items():
                    primary_conditions += len(conditions)

                if primary_conditions == 0 and len(secondary_conditions) == 0:
                    return False
        return True

    def check_execution_path(self, path, tracked_variables: set):
        variables_dict = dict()
        secondary_conditions = list()
        for variable in tracked_variables:
            variables_dict[variable] = list()

        store_move_result = False
        for line in path:
            tokens = line.split()
            if line.startswith("move"):
                instruction = tokens[0]

                if instruction.startswith("move-result") or instruction == "move-exception":
                    if store_move_result:
                        tracked_variables.add(tokens[1])
                        variables_dict[tokens[1]] = list()
                else:
                    dest_register = tokens[1].replace(",", "")
                    src_register = tokens[-1]

                    if src_register in tracked_variables:
                        tracked_variables.add(dest_register)
                        variables_dict[dest_register] = list()

            elif line.startswith("const"):
                dest_register = tokens[1].replace(",", "")
                if dest_register in tracked_variables:
                    tracked_variables.remove(dest_register)

            elif line.startswith("invoke"):
                invoke_args = re.findall("{.*}", line)[0][1:-1].replace(",", "").split()
                called_object = re.findall("L.*;->", line)[0][1:-3].replace("/", ".")
                called_method = re.findall("->.*\\(", line)[0][2:-1]
                method_signature = re.findall("->.*\\(.*", line)[0][2:]
                method_call = called_object + ":" + called_method

                if is_sql_api_call(method_call):
                    return True, variables_dict, secondary_conditions
                else:
                    argument_mapping = dict()
                    rec_tracked_vars = set()
                    for i in range(0, len(invoke_args)):
                        if invoke_args[i] in tracked_variables:
                            rec_var = "p" + str(i)
                            argument_mapping[rec_var] = invoke_args[i]
                            rec_tracked_vars.add(rec_var)
                    if len(tracked_variables) != 0:
                        store_move_result = True

                        smali_path = self.apk_handler.get_smali_file_path(called_object)
                        if smali_path is None:
                            continue
                        else:
                            smali_handler = SmaliHandler(smali_path)
                            method = smali_handler.get_method(method_signature)
                            execution_paths = build_execution_paths(method)
                            for path in execution_paths:
                                reached_terminal, rec_vars_dict, rec_sec_cond = self.check_execution_path(path,
                                                                                                          rec_tracked_vars)
                                if reached_terminal:
                                    secondary_conditions.extend(rec_sec_cond)
                                    for key, value in rec_vars_dict.items():
                                        if key in argument_mapping.keys():
                                            map(lambda x: x + " IN " + method_call, value)
                                            variables_dict[argument_mapping[key]].extend(value)

                                    return True, variables_dict, secondary_conditions

                    else:
                        store_move_result = False
                        continue

            elif tokens[0] == "c:":
                tokens_set = set(tokens)
                for variable in tracked_variables:
                    if variable in tokens_set:
                        variables_dict[variable].append(line)
                        secondary_conditions.append(line)

        return False, variables_dict, secondary_conditions
