from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import csv
import re
import datetime
import math


def calulate_elo_winner(winner_rating, loser_rating):
    k_multiplier = 32
    e = 1 / (1 + math.pow(10, (loser_rating - winner_rating) / 400))
    return math.ceil(k_multiplier * (1 - e))


def update_elos(name1, name2, elo_dic):
    # If the names haven't popped up before set the values to 1000
    if name1 not in elo_dic:
        elo_dic[name1] = 1000
    if name2 not in elo_dic:
        elo_dic[name2] = 1000
    return elo_dic


def convert_date(date_str):
    # Convert dates to datetime format so that they can be compared
    date_str = date_str.replace("Date:", "")
    return datetime.datetime.strptime(date_str, "%B %d, %Y")


def pull_data(link):
    data = []
    req = requests.get(link)
    soup2 = BeautifulSoup(req.content, "html5lib")
    try:
        date = soup2.find(
            "i", class_="b-list__box-item-title", string=re.compile("Date")
        )
        date = convert_date(date.find_parent("li").get_text(strip=True))
    except Exception as e:
        print(e)

    for item in soup2.findAll(
        "tr",
        class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click",
    ):
        if item.find("i", class_="b-flag__text").text.strip() == "win":
            data.append(
                [
                    i.text.strip()
                    for i in item.findAll("a", class_="b-link b-link_style_black")
                ]
                + [date]
            )
    return data


def main():
    csvfile = open("scraped_stats.csv", "r+", newline="")
    # Checks the last events date to see if there are any new events.

    try:
        last_date = datetime.datetime.strptime(
            csvfile.readlines()[-1].split(",")[2].strip(), "%Y-%m-%d %H:%M:%S"
        )
    except:
        # If file is empty choose an old date as last date to compare to.
        last_date = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")

    r = requests.get("http://www.ufcstats.com/statistics/events/completed?page=all")
    soup = BeautifulSoup(r.content, "html5lib")

    # Takes the links for each event that is new from last pull.
    links = []
    for el in soup.findAll("i", class_="b-statistics__table-content"):
        if el.findChild("span").get_text(strip=True):
            event_date = convert_date(el.findChild("span").get_text(strip=True))
            if event_date > last_date and el.findChild(
                "a", class_="b-link b-link_style_black"
            ):
                links.append(
                    el.findChild("a", class_="b-link b-link_style_black")["href"]
                )
    data = []
    links = list(reversed(links))

    # Pull data from each site using multithreading.
    with ThreadPoolExecutor(max_workers=5) as executor:
        try:
            results = executor.map(pull_data, links)
        except Exception as e:
            print(e)
    for result in results:
        data.extend(result)

    # Calculate elo's gained for each fight and write to file for later use.
    writer = csv.writer(csvfile)
    elos = {}
    for i in range(len(data)):
        if len(data[i]) < 4:
            names = data[i][:2]
            elos = update_elos(names[0], names[1], elos)
            elo = calulate_elo_winner(elos[names[0]], elos[names[1]])
            elos[names[0]] += elo
            elos[names[1]] -= elo
            data[i].append(elo)
    for i in data:
        writer.writerow(i)
    csvfile.close()


if __name__ == "__main__":
    main()
