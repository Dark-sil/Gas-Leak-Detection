import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Define variables to store data
gasvalue = None
manualoverride = None
valvestatus = None

# Telegram Bot configuration
telegram_bot_token = '6543149823:AAHNchsL62Stg3ZGllj0T1Kd4uJ-u8ZbACo'
telegram_chat_id = '6319653242'
threshold = 750  # Set your threshold value here

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {'chat_id': telegram_chat_id, 'text': message}
    return requests.post(url, data=data).json()

def save_data_to_file(data, filename='data.json'):
    with open(filename, 'w') as file:
        json.dump(data, file)

def load_data_from_file(filename='data.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

class RequestHandler(BaseHTTPRequestHandler):
    data = {'gasvalue': gasvalue, 'manualoverride': manualoverride, 'valvestatus': valvestatus}
    save_data_to_file(data)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_string = parsed_url.query

        if query_string:
            query_dict = urllib.parse.parse_qs(query_string)
            data = load_data_from_file()

            if "gasvalue" in query_dict:
                gasvalue = query_dict["gasvalue"][0]
                data['gasvalue'] = gasvalue
                if float(gasvalue) > threshold:
                    send_telegram_message(f"Warning: Gas value is above the threshold! Current value: {gasvalue}")

            if "manualoverride" in query_dict:
                manualoverride = query_dict["manualoverride"][0]
                data['manualoverride'] = manualoverride

            if "valvestatus" in query_dict:
                valvestatus = query_dict["valvestatus"][0]
                data['valvestatus'] = valvestatus

            save_data_to_file(data)

            if "givedata" in query_dict and query_dict["givedata"][0] == 'true':
                response = f"gasvalue: {data['gasvalue']}, valvestatus: {data['valvestatus']}"
            elif "gasvalueread" in query_dict and query_dict["gasvalueread"][0] == 'true':
                response = f"{data['gasvalue']}"
            elif "manualoverrideread" in query_dict and query_dict["manualoverrideread"][0] == 'true':
                response = f"{data['manualoverride']}"
            elif "valvestatusread" in query_dict and query_dict["valvestatusread"][0] == 'true':
                response = f"{data['valvestatus']}"
            else:
                response = "Data received successfully!"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(response, "utf8"))

        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("No Data Received Yet!", "utf8"))

if __name__ == "__main__":
    PORT = 8000
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on port {PORT}")
    httpd.serve_forever()
