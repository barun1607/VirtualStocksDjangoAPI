import nltk
nltk.download('vader_lexicon')
from GoogleNews import GoogleNews

# from newsplease import NewsPlease
import io
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import base64
from io import StringIO
from matplotlib import cm
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.http import JsonResponse
from nltk.sentiment.vader import SentimentIntensityAnalyzer

@api_view(['GET'])
def get_news_links(request, name):
    googlenews = GoogleNews()
    print(name)
    googlenews.get_news(name+'stock')
    links=googlenews.results()
    print(links)
    return JsonResponse(links,safe=False)

@api_view(['GET'])
def get_news_analysis(request, name):
    headlines=[]
    dates=[]
    s = io.BytesIO()
    new_words = {
        'crushes': 10,
        'beats': 5,
        'misses': -5,
        'fell':-80,
        'trouble': -10,
        'surged':-100,
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
    googlenews.get_news(name+' stock')
    links=googlenews.results()

    headlines=[]
    dates=[]
    for link in links:
        flag = 0
        if link.get('datetime')!=None:
            dates.append(link.get('datetime'))
        elif link.get('date')=='Yesterday':
            now = datetime.now() # current date and time
            now=now-timedelta(days=1)
            dates.append(now)
        else:
            try:
                if '-' in str(link.get('date')):
                    dates.append(datetime.strptime(link['date'],'%d-%b-%Y'))
                else:
                    if datetime.strptime(link['date'] + " 2021",'%d %b %Y') > datetime.now():
                        dates.append(datetime.strptime(link['date'] + " 2020",'%d %b %Y'))
                    else:
                        dates.append(datetime.strptime(link['date'] + " 2021",'%d %b %Y'))                    
            except Exception as e:
                flag = 1
                print(e)
        if flag == 0:
            headlines.append(link.get('title'))
    parsed_news=list(zip(dates, headlines, dates)) 
    columns = ['Date', 'Headline','Time']
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

    # Group by date and ticker columns from scored_news and calculate the mean
    mean_c = scored_news.groupby(['Date']).mean()
    mean_c = mean_c.xs('compound', axis='columns')
    ax=mean_c.plot(kind='bar', figsize=(10,3),rot=45,title='Market Sentiment based on News',colormap=cm.gist_rainbow,stacked=True)
    ax.set_ylabel('Sentiment')
    plt.plot()
    plt.savefig(s, format="png")
    plt.close()
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    return HttpResponse("data:image/png;base64,%s"%s)

@api_view(['GET'])
def get_news_analysis_for_day(request, name,date):
    headlines=[]
    dates=[]
    s = io.BytesIO()
    new_words = {
        'crushes': 10,
        'beats': 5,
        'misses': -5,
        'fell':-80,
        'trouble': -10,
        'surged':-100,
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
    googlenews.get_news(name+' stock')
    links=googlenews.results()

    headlines=[]
    dates=[]
    for link in links:
        flag = 0
        if link.get('datetime')!=None:
            dates.append(link.get('datetime'))
        elif link.get('date')=='Yesterday':
            now = datetime.now() # current date and time
            now=now-timedelta(days=1)
            dates.append(now)
        else:
            try:
                if '-' in str(link.get('date')):
                    dates.append(datetime.strptime(link['date'],'%d-%b-%Y'))
                else:
                    if datetime.strptime(link['date'] + " 2021",'%d %b %Y') > datetime.now():
                        dates.append(datetime.strptime(link['date'] + " 2020",'%d %b %Y'))
                    else:
                        dates.append(datetime.strptime(link['date'] + " 2021",'%d %b %Y'))                    
            except Exception as e:
                flag = 1
                print(e)
        if flag == 0:
            headlines.append(link.get('title'))
    parsed_news=list(zip(dates, headlines, dates)) 
    columns = ['Date', 'Headline','Time']
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
    ddte=datetime.strptime(date,'%d-%m-%Y').date()
    single_day = scored_news[ scored_news["Date"] == ddte].copy()
    single_day['Time'] = pd.to_datetime(single_day['Time']).dt.time
    single_day.set_index('Time', inplace=True)
    single_day.sort_index(inplace=True)

    TITLE = "Positive, negative and neutral sentiment for {} on {}".format(name,date)
    COLORS = ["red", "orange", "green"]

    plot_day = single_day.drop(['Headline','compound','Date'], axis=1)

    # Drop the columns that aren't useful for the plot
    # Change the column names to 'negative', 'positive', and 'neutral'
    plot_day.columns = ['negative', 'positive', 'neutral']

    # Plot a stacked bar chart
    ax=plot_day.plot(kind='bar', color=COLORS, figsize=(10,3), width=0.3)
    ax.set_ylabel('Sentiment')

    # mean_c = scored_news.groupby(['Date']).mean()
    # mean_c = mean_c.xs('compound', axis='columns')
    # ax=mean_c.plot(kind='bar', figsize=(20,5),rot=45,title='Market Sentiment based on News',colormap=cm.gist_rainbow,stacked=True)
    plt.plot()
    plt.savefig(s, format="png")
    plt.close()
    s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
    return HttpResponse("data:image/png;base64,%s"%s)


