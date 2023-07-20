from flask import Flask, jsonify, render_template, request
from typing import List, Dict
import requests
import calendar


app = Flask(__name__)

WIKIPEDIA_API_BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
EXPECTED_DATE_LEN = 8


@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')


def parse_date(date: int) -> str:
    """
    :param date: date in format YYYYMMDD
    :return date: "YYYY/MM/DD"
    """
    date = str(date)
    year = date[:4]
    month = date[4:6]
    day = date[6:8]
    return f"{year}/{month}/{day}"


def get_articles_for_date(date: int) -> List:
    """
    This method gets all articles and views for a given date.

    :param date: date in format YYYYMMDD
    :return article items list

    Sample article item: {"article":"Main_Page","views":18793503,"rank":1}
    """
    curr_date = parse_date(date)
    url = f"{WIKIPEDIA_API_BASE_URL}/{curr_date}"

    items = []
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])

    # Check if items list is empty
    if not items:
        articles_list = []
    else:
        articles_list = items[0]["articles"]
    return articles_list


def get_articles_viewcount_for_period(start_date: int, end_date: int) -> Dict:
    """
    This method aggregates articles views over a period.

    :param start_date: start_date in format YYYYMMDD
    :param start_date: end_date in format YYYYMMDD
    :return Dict of articles and its views
    """
    article_viewcount = {}  # { "article_title" : 100 }
    current_date = start_date

    # Aggregate article views for all days over the given period
    while current_date <= end_date:
        articles_list = get_articles_for_date(current_date)
        for item in articles_list:
            article_title = item["article"]
            view_count = item["views"]
            if article_title not in article_viewcount:
                article_viewcount[article_title] = 0
            article_viewcount[article_title] += view_count
        current_date += 1  # increment current_date by one day
    return article_viewcount


@app.route("/most_viewed_articles", methods=["GET"])
def most_viewed_articles() -> Dict:
    """
    This method returns the most viewed articles sorted by view count.
    
    :param start_date: start_date in format YYYYMMDD
    :param start_date: end_date in format YYYYMMDD
    :return Dict of most viewed articles
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date parameters are required"}), 400

    # Check input date length
    if len(start_date) != EXPECTED_DATE_LEN or len(end_date) != EXPECTED_DATE_LEN:
        return jsonify({"error": "Invalid format. Please use YYYYMMDD date format."}), 400

    # Check if the date contains only numbers
    try:
        start_date = int(start_date)
        end_date = int(end_date)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYYMMDD format."}), 400

    articles = get_articles_viewcount_for_period(start_date, end_date)
    # sort in descending order by views
    sorted_articles = sorted(
        articles.items(), key=lambda x: x[1], reverse=True)
    return jsonify({"articles": sorted_articles}), 200


@app.route("/article_view_count", methods=["GET"])
def article_view_count() -> Dict:
    """
    This method gives the view count for the given article over a given time period.

    :param artcicle_title: name of the article
    :param start_date: start_date in format YYYYMMDD
    :param start_date: end_date in format YYYYMMDD
    :return view_count: aggregated view count over specified period
    """
    article_title = request.args.get("article_title")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not article_title or not start_date or not end_date:
        return (
            jsonify(
                {"error": "article_title, start_date, and end_date parameters are required"}),
            400,
        )
    # Check input date length
    if len(start_date) != EXPECTED_DATE_LEN or len(end_date) != EXPECTED_DATE_LEN:
        return jsonify({"error": "Invalid format. Please use YYYYMMDD date format."}), 400

    # Check if the date contains only numbers
    try:
        start_date = int(start_date)
        end_date = int(end_date)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYYMMDD format."}), 400

    articles = get_articles_viewcount_for_period(start_date, end_date)
    total_view_count = articles.get(article_title, 0)

    return jsonify({"article_title": article_title, "view_count": total_view_count}), 200


@app.route("/article_most_viewed_day", methods=["GET"])
def get_most_viewed_day_in_a_month_for_an_article() -> Dict:
    """
    This method finds the day of the month when the article got the most page views.

    :param article_title: name of the article
    :param year: year in format YYYY
    :param month: month in format MM
    :return date: day with most views for the given article in a given month
    """
    article_title = request.args.get("article_title")
    year = request.args.get("year")
    month = request.args.get("month")

    if not article_title or not year or not month:
        return jsonify({"error": "article_title, year and month parameters are required"}), 400

    if len(month) != 2 or len(year) != 4:
        return jsonify({"error": "Invalid format. Please use YYYY for year and MM for month format."}), 400

    # Check if the date contains only numbers
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return jsonify({"error": "Invalid format. Please use YYYY for year and MM for month format."}), 400

    max_views = 0
    most_viewed_day = None

    days_in_month = calendar.monthrange(int(year), int(month))[1]

    start_date = f"{year}{month}01"
    end_date = f"{year}{month}{days_in_month}"
    for date in range(int(start_date), int(end_date) + 1):
        articles_list = get_articles_for_date(date)
        if not articles_list:
            return max_views

        for item in articles_list:
            if item["article"] == article_title and item["views"] > max_views:
                max_views = item["views"]
                most_viewed_day = date

    most_viewed_day = parse_date(most_viewed_day)
    return jsonify({"article_title": article_title, "most_viewed_day": most_viewed_day}), 200


if __name__ == "__main__":
    app.run()
