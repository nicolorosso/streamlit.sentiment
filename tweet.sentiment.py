import openpyxl
import pandas as pd
import snscrape
import spacy
import streamlit as st

# Load the Italian language model
nlp = spacy.load("it_core_news_sm")

def scrape_tweets(usernames, since, until):
    tweets = []

    # Collect tweets from each user
    for username in usernames:
        user_tweets = snscrape.tweet.user_tweets(username, since=since, until=until)
        tweets.extend(user_tweets)

    # Classify the sentiment of each tweet
    for tweet in tweets:
        # Use the nlp object to create a Doc object
        # containing the text of the tweet
        doc = nlp(tweet["text"])

        # Classify the sentiment of the tweet
        sentiment = doc.cats["POSITIVE"] - doc.cats["NEGATIVE"]

        if sentiment > 0:
            sentiment = "positive"
        elif sentiment == 0:
            sentiment = "neutral"
        else:
            sentiment = "negative"

        # Add the sentiment to the tweet
        tweet["sentiment"] = sentiment

    # Return the collected tweets
    return tweets

def export_to_excel(tweets):
    # Create an Excel workbook
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Write the tweets to the Excel worksheet
    for i, tweet in enumerate(tweets):
        worksheet.cell(row=i+1, column=1).value = tweet["username"]
        worksheet.cell(row=i+1, column=2).value = tweet["date"]
        worksheet.cell(row=i+1, column=3).value = tweet["text"]
        worksheet.cell(row=i+1, column=4).value = tweet["sentiment"]

    # Save the Excel workbook
    workbook.save("tweets.xlsx")

# Add a title and introductory text
# Add a welcoming message and instructions
st.markdown("# Twitter Sentiment Analyzer")
st.markdown("This app allows you to collect tweets from multiple users and analyze the sentiment of each tweet. Follow the instructions below to get started.")

# Ask the user for the usernames, start date, and end date
usernames = st.text_input("Enter the usernames of the users you want to collect tweets from (comma-separated):")
usernames = usernames.split(",")
since = st.text_input("Enter the start date for the collection (YYYY-MM-DD):")
until = st.text_input("Enter the end date for the collection (YYYY-MM-DD):")

# Collect the tweets using the user's input
tweets = scrape_tweets(usernames, since, until)

# Display the collected tweets
st.table(tweets)

# Ask the user if they want to export the tweets to an Excel file
if st.checkbox("Export to Excel"):
    # Export the collected tweets to an Excel file
    export_to_excel(tweets)

# Ask the user if they want to display the Excel table
if st.checkbox("Display Excel table"):
    # Read the Excel file using pandas
    df = pd.read_excel("tweets.xlsx")

    # Display the Excel table
    st.dataframe(df)

# Ask the user if they want to filter the tweets by username
if st.checkbox("Filter by username"):
    # Ask the user for the username(s) to filter by
    filter_username = st.text_input("Enter the username(s) to filter by (comma-separated):")
    filter_username = filter_username.split(",")

    # Filter the tweets by username
    filtered_tweets = []
    for tweet in tweets:
        if tweet["username"] in filter_username:
            filtered_tweets.append(tweet)
    tweets = filtered_tweets

# Ask the user if they want to display the sentiment distribution
if st.checkbox("Display sentiment distribution"):
    # Count the number of tweets with each sentiment
    sentiments = [tweet["sentiment"] for tweet in tweets]
    counts = {
        "positive": sentiments.count("positive"),
        "neutral": sentiments.count("neutral"),
        "negative": sentiments.count("negative"),
    }

    # Ask the user to choose between a bar chart and line plot
    chart_type = st.radio("Choose a chart type:", ("Bar chart", "Line plot"))

    # Display the sentiment distribution using the chosen chart type
    if chart_type == "Bar chart":
        st.bar_chart(counts)
    else:
        st.line_chart(counts)



