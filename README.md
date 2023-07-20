HOW TO RUN LOCALLY? (Assuming you have python3.7 env setup)
1. Install flask using cmd 'pip install flask'
2. Run cmd 'export FLASK_APP=main.py'
3. Run cmd 'export FLASK_DEBUG=development'
4. Run cmd 'flask run'
4. Click on the localhost link to start the app.

Public API endpoints:
1. Retrieve a list of the most viewed articles for a week or a month
 Input params: start_date, end_date
 URL format: http://127.0.0.1:5000/most_viewed_articles?start_date={YYYYMMDD}&end_date={YYYYMMDD}
 For eg: http://127.0.0.1:5000/most_viewed_articles?start_date=20151111&end_date=20151113

2. For any given article, be able to get the view count of that specific article for a week or a month:
 Input params: article_title, start_date, end_date
 URL format: http://127.0.0.1:5000//article_view_count?article_title={article_name}&start_date={YYYYMMDD}&end_date={YYYYMMDD}
 For eg: http://127.0.0.1:5000/article_view_count?article_title=Main_Page&start_date=20151111&end_date=20151113

3. Retrieve the day of the month where an article got the most page views:
 Input params: article_title, year, month
 URL format: http://127.0.0.1:5000/article_most_viewed_day?article_title={article_name}&year={year}&month={month}
 For eg: http://127.0.0.1:5000/article_most_viewed_day?article_title=Main_Page&year=2015&month=10

 Testing:
 Used Apache JMeter for testing endpoints. Apache JMeter is an open-source software designed to load test functional behavior and measure performance.
 Configured the following:
 - Number of threads(users): 1000
 - Ramp-up period: 5s
 - Loop count: 1
 Added an HTTP Header manager to add the User-Agent header needed to invoke the endpoints.


