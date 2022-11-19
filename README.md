# pyAviasalesFinder

## Requirements
- Python 3.7 or higher
- Installed libraries os, requests, json, re, datetime, configparser, wget. You can install the missing library like this: ``` pip install datetime ```

## Example working

```
import aviasalesFinder

data_tickets = aviasalesFinder.FindMeTickets(origin="MOW", destination="LED", currency="rub", period_type="month", direct="true", limit=10)
tickets = data_tickets.get_ticket_data()
for ticket in tickets:
    print(ticket)
```

## Extended example
### Get ticket data and send it to telegram in friendly format
```
from telebot import telebot
import aviasalesFinder
bot = telebot.TeleBot("your token API Telegram", parse_mode="HTML")

data_tickets = aviasalesFinder.FindMeTickets(origin="MOW", destination="LED", currency="rub", period_type="month", direct="true", limit=10)
message_list = []
tickets = data_tickets.get_ticket_data()
for ticket in tickets:
    message_list.append(ticket["origin_city"] + " - " + ticket["destination_city"] + " " + "<a href='" + ticket["link"] + "'>" + str(ticket["price"])+ "</a>" + ticket["currency"] + " " + "(" + ticket["departure_at_date"] + ")" + "\n")
messages = " ".join(message_list)

bot.send_message("@MySupport_Tickets_Group", messages)
```

