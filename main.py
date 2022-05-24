import requests
import os, sys, time
import os.path
import time as t
import threading
import urllib.request
import urllib.parse
import pickle
import re
import json
import random
from uuid import uuid4
from subprocess import call

CRED = '\033[91m'
CEND = '\033[0m'
CGREEN = '\33[92m'
BLACK   = '\033[30m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
BLUE    = '\033[34m'
MAGENTA = '\033[35m'
CYAN    = '\033[36m'
WHITE   = '\033[37m'
RESET   = '\033[39m'

# Checking if program is up-to-date
version = "2.0"
check = "2.0"
check = requests.get(url = "https://raw.githubusercontent.com/itsunderscores/Twitter-Username-Swapper/main/version.txt")
if(version in check.text):
    pass
else:
    print("This version is currently out of date and is recommended you download the updated one.")
    print("https://github.com/itsunderscores/Twitter-Autoclaimer-Swapper")
    print(check)
    exit()

def header():
    os.system("cls")
    print(f"[{CRED}+{WHITE}] Twitter Swapper v%s" % version)
    print(f"[{CRED}-{WHITE}] Developed by underscores#0001")
    print(f"-------------------------------------------------------")


def unescape(in_str):
    in_str = in_str.encode('unicode-escape')   # bytes with all chars escaped (the original escapes have the backslash escaped)
    in_str = in_str.replace(b'\\\\u', b'\\u')  # unescape the \
    in_str = in_str.decode('unicode-escape')   # unescape unicode
    return in_str

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Check if string is blank
def is_not_blank(s):
    return bool(s and not s.isspace())

# Log to textfile
def logtofile(file, text):
	f = open(file, "w")
	f.write(str(text)+"\n") 
	f.close()
	return text

# Grab random proxy from file
def getproxy(file):
    proxy = random.choice(list(open(file)))
    proxy = proxy.strip()
    proxy = proxy.replace("\n", "")
    return proxy

# Grab random usernamer from file
def getusernamefromlist():
    username = random.choice(list(open("usernames.txt")))
    username = username.strip()
    username = username.replace("\n", "")
    return username
    

# Grab headers and compile to format
def headers(file):
    with open(file, 'r') as f:
        for line in f:
            if not find_between(line, "x-csrf-token: ", "\n"):
                pass
            else:
                csrf = find_between(line, "x-csrf-token: ", "\n")

            if not find_between(line, "Cookie: ", "\n"):
                pass
            else:
                cookie = find_between(line, "Cookie: ", "\n")

            if not find_between(line, "authorization: Bearer ", "\n"):
                pass
            else:
                auth = find_between(line, "authorization: Bearer ", "\n")

    getheaders={ 
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0", 
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
        "x-csrf-token": ""+csrf+"",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
        "x-twitter-active-user": "yes",
        "authorization": "Bearer " + auth + "",
        "Origin": "https://twitter.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://twitter.com/settings/screen_name",
        "Connection": "keep-alive",
        "Cookie": "" + cookie + "",
        "TE": "trailers"
    }

    return getheaders

claimed = []
failed = []
completed = []
released = []
swapped = []

# Check if username is valid
def check(username, file):
    url = "https://twitter.com/i/api/i/users/username_available.json?full_name=" + username + "&suggest=true&username=" + username
    getheaders = headers(file)
    attempts = 0

    while True:
        try:
            if attempts >= 5:
                return
            response = requests.get(url=url, headers=getheaders, timeout=5)
            if not response.text:
                randomnumber = random.randint(10,120)
                print(f"[{CRED}>{WHITE}] Could not grab information from website, rate limited, waiting %s seconds: %s" % (str(randomnumber), username))
                time.sleep(randomnumber)
                #time.sleep(1)
                attempts += 1
            else:
                try:
                    data = json.loads(str(response.text))
                    if data["reason"] == "taken":
                        return "N"
                    elif data["reason"] == "available":
                        return "Y"
                except:
                    return "S"
        except requests.ConnectionError:
            print(RED + "[>] Connection timed out. Most likley rate limited, sleeping for 2 minutes.")
            time.sleep(120)

# Grabs current username from header
def verifyaccount(file):
    url = "https://twitter.com/i/api/1.1/account/settings.json?include_mention_filter=true&include_nsfw_user_flag=true&include_nsfw_admin_flag=true&include_ranked_timeline=true&include_alt_text_compose=true&ext=ssoConnections&include_country_code=true&include_ext_dm_nsfw_media_filter=true&include_ext_sharing_audiospaces_listening_data_with_followers=true"
    getheaders = headers(file)
    try:
        response = requests.get(url=url, headers=getheaders, timeout=5)
        try:
            data = json.loads(str(response.text))
            return data["screen_name"]
        except:
            print(f"[{CRED}>{WHITE}] Could not grab your account information. This could be because of rate limiting or bad headers.")
    except requests.ConnectionError:
        print(f"[{CRED}>{WHITE}] Could not make connection to Twitter. This could be because of rate limiting or bad headers.")

def swap(username, file, type):
    attempts = 1

    try:
        if claimed[0] == "1":
            print(f"[{GREEN}>{WHITE}] Closed because we successfully claimed.")
            exit()
        else:
            pass
    except:
        pass

    if type == "1":
        print(f"[{GREEN}+{WHITE}] Releasing username...")
        time.sleep(2)
    elif type == "2":
        print(f"[{GREEN}+{WHITE}] [{GREEN}Thread Opened{WHITE}] Claiming %s" % username)

    url = "https://twitter.com/i/api/1.1/account/settings.json"
    getheaders = headers(file)
    data1 = "screen_name=" + username

    while True:
        if attempts >= 10:
            print(f"[{CRED}!{WHITE}] {CRED}ERROR:{WHITE} Cancelled due to too many requests failing.")
            failed.append("true")
            break
            return

        try:
            response = requests.post(url=url, data=data1, headers=getheaders, timeout=5)
            if response.status_code == 429:
                print(f"[{CRED}!{WHITE}] {CRED}ERROR:{WHITE} Rate limited by Twitter, response code 429")
                attempts += 1
            elif not response.text:
                time.sleep(1)
                attempts += 1
            else:

                try:
                    if "has already been taken for Screen name." in response.text:
                        print(f"[{CRED}!{WHITE}] Username has not been dropped yet. Reattempting...")
                        attempts += 1
                except:
                    pass

                try:
                    data = json.loads(str(response.text))
                    if data["screen_name"] == username:
                        if type == "1":
                            print(f"[{GREEN}>{WHITE}] Successfully released username!")
                            released.append(time.time())
                            return
                        elif type == "2":
                            print(f"[{GREEN}>{WHITE}] Successfully claimed %s" % username)
                            claimed.append("1")
                            completed.append("true")
                            swapped.append(time.time())
                            break
                            return
                    else:
                        if type == "1":
                            print(f"[{CRED}>{WHITE}] Could not release username")
                            break
                            return
                        elif type == "2":
                            print(f"[{CRED}>{WHITE}] Could not claim %s" % username)
                            attempts += 1
                except:
                    if type == "1":
                        print(f"[{CRED}!{WHITE}] Unexpected Variable Releasing Username")
                        break
                        return
                    elif type == "2":
                        print(f"[{CRED}!{WHITE}] Unexpected Variable Claiming %s" % username)
                        attempts += 1

        except requests.ConnectionError:
            print(f"[{CRED}>{WHITE}] Connection timed out. Most likley rate limited.")
            attempts += 1


def swapper():
    response1 = verifyaccount("account1.txt")
    response2 = verifyaccount("account2.txt")

    if not response1:
        print(f"[{GREEN}>{WHITE}] {CRED}ERROR:{WHITE} Could not sign into {CYAN}%s{WHITE}." % (response1))
        exit()
    else:
        print(f"[{GREEN}>{WHITE}] Signed in, {CYAN}%s{WHITE} is going to be released." % response1)

    if not response2:
        print(f"[{GREEN}>{WHITE}] {CRED}ERROR:{WHITE} Could not sign into {CYAN}%s{WHITE}." % (response2))
        exit()
    else:
        print(f"[{GREEN}>{WHITE}] Signed in, {CYAN}%s{WHITE} is going to claim {CYAN}%s{WHITE}." % (response2, response1))

    while True:
        new_username = input(f"[{GREEN}>{WHITE}] Enter username to change %s to: " % response1)
        checkifavailable = check(new_username, "account1.txt")
        if checkifavailable == "Y":
            break
        else:
            print(f"[{GREEN}>{WHITE}] {CRED}ERROR:{WHITE} The username you want to change %s to is unavailable. Please chose another." % response1)


    question = input(f"[{GREEN}>{WHITE}] Confirm this swap? (Y/N): ")
    if question == "y" or question == "Y":
        print(f"-------------------------------------------------------")
        for x in range(int(1)):
            th = threading.Thread(target=swap, args=(new_username, "account1.txt", "1"))
            th.start()

        time.sleep(1)

        for x in range(int(4)):
            th = threading.Thread(target=swap, args=(response1, "account2.txt", "2"))
            th.start()

        # Monitor Status
        while True:
            try:
                if failed[0] == "true":
                    print(f"[{GREEN}>{WHITE}] The claim process failed, reverting back to original name.")
                    swap(response1, "account1.txt", "2")
                    break
                else:
                    pass
            except:
                pass

            try:
                if completed[0] == "true":
                    number1 = released[0]
                    number2 = swapped[0]
                    print(f"[{GREEN}!{WHITE}] Completed in {number2 - number1} seconds")
                    break
                else:
                    pass
            except:
                pass


    else:
        print(f"[{CRED}>{WHITE}] This swap has been cancelled." + WHITE)


def main():
    header()
    swapper()
main()
