import hashlib
import requests

stored = []
common_passwords = set()
with open("common_passwords.txt") as p:
    for line in p:
        common_passwords.add(line.strip().lower())

password = input("Enter Password: ")

if len(password) < 15:
    stored.append("Password is too short. Password must be at least 15 characters long.")
if len(password) >= 65:
    stored.append("Password is too long. Password must be at most 64 characters long.")
if password.lower() in common_passwords:
    stored.append("Password entered is a common password. Please try again.")

password_bytes = password.encode()
password_hash = (hashlib.sha1(password_bytes).hexdigest().upper())
prefix_hash = (password_hash[:5])
suffix_hash = (password_hash[5:])

breach_check_failed = False
pwned = 0

try:
    url = f"https://api.pwnedpasswords.com/range/{prefix_hash}" 
    response = requests.get(url, timeout=5)
    for line in response.text.splitlines():
        parts = line.split(":")
        if parts[0]  == suffix_hash:
            pwned = parts[1]
except requests.RequestException:
    breach_check_failed = True
    print("Unable to connect to the internet to check if " \
    "entered password has been breached. Recommendation is " \
    "to try again when there is internet access.")

if pwned != 0:
    stored.append(f"The entered password has been leaked {int(pwned):,} times. Please try again.")

if len(stored) == 0:
    print("PASS")
else:
    print("FAIL")
    for reason in stored:
        print(reason)


