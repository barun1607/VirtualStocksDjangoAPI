import nltk
nltk.download('vader_lexicon')
from GoogleNews import GoogleNews
# from newsplease import NewsPlease
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from datetime import timedelta
from rest_framework.response import Response

def get_news_links(request, name):
    googlenews = GoogleNews()
    googlenews.get_news(name+'stock')
    links=googlenews.results()
    return Response(links, status=status.HTTP_200_OK)

def get_news_analysis(request, name):
    headlines=[]
    dates=[]

    new_words = {
        'crushes': 10,
        'beats': 5,
        'misses': -5,
        'fell':-80,
        'trouble': -10,
        'rises':20,
        'new features':10,
        'product fail':-10,
        'failure':-15,
        'falls': -100,
    }
    # Instantiate the sentiment intensity analyzer with the existing lexicon
    vader = SentimentIntensityAnalyzer()
    # Update the lexicon
    vader.lexicon.update(new_words)

    googlenews = GoogleNews()
    googlenews.get_news(name+'stock')
    links=googlenews.results()

    for link in links:
        headlines.append(link.get('title'))
        if link.get('datetime')!=None:
            dates.append(link.get('datetime'))
        elif link.get('date')=='Yesterday':
            now = datetime.now() # current date and time
            now=now-timedelta(days=1)
            dates.append(now)
        else:
            if '-' in str(link.get('date')):
                dates.append(datetime.strptime(link['date'],'%d-%b-%Y'))
            else:
                dates.append(datetime.strptime(link['date'],'%d %b'))

    parsed_news=list(zip(dates, headlines))

    # Use these column names

    columns = ['Date', 'Headline']
    # Convert the list of lists into a DataFrame
    scored_news = pd.DataFrame(parsed_news, columns=columns)

    # Iterate through the headlines and get the polarity scores
    scores = scored_news['Headline'].apply(vader.polarity_scores)

    # Convert the list of dicts into a DataFrame
    scores_df = pd.DataFrame.from_records(scores)

    # Join the DataFrames
    scored_news = scored_news.join(scores_df)

    # # Convert the date column from string to datetime
    scored_news['Date'] = pd.to_datetime(scored_news.Date).dt.date
    print(scored_news.head())

    # Group by date and ticker columns from scored_news and calculate the mean
    mean_c = scored_news.groupby(['Date']).mean()

    # Unstack the column ticker

    # mean_c = mean_c.unstack('ticker')

    # Get the cross-section of compound in the 'columns' axis
    mean_c = mean_c.xs('compound', axis='columns')
    # Plot a bar chart with pandas

    mean_c.plot(kind='bar', figsize=(20,5), width=1,rot=45)


