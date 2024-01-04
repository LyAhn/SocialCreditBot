import sqlite3
import discord
from operator import itemgetter
from textblob import TextBlob

version = "0.2"

############################Test stuff#################################
#with open('owners.txt') as f:
#    lines = f.readlines()
owner_id = "2528954110969118730"
role_name = "Janitor"

with open('token.txt') as f:
    token = f.read()

keywords = []
with open('keywords.txt') as f:
    keywords = f.readlines()
    keywords = [x.strip() for x in keywords]



######################################################################

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    watching = discord.Activity(type=discord.ActivityType.watching, name="you! 🇨🇳")
    await client.change_presence(activity=watching)
    
@client.event
async def on_message(message):
    
    # Leaderboard command
    if message.content.startswith('?board'):
        await display_leaderboard(message)
    
    
    if message.author == client.user:
        return

    if any(keyword in message.content.lower() for keyword in keywords):
        blob = TextBlob(message.content)
        sentiment = blob.sentiment.polarity
        
        score = 0
        
        if sentiment > 0.5:
            score = 25
            await message.channel.send(f'CCP Message for User: {message.author.mention}! China Appreciation Detected. {score} Credit Points have been added to your Government Profile :red_envelope: :flag_cn:')
        elif sentiment > 0:
            score = 10
            await message.channel.send(f'CCP Message for User: {message.author.mention}! China Appreciation Detected. {score} Credit Points have been added to your Government Profile :red_envelope: :flag_cn:')
        elif sentiment < -0.5:
            score = -25
            await message.channel.send(f'CCP Message for User: {message.author.mention}! We have detected improper behaviour! You have been deducted {score} points! ')
        elif sentiment < 0:
            score = -10
            await message.channel.send(f'CCP Message for User: {message.author.mention}! We have detected improper behaviour! You have been deducted {score} points! ')

        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scores (user_id INTEGER PRIMARY KEY, score INTEGER)')
        c.execute('SELECT score FROM scores WHERE user_id = ?', (message.author.id,))
        result = c.fetchone()
        if result is None:
            c.execute('INSERT INTO scores (user_id, score) VALUES (?, ?)', (message.author.id, score))
            result = (score,)
        else:
            c.execute('UPDATE scores SET score = ? WHERE user_id = ?', (result[0] + score, message.author.id))
        conn.commit()
        conn.close()

    if message.content.startswith('?give'):
        
        # Check author permissions
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        else:
        # Check if user is mentioned
            user = message.mentions[0]
        amount = int(message.content.split()[-1])
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = score + ? WHERE user_id = ?", (amount, user.id))
        conn.commit()
        conn.close()

        await message.channel.send(f"The CCP has awarded {user.mention} {amount} Social Credit Score!")
        
    if message.content.startswith('?take'):
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        user = message.mentions[0]
        amount = int(message.content.split()[-1])
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = score - ? WHERE user_id = ?",(amount, user.id))
        conn.commit()
        conn.close()
        await message.channel.send(f"The CCP has deducted {user.mention} {amount} Social Credit Score!")
        
    if message.content.startswith('?reset'):
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        user = message.mentions[0]
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = 0 WHERE user_id = ?",(user.id,))
        conn.commit()
        conn.close()
        await message.channel.send(f"The CCP has reset {user.mention} Social Credit Score!")
        
    if message.content.startswith('?set'):
        if role_name not in [role.name for role in message.author.roles]:
            return await message.channel.send(':raised_hand::octagonal_sign: This is a CCP command! :flag_cn: :raised_hand::octagonal_sign: ')
        else:
            user = message.mentions[0]
        amount = int(message.content.split()[-1])
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute("UPDATE scores SET score = ? WHERE user_id = ?",
                  (amount, user.id))
        await message.channel.send(f"The CCP has set {user.mention} Social Credit Score to {amount}!")
        conn.commit()
        conn.close()
        
    elif message.content.startswith('?score'):
        user = message.author
        if len(message.mentions) > 0:
            user = message.mentions[0]
        conn = sqlite3.connect('scores.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS scores (user_id INTEGER PRIMARY KEY, score INTEGER)')
        c.execute('SELECT score FROM scores WHERE user_id = ?', (user.id,))
        result = c.fetchone()
        if result is None:
            await message.channel.send(f':flag_cn: {user.mention} has not received a social credit score yet. :flag_cn:')
        else:
            await message.channel.send(f'{user.mention} has a social credit score of {result[0]}. :flag_cn:')

    if message.content.startswith('?help'):
        embed = discord.Embed(title='Social Credit Score Bot Help', description='Here are the available commands for the Social Credit Score Bot:', color=0xFF0000)
        embed.add_field(name='?score', value='Displays the social credit score of the user who sent the command. You can also mention another user to see their social credit score.', inline=False)
        embed.add_field(name='?help', value='Displays this help message.', inline=False)
        embed.add_field(name='?board', value='Displays the leaderboard of the users with the highest social credit scores.', inline=False)
        embed.add_field(name='?give', value='Gives a user a specified amount of social credit score. You must be an owner or a member of the CCP to use this command.', inline=False)
        embed.add_field(name='?take', value='Takes a user a specified amount of social credit score. You must be an owner or a member of the CCP to use this command.', inline=False)
        embed.add_field(name='?reset', value='Resets the social credit score of a user. You must be an owner or a member of the CCP to use this command.', inline=False)
        embed.add_field(name='?set', value='Sets the social credit score of a user to a specified amount. You must be an owner or a member of the CCP to use this command.', inline=False)
        embed.add_field(name='Version', value=(version), inline=True)
        await message.channel.send(embed=embed)
        
    # Define leaderboard function
async def display_leaderboard(message):

  # Connect to database
  conn = sqlite3.connect('scores.db')  
  c = conn.cursor()

  # Query all scores
  c.execute("SELECT user_id, score FROM scores ORDER BY score DESC")

  # Fetch results 
  results = c.fetchall()

  # Create embed message
  embed = discord.Embed(title="Social Credit Leaderboard")

  # Add fields for each result
  for pos, result in enumerate(results):
    user_id = result[0]
    score = result[1]
    user = client.get_user(user_id)
    color = 0xFF0000 if pos <3 else 0x00FF00
    emoji = "🥇" if pos==0 else "🥈" if pos==1 else "🥉" if pos==2 else ""
    embed.add_field(name=f"#{pos+1} {emoji}", value=f"{user} : {score:>10}")
    embed.color = color

  # Send embed message
  await message.channel.send(embed=embed)

# Close connection
  conn.close()


client.run(token)
