import json
import os
import shlex
import subprocess
import sys
import time
from urllib.request import urlopen

delay_for_cloning = 3
gitlab_api_token = os.environ.get('GITLAB_API_TOKEN')
gitlab_instance_domain = os.environ.get('GITLAB_DOMAIN_NAME')
relocations = []


def local_path(url):
    parts = url.split('/')
    if not parts[-1].endswith(".git"):
        raise OSError("Cannot parse url: not .git %s" % url)
    parts[-1] = parts[-1][:-4]
    here_dir = parts[-1]
    for portion, part in enumerate(parts):
        if ':' in part and 'ssh' not in part:
            wanted_dir = '/'.join(parts[portion + 1:-1])
            return here_dir, wanted_dir

    raise OSError("Cannot parse url: no colon separator present: %s" % url)


def store_relocate(here_dir, wanted_dir):
    global relocations
    wanted_dir = os.path.join('RELOCATION', wanted_dir)
    relocations.append((here_dir, wanted_dir, os.path.join(wanted_dir, here_dir)))


def do_relocate():
    global relocations
    print(f"Waiting {delay_for_cloning} minutes for cloning to complete ...")
    time.sleep(delay_for_cloning * 60)
    print("Performing relocation ...")
    for present_dir, desired_dir, wanted_dir_full in relocations:
        print("Renaming %s to %s" % (present_dir, wanted_dir_full))
        try:
            if not os.path.isdir(desired_dir):
                os.makedirs(desired_dir)
            os.rename(present_dir, wanted_dir_full)
        except Exception as e:
            print("Error relocating: %s" % e)
            print("Manually perform this action:\n  os.rename(%s,%s)" % (present_dir, wanted_dir_full))

    relocations = []


def find_all_projects(api_token):
    """
    Find all projects within GitLab instance, iterating until the last page
    has been reached.
    """
    project_dict_omnibus = []
    page = 1
    while True:
        all_projects_json = urlopen(
            "https://" + gitlab_instance_domain + "/api/v4/projects?private_token=" + api_token +
            "&page=" + str(page) +
            "&per_page=100")
        project_dict = json.loads(all_projects_json.read().decode())
        project_dict_omnibus += project_dict
        if len(project_dict) < 100:
            print(f"Finished at page #{page}, returned {len(project_dict_omnibus)} records.")
            return project_dict_omnibus
        else:
            page += 1
            print(f"Continuing at page #{page}")


assert os.getenv('GITLAB_API_TOKEN') is not None, "GITLAB_API_TOKEN environment variable has not been set."
assert os.getenv('GITLAB_DOMAIN_NAME') is not None, "GITLAB_DOMAIN_NAME environment variable has not been set."

projects_dict = find_all_projects(gitlab_api_token)

errs = False
already_seen = set()
for project in projects_dict:
    """
    For each project use the SSH URL to clone the project locally, will move projects
    to desired location and attempt to rename projects if duplicate detected.
    """
    try:
        url = project['ssh_url_to_repo']
        if url is not None:
            print(url)
            here_dir, wanted_dir = local_path(url)
            if here_dir in already_seen:
                print("Duplicate name: %s" % here_dir)
                print("Attempting to rename, then we will continue")
                do_relocate()
                already_seen = set()
            already_seen.add(here_dir)
            command = shlex.split('git clone %s' % url)
            job = subprocess.check_call(command)
            store_relocate(here_dir, wanted_dir)
            time.sleep(3)

    except Exception as exception:
        errs = True
        print(f"Error on {url}, returned non-zero exit code: {exception.returncode}")

if errs:
    print("There were errors, view console for more details.")
    sys.exit(1)

"""Finally relocate directory"""
do_relocate()
