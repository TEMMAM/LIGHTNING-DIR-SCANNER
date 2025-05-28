What is this?
A blazing-fast Python script to scan websites for existing directories using multi-threading, smart soft-404 detection, user-agent randomization, and progress bar feedback.

Requirements:
----------------------------------------
-Python 3.6+
-requests library
-tqdm library
-beautifulsoup4 library (for HTML parsing)

Install dependencies via bash :
pip install requests tqdm beautifulsoup4

----------------------------------------

How to Use:
1.Prepare your wordlist (.txt) Save it as wordlist.txt (or any name)

2. Run the script
python3 D.py https://targetwebsite.com/ -w wordlist.txt -t 50 -o results.txt 
or:
python D.py https://targetwebsite.com/ -w wordlist.txt -t 50 -o results.txt

----------------------------------------
Arguments:

Argument	Description	Required/Optional	Default
url	Target base URL	Required	-
-w, --wordlist	Path to wordlist file	Required	-
-t, --threads	Number of concurrent threads	Optional	50
-o, --output	File to save found directories	Optional	(none)

----------------------------------------

What happens : 
The script fetches the homepage to detect soft 404 pages
Then scans all wordlist entries as potential directories, using multiple threads
Shows a progress bar and outputs found directories live
Saves results if -o is specified




