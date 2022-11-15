# pyAviasalesFinder

## Требования
- Python 3.7 или старше
- Установленные библиотеки os, requests, json, re, datetime, configparser, wget. Установить недостающую библиотеку можно например так ``` pip install datetime ```

## Пример работы с классом

```
import aviasalesFinder

data_tickets = aviasalesFinder.FindMeTickets(origin="MOW", destination="LED", currency="rub", period_type="month", direct="true", limit=10)
tickets = data_tickets.get_ticket_data()
print(tickets)
```

