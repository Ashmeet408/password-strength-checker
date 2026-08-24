# Password Strength Checker

## What It Does

This code checks the strength of your password against a few checks being length, local blocklist, and a breach lookup.

## Why It's Built This Way

The code is formatted this way in reference to the NIST SP 800-63B Rev 4. This is the US National Institute of Standards and Technology. The checks of the code are if it is at least 15 characters long, at most 64 characters, and if it is a common password. The code also checks if your entered password has been pwned against the website Have I Been Pwned. There is also no restriction on uppercase/digit/symbol. The spec prohibits composition rules because it can lead to a password like "Password1!". Capitalizing the first letter is very common and so is using the exclamation point as the symbol.

## How The Breach Check Works

The breach check uses a technique called k-anonymity. The k is the crowd size and here k is approximately 800. This works by first producing a SHA-1 hash from your password and then splitting that key in 2 parts. The first part is the prefix which is the first 5 characters and the other part is the suffix which is the remaining characters. The prefix is then compared against the Have I Been Pwned(HIBP) website and the matching suffixes of every hash sharing that prefix are returned along with a breach count. The suffix never leaves your machine. If your entered password is breached, a message stating this password has been breached is printed, along with a number of how many times that password is breached. If there is no internet access a message is printed saying that you should try again when there is internet access as a recommendation.

## Installation

```
git clone https://github.com/Ashmeet408/password-strength-checker.git
pip install -r requirements.txt
```
## Usage

```
python checker.py
```

## Example Output

```
Enter Password: password
FAIL
Password is too short. Password must be at least 15 characters long.
The entered password has been leaked 52,372,427 times. Please try again.
Enter Password: k7#mQp2vLx9wZn4t
PASS
```

## What I Learned

I learned a lot with this being my first personal project. I learned the importance of a .gitignore file and to have files store information and to call that file instead hardcoding everything. This is done so the blocklist file can grow to 100,000 entries without touching a line of code. I learned to use a set over a list because the list has O(n) and a set is O(1) when it comes to a lookup. I learned how to turn an entered passcode into its SHA-1 and how to compare it with breached passwords without giving away said password. I learned how to access the internet within the code and also to make sure there is a check in case internet access is not available.