#!/usr/bin/env python3

import re
import os
import io
import sys
import shlex
import runpy


# Variables

VARIABLES = {
    "WEB_ROOT": os.environ.get("WEB_ROOT", "/")
}


# Paths

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")
TOOLS_DIR = os.path.join(PROJECT_DIR, "tools")
SRC_DIR = os.path.join(PROJECT_DIR, "src")


# Source processing

TEMPLATE_REGEX = r"{{(.*?)}}"

def call_tool(args):
    tool_name = args[0]
    tool_path = os.path.join(TOOLS_DIR, tool_name+".py")

    out = io.StringIO()

    old_argv = sys.argv
    old_out = sys.stdout

    sys.argv = args
    sys.stdout = out

    try:
        runpy.run_path(tool_path, run_name="__main__")
    finally:
        out.flush()
        sys.argv = old_argv
        sys.stdout = old_out

    string = out.getvalue()
    return string

def expand(match):
    start, end = match.span()
    try:
        call = match.group()[2:][:-2]
    except IndexError:
        return call
   
    arguments = shlex.split(call)
    try:
        template_name = arguments.pop(0)
    except IndexError:
        return call

    content = match.string
    i = start-1
    indentation = ""
    try:
        while content[i] == " " or content[i] == "\t":
            indentation += content[i]
            i -= 1
    except IndexError:
        pass

    template_content = "\n"

    if template_name == "tool":
        template = call_tool(arguments)
    else:
        with open(os.path.join(TEMPLATES_DIR, template_name), "r") as t:
            template = t.read()

            i = 1
            for arg in arguments:
                template = template.replace(f"%{i}%", arg)
                i += 1

            for (key, value) in VARIABLES.items():
                template_content = template_content.replace(f"%{key}%", value)


    template = re.sub(TEMPLATE_REGEX, expand, template)
    for line in template.split("\n"):
        template_content += indentation + line + "\n"

    i = 1
    for arg in arguments:
        template_content = template_content.replace(f"%{i}%", arg)
        i += 1

    return template_content

def process(src_path):
    relative_path = os.path.relpath(src_path, SRC_DIR)
    output_path = os.path.join(PROJECT_DIR, relative_path)
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    print(f"Processing {relative_path}...")
    with open(src_path, "r") as f:
        content = f.read()
        content = re.sub(TEMPLATE_REGEX, expand, content)
    for (key, value) in VARIABLES.items():
        content = content.replace(f"%{key}%", value)
    with open(output_path, "w+") as f:
        f.write(content)

# Main

def main():
    for (root, dirs, files) in os.walk(SRC_DIR):
        for file in files:
            if file.startswith("."):
                continue
            path = os.path.join(root, file)
            process(path)


if __name__ == "__main__":
    main()
