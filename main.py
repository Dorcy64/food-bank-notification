import pandas
import requests
from bs4 import BeautifulSoup
import smtplib
import os

OCR_API_KEY = os.environ.get("OCR_API_KEY")
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
TO_ADDRESS = os.environ.get("TO_ADDRESS")



tafbg = requests.get(url="http://fetchrss.com/rss/604ade0edf15bf02551ff313604ade1ea4f7e53f98179592.xml").text
rss = BeautifulSoup(tafbg, "lxml")
media = rss.find_all("media:content")

words = []
for x in media[0:3]:
    image_text = x.get('url')
    parameters = {
        "apikey": OCR_API_KEY,
        "url": image_text,
    }
    new_text = requests.get(url="https://api.ocr.space/parse/imageurl", params=parameters)
    words.append(new_text.json())

formatted_text = []
for x in words:
    text = x["ParsedResults"][0]["ParsedText"]
    if len(text) > 60:
        formatted_text.append(text)

cities = pandas.read_csv("FoodBanks.csv")
names = cities.to_dict()
church_name = [names["LOCATIONS"][x] for x in names["LOCATIONS"]]

message_body = ""
for x in formatted_text:
    message_body += x

send_email = False

new_message = message_body.split("\n")

final_message = ""
for x in church_name:
    for y in new_message:
        if str(x) in y:
            send_email = True
            location = new_message.index(y)
            final_message += f"{new_message[location - 1]}\n"
            final_message += f"{new_message[location]}\n"

print(final_message)
if send_email:

    with smtplib.SMTP(host="smtp.mail.yahoo.com", port=587) as connect:
        connect.starttls()
        connect.login(user=EMAIL, password=PASSWORD)
        connect.sendmail(from_addr=EMAIL, to_addrs="hello@dorcis.com",
                         msg=f"Subject:The Package Arrived\n\n{final_message}")
        print("Sent Successfully")
else:
    print("No food opportunities today\nCheck for your self: https://www.facebook.com/tafoodbank")
