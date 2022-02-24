import requests
import time
from bs4 import BeautifulSoup
from math import inf
from notify_run import Notify


def check_and_notify_book_price(book_title : str, price_threshold : float, destination : str, book_language : str, channel_id : str):
    """
    Checks price of book in bookfinder.com website and notifies
    the user in case lowest available price (with shipping) is lower 
    than price threshold.

    Args:
        book_title (str): Title of the desired book
        price_threshold (float): Upper bound on the desired price
        destination (str): Country code of the book's destination (e.g. 'PT' for Portugal)
        book_language (str): Language of the desired book (e.g. 'en' for english)
        channel_id (str): Endpoint of user's private Notify's package channel 
        (see the config example in https://pypi.org/project/notify-run/)
    """

    cleaned_title = book_title.replace(" ","+").lower()
    search_url = f'https://www.bookfinder.com/search/?title={cleaned_title}&lang={book_language}&new_used=*&destination={destination}&currency=EUR&binding=*&isbn=&keywords=&minprice=&maxprice=&publisher=&min_year=&max_year=&mode=advanced&st=sr&ac=qr'
    search_response = requests.get(search_url)

    if 'all matches combined' in search_response.text: # case where there is more than 1 search result with the book query
        book_url = search_response.text.split("href")[18].split('"')[1]+'&ps=tp'
    else: # case where there is exactly 1 search result with the book query
        book_url = search_response.text.split("href")[17].split('"')[1]+'&ps=tp'

    time.sleep(.1)
    response = requests.get(book_url)
    html_content = BeautifulSoup(response.text, "html.parser")

    clean_html = html_content.text.strip()
    prices = clean_html.split("€")

    min_cost = inf
    number_book_options = len(prices)

    for j in range(1, number_book_options): # running over all book options
        cost = float(prices[j][:5].replace(",","."))
        if cost < min_cost: # check if book option cost is lower than minimum cost
            min_cost = cost

    print(f'Current lowest price of book {book_title} is: {min_cost}€.')

    if min_cost <= price_threshold and channel_id:
        notify = Notify(endpoint=f'https://notify.run/{channel_id}')
        notify.send(f'Book {book_title} costs {min_cost}€')

# EXAMPLE: 
book_list = ['Practical Statistics for Data Scientists', 'Information Theory, Inference and Learning Algorithms', 'Machine Learning: A Probabilistic Perspective', 'Approaching (Almost) Any Machine Learning Problem']

for book_title in book_list:
    check_and_notify_book_price(book_title = book_title, price_threshold = 15, destination = 'PT', book_language = 'en', channel_id = None)