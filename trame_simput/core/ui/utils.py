def extract_ui(yaml_content):
    ui_map = {}
    prop_indent = 10
    current_type = None
    current_list = []
    last_property = None
    for line in yaml_content.splitlines():
        stline = line.strip()
        sline = stline.split(":")[0]
        # Skip empty lines or comments
        if len(sline) == 0 or sline[0] == "#":
            # print(f"skip a: {sline}")
            continue

        indent = line.index(sline)
        if indent == 0:
            # Detect new object definition
            if current_type:
                # print(f"Add ui for {current_type}")
                current_list.insert(0, f'<ui id="{current_type}">')
                current_list.append("</ui>")
                ui_map[current_type] = "\n".join(current_list)
                current_list = []
            current_type = line.strip().split(":")[0]
        else:
            # Detect property
            if prop_indent > indent:
                prop_indent = indent

            # skip hidden prop
            if stline == "_ui: skip":
                last_property = None
                current_list.pop()
                continue

            # skip object prop
            if stline == "_ui: proxy":
                current_list.pop()
                continue

            if stline == "type: proxy" and last_property:
                current_list.append(f'  <proxy name="{last_property}" />')

            if indent > prop_indent or sline[0] == "_":
                continue

            current_list.append(f'  <input name="{sline}" />')
            last_property = sline

    # Always have a ui container
    # print(f"Add ui for {current_type}")
    current_list.insert(0, f'<ui id="{current_type}">')
    current_list.append("</ui>")
    ui_map[current_type] = "\n".join(current_list)

    return ui_map
