# SocialCreditBot
 Just For Memes Discord Bot that reads the conversation and gives you a positive or negative social credit score depending on your messages using TextBlob Sentiment Analysis. - Super basic, super WIP. Don't use, this is purely for a joke and for practice. Built using Python, Discord.py, SQLite, and TextBlob. 

Features
--------

-   Analyzes messages for sentiment using TextBlob
-   Rewards or deducts social credit scores based on sentiment
-   Persistently stores scores in an SQLite database
-   Provides commands for users to view/manage their score
-   Displays a leaderboard of top scoring users

Usage
-----

1.  Install requirements from requirements.txt
2.  Set up config files for token, roles, keywords
3.  Run bot.py
4.  Use commands like `?score`, `?give`, `?take`

Commands
--------

-   `?score` - Shows your current score
-   `?give` - Adds points to another user
-   `?take` - Deducts points from a user
-   `?reset` - Resets a user's score to 0
-   `?set` - Sets a user's score to a value
-   `?board` - Shows the leaderboard

Database
--------

The `scores.db` SQLite database contains a `scores` table with:

-   `user_id` as PRIMARY KEY
-   `score` integer column

This stores and retrieves social credit scores.

Configuration
-------------

Copy example files and edit for your bot:

-   `roles.txt` - Role name to check permissions
-   `keywords.txt` - Words to monitor in messages
-   `token.txt` - Discord bot user token