stored = []
common_passwords = ["correcthorsebatterystaple", 
                    "123456789012345", 
                    "passwordpassword", 
                    "qwertyuiopasdfgh", 
                    "iloveyouiloveyou", 
                    "letmeinletmein12", 
                    "adminadminadmin1",
                    "password123"]

password = input("Enter Password: ")

if len(password) < 15:
    stored.append("Password is too short. Password must be at least 15 characters long.")
if len(password) >= 65:
    stored.append("Password is too long. Password must be at most 64 characters long.")
if password.lower() in common_passwords:
    stored.append("Password is a common password. Please try again.")

if len(stored) == 0:
    print("PASS")
else:
    print("FAIL")
    for reason in stored:
        print(reason)

