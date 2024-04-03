# Discord Bingo and Sound Bot
## Welcome to the Discord Bingo and Sound Bot! This bot enables you to host and play bingo games within your Discord server, as well as play specific sounds on a voice channel. Whether you're looking to add some fun to your community interactions or just enjoy games with friends, this bot has something for everyone.

### Features
- Create Bingo Games: Easily set up bingo games with custom titles and sizes.
- Manage Bingo: Open, show, and delete your bingo games. Limit the number of active bingos to keep things organized.
- Play Bingo: Start a bingo game, cross off numbers, and stop the game when it's over.
- Play Sounds: Play specific sounds from a pre-defined list on a voice channel.
- User Interaction: Users can join ongoing bingo games, view all available sound clips, and more.
## Getting Started
### Prerequisites
- Discord server with permissions to add bots
- Python 3.8 or newer
- Required Python libraries: discord.py, ffmpeg, mutagen, nacl, and others as needed for your specific setup
- Installation
- Clone this repository or download the source code.


### Create a config.py file in the root directory and define get_token() function to return your Discord bot token.


### Run the bot with python your_script_name.py.

### Adding the Bot to Your Server
- Navigate to the Discord Developer Portal.
- Create a new application and navigate to the "Bot" tab.
- Click "Add Bot" and customize your bot's profile.
- Under the "OAuth2" tab, generate an invitation link with the required permissions.
- Use the generated link to add the bot to your Discord server.
- Usage
- Creating a Bingo Game: !create <title> <size>
- <title>: A title for your bingo game.
- <size>: The size of the bingo grid (3 to 7).
- Showing All Bingos: !showall
- Opening a Bingo Game for Editing: !open <number>
- <number>: The number of the bingo to open, as shown by !showall.
- Setting a Cell in a Bingo Game: !setcell <row> <col> <text>
- <row>: The row number.
- <col>: The column number.
- <text>: The text to place in the specified cell.
- Showing the Current Bingo Game: !show
-Starting a Bingo Game: !start
- Crossing a Number Off in a Bingo Game: !cross <row> <col>
Stopping a Bingo Game: !stop
Deleting a Bingo Game: !delete <number>
Playing a Sound: !playsounds <title>
<title>: The title of the sound clip to play.
Listing Available Sounds: !showsounds
