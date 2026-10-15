import sys
import os
from packaging.version import Version


PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
RELEASES_DIR = os.path.join(PROJECT_DIR, "src", "releases")


def get_releases_list():
    versions_list = os.listdir(RELEASES_DIR)
    versions_list = list(filter(lambda v: v.startswith("v") and v.endswith(".html"), versions_list))
    versions_list = list(map(lambda v: v.replace(".html", ""), versions_list))
    versions_list.sort(key=Version)
    versions_list.reverse()
    return versions_list


def releases_list():
    versions_list = get_releases_list()
    for version in versions_list:
        link = f"• <a href='{version}.html'>{version}</a>"
        print(f"<li class='release-link'>{link}</li>")


def releases_latest():
    latest = get_releases_list()[0]
    print(f"%WEB_ROOT%releases/{latest}.html", end="")


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        return

    if args[0] == "latest":
        releases_latest()
    elif args[0] == "list":
        releases_list()

if __name__ == "__main__":
    main()
