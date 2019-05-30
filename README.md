Python Mysql Example
--
Monkey patch example of how to use python and mysql through the QuotaGuard Static or QuotaGuard Shield proxy.

Tested to work with Python 3

## Usage
Install the pips in the requirements.txt file: `pip install -r requirements.txt`

Setup the environment variables QUOTAGUARDSTATIC_URL or QUOTAGUARDSHIELD_URL from the quotaguard dashboard. For example: http://username:password@hostname.quotaguard.com:9293

Setup your database connection environment variable DATABASE.  For example: mysql://username:password@database.hostname.com:3306/database-name

Run the application: `python app.py`
