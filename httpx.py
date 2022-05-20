from asyncio import futures
import requests
import argparse
import os
import sys
import urllib3
import concurrent.futures
from modules.database_connections import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="HTTP Live Analyzer.")

parser.add_argument("-l", "--list-path",
                    default="examples.txt",
                    # required=True,
                    help='Specify the subdomain list path.')

parser.add_argument("-t", "--threads",
                    default=5,
                    type=int,
                    help='Number of threads to send HTTP requests.')

parser.add_argument("-s", "--store",
                    default=False,
                    action="store_true",
                    help='Use this switch if you want to store data to database.')
options = parser.parse_args()


def return_list_subdomains(filepath):
    subdomain_list = set()

    if not os.path.exists(filepath):
        print("[-] Wrong file path provided.")
        sys.exit(-1)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as file_handle:
        for subdomain in file_handle.readlines():
            subdomain = subdomain.strip()
            subdomain = subdomain.replace("*.", "")
            subdomain_list.add(subdomain)
        file_handle.close()
    subdomain_list = list(subdomain_list)
    return subdomain_list


def check_live(subdomain):
    information_data = dict()

    try:
        response = requests.get(f'https://{subdomain}',
                                verify=False,
                                allow_redirects=True,
                                timeout=3)
        information_data["url"] = f'https://{subdomain}'
        information_data["live"] = 1
        information_data["status_code"] = response.status_code
        information_data["content_length"] = response.headers["content-length"]

    except:
        try:
            response = requests.get(
                f'http://{subdomain}', verify=False, allow_redirects=True, timeout=3)
            information_data["url"] = f'http://{subdomain}'
            information_data["live"] = 1
            information_data["status_code"] = response.status_code
            information_data["content_length"] = response.headers["content-length"]

        except:
            information_data["url"] = subdomain
            information_data["live"] = 0
            information_data["status_code"] = 0
            information_data["content_length"] = 0

    return information_data


subdomain_list = return_list_subdomains(options.list_path)
# subdomain_list = subdomain_list[:20]

subdomain_data = []
print(f"[+] Checking For Live Assets [{len(subdomain_list)}].")
thread_num = options.threads
while len(subdomain_list) > 0:
    print(f"[+] Checking Live With [{thread_num}] Threads. ({current_time()})")
    queue_subdomains = subdomain_list[:thread_num]
    del subdomain_list[:thread_num]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(check_live, subdomain)
                   for subdomain in queue_subdomains]
        result = [f.result() for f in futures]
    subdomain_data += result

if options.store:
    print("[+] Inserting Assets Into Database.")
    for subdomain in subdomain_data:
        insert_into_database(subdomain)

else:
    print("[+] Printing Live Assets.")
    for subdomain in subdomain_data:
        if subdomain["live"] == 1:
            print(subdomain["url"])
