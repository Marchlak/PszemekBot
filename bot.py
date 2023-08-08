import discord
from discord.ext import commands
from discord import app_commands
import bingo
from bingo import Bingo, Bingo_Owner
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import os
import nacl
import time
import asyncio
import math
from mutagen.mp3 import MP3
import config

def run_discord_bot():
    bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())
    TOKEN= config.get_token()
    last_open = {}

    @bot.event
    async def on_ready():
        print("Bot is Up and Ready!")
        try:
            synced = await bot.tree.sync()
            print (f"Synced {len (synced)} commands")
        except Exception as e:
            print(e)

    @bot.tree.command(name="help")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hey {interaction.user.mention}! to jest slashowa komenda")

    @bot.tree.command(name="create")
    @app_commands.describe(tittle="Tittle od the bingo", size="Size of bingo")
    async def create(interaction: discord.Interaction, tittle: str, size: int):
        if(it_is_game(str(interaction.user.id)) is True):
            await interaction.response.send_message("Podczas gry nie można dokonywać żadnych zmian")
            return
        name= tittle + '.json'
        if(os.path.exists(os.path.join(str(interaction.user.id),name))):
            await interaction.response.send_message("Bingo o takiej nazwie już istnieje")
            return
        folder_path = str(interaction.user.id)
        json_file_count = sum(1 for file in os.listdir(folder_path) if file.endswith('.json'))
        if json_file_count >= 10:
            await interaction.response.send_message("Limit ilości bingo zostały wyczerapane")
            return

        if(size >= 3 and size <= 7):
            if(bingo.max_tittle_size(tittle,size) is True):
                new_bingo = Bingo(size,tittle,str(interaction.user.id))
                new_bingo.save_to_file()
                print(interaction.user.id)
                bingo.generate_image(new_bingo,size,str(interaction.user.id),False)
                await interaction.response.send_message(file=discord.File(os.path.join(str(interaction.user.id),"bingo.png")))
            else:
                await interaction.response.send_message("Zły rozmiar tytułu")
        else:
            await interaction.response.send_message("Zły rozmiar binga (minimalny to 3 maxymalny to 7)")

    @bot.tree.command(name="showall")
    async def showall(interaction: discord.Interaction):
        if (it_is_game(str(interaction.user.id)) is True):
            await interaction.response.send_message("Podczas gry nie można dokonywać żadnych zmian")
            return
        embed = discord.Embed(title="Twoje binga")
        files = os.listdir(str(interaction.user.id))
        json_files = [file for file in files if file.endswith(".json")]
        for index,file in enumerate(json_files, start=1):
                embed.add_field(name="",value=str(index) + ". " + str(file)[:-5],inline=False)
        await interaction.response.send_message(embed=embed)


    @bot.tree.command(name="open")
    @app_commands.describe(number="Bingo które chcesz edytować")
    async def open(interaction: discord.Interaction,number: int):
        if (it_is_game(str(interaction.user.id)) is True):
            await interaction.response.send_message("Podczas gry nie można dokonywać żadnych zmian")
            return

        if(get_json_filename_by_number(str(interaction.user.id),number)is not None):
            folder_path = str(interaction.user.id)
            file_index = number
            json_files = [file for file in os.listdir(str(interaction.user.id)) if file.endswith('.json')]
            if len(json_files) == 0:
                await interaction.response.send_message(f"W folderze '{folder_path}' nie ma plików z rozszerzeniem .json.")
                return

            if file_index < 1 or file_index > len(json_files):
                await interaction.response.send_message(f"Nieprawidłowy numer pliku. Dostępne numery to: 1-{len(json_files)}")
                return
            file_name = get_json_filename_by_number(str(interaction.user.id),number)
            if(os.path.exists(os.path.join(str(interaction.user.id),"data.json"))):
                bingo_owner = Bingo_Owner.load_from_json(str(interaction.user.id))
                bingo_owner.bingo_game = file_name
                bingo_owner.save_to_json()
                await interaction.response.send_message(f"Bingo zostało otworzone {file_name[:-5]}")
            else:
                bingo_owner = Bingo_Owner(str(interaction.user.id),None,file_name)
                bingo_owner.save_to_json()
                await interaction.response.send_message(f"Bingo zostało otworzone {file_name[:-5]}")
        else:
            await interaction.response.send_message("Nie ma bingo o takim numerze")

    @bot.tree.command(name="setcell")
    @app_commands.describe(row="Rząd",col="wiersz",cell="tekst w środku")
    async def setcell(interaction: discord.Interaction, row: int, col:int, cell:str):
        if (it_is_game(str(interaction.user.id)) is True):
            await interaction.response.send_message("Podczas gry nie można dokonywać żadnych zmian")
            return

        if (last_open_bingo(str(interaction.user.id)) is not None):
            last_open = last_open_bingo(str(interaction.user.id))
            temp_bingo = Bingo.load_from_file(last_open,str(interaction.user.id))

            if(row-1>=0 and row-1<temp_bingo.get_size() and col-1>=0 and col-1<temp_bingo.get_size()):
                previous_word = temp_bingo.get_word(row-1,col-1)
                temp_bingo.set_word(row-1,col-1,cell)
                word = temp_bingo.get_word(row-1,col-1)

                if previous_word is None:
                    previous_word = "-"
                temp_bingo.save_to_file()
                await interaction.response.send_message(f"Hasło {previous_word} zostało zastąpione {word}")
            else:
                await interaction.response.send_message("Wiersz lub kolumna pozazakresem")
        else:
            await interaction.response.send_message("Żadne bingo nie jest otwarte")

    @bot.tree.command(name="show")
    async def show(interaction: discord.Interaction):
        bingo_name = "bingo.png"
        if (it_is_game(str(interaction.user.id)) is True):
            bingo_name="bingo_game.png"

        if (last_open_bingo(str(interaction.user.id)) is not None):
            last_open = last_open_bingo(str(interaction.user.id))
            temp_bingo = Bingo.load_from_file(str(last_open),str(interaction.user.id))
            bingo.generate_image(temp_bingo,temp_bingo.get_size(),str(interaction.user.id),False)
            print(str(interaction.user.id) + " " + str(last_open))
            await interaction.response.send_message(file=discord.File(os.path.join(str(interaction.user.id),bingo_name)))
        else:
            await interaction.response.send_message("Żadne bingo nie jest otwarte")

    @bot.tree.command(name="start")
    async def start(interaction: discord.Interaction):
        if(last_open_bingo(str(interaction.user.id)) is not None):
            bingo_owner = Bingo_Owner.load_from_json(str(interaction.user.id))
            if(bingo_owner.bingo_game is None):
                bingo_owner.bingo_game=bingo_owner.last_open_bingo
                last_open = last_open_bingo(str(interaction.user.id))
                temp_bingo = Bingo.load_from_file(last_open,str(interaction.user.id))
                bingo.generate_image(temp_bingo,temp_bingo.get_size(),str(interaction.user.id),True)
                bingo_owner.save_to_json()
                await interaction.response.send_message("Rozpoczeles gre bingo")
            else:
                await interaction.response.send_message("Gra w bingo już trwa")
        else:
            await interaction.response.send_message("Żadne bingo nie jest otwarte")


    @bot.tree.command(name="cross")
    @app_commands.describe(row="Rząd",col="wiersz")
    async def cross(interaction: discord.Interaction, row: int, col: int):
        if(it_is_game(str(interaction.user.id)) is True):
            bingo_owner = Bingo_Owner.load_from_json(str(interaction.user.id))
            if (bingo_owner.bingo_game is not None):
                last_open = bingo_owner.bingo_game
                temp_bingo = Bingo.load_from_file(last_open, str(interaction.user.id))
                if (row - 1 >= 0 and row - 1 < temp_bingo.get_size() and col - 1 >= 0 and col - 1 < temp_bingo.get_size()):
                    a,b,c,d = temp_bingo.mark_cell(row-1,col-1)
                    temp_bingo.save_to_file()
                    image_path = os.path.join(str(interaction.user.id),"bingo_game.png")
                    bingo.draw_crossed_square(image_path,row,col,temp_bingo.get_size())
                    bingo.draw_bingo(image_path ,a ,b ,c ,d , temp_bingo.get_size())
                    await interaction.response.send_message(file=discord.File(image_path))
                else:
                    await interaction.response.send_message("Zły rozmiar")
            else:
                await interaction.response.send_message("Żadna gra nie jest uruchomiana")
        else:
            await interaction.response.send_message("Żaden bingo nie zostało otwarte")
    @bot.tree.command(name="stop")
    async def stop(interaction: discord.Interaction):
        if(it_is_game(str(interaction.user.id)) is True):
            bingo_owner = Bingo_Owner.load_from_json(str(interaction.user.id))
            temp_bingo = Bingo.load_from_file(bingo_owner.bingo_game,str(interaction.user.id))
            temp_bingo.clean_marked()
            temp_bingo.save_to_file()
            bingo_owner.bingo_game = None
            bingo_owner.save_to_json()
            await interaction.response.send_message("Gra została przerwana")
        else:
            await interaction.response.send_message("Gra nie jest w trakcie")

    @bot.tree.command(name="delete")
    @app_commands.describe(number="numer który chcesz użyć")
    async def delete(interaction: discord.Interaction, number: int):
        if (it_is_game(str(interaction.user.id)) is True):
            await interaction.response.send_message("Podczas gry nie można dokonywać żadnych zmian")
            return
        if (get_json_filename_by_number(str(interaction.user.id), number) is not None):
            folder_path=str(interaction.user.id)
            file_index = number
            json_files = [file for file in os.listdir(str(interaction.user.id)) if file.endswith('.json')]
            if len(json_files) == 0:
                await interaction.response.send_message(f"W folderze '{folder_path}' nie ma plików z rozszerzeniem .json.")
                return

            if file_index < 1 or file_index > len(json_files):
                await interaction.response.send_message(f"Nieprawidłowy numer pliku. Dostępne numery to: 1-{len(json_files)}")
                return

            temp_bingo_owner = Bingo_Owner.load_from_json(str(interaction.user.id))
            if(temp_bingo_owner.last_open_bingo == get_json_filename_by_number(str(interaction.user.id), number)):
                temp_bingo_owner.last_open_bingo = None
                temp_bingo_owner.save_to_json()

            file_to_remove = json_files[file_index - 1]
            file_path = os.path.join(folder_path, file_to_remove)
            os.remove(file_path)
            await interaction.response.send_message(f"Bingo {file_to_remove[:-5]} zostało usunięte")
        else:
            await interaction.response.send_message(f"Nie ma takiego Binga")

    @bot.tree.command(name="host")  # poprawić to gówno
    async def join(interaction: discord.Interaction):
        await interaction.response.send_message("w trakcie robienia")

    @bot.tree.command(name="join")  # poprawić to gówno
    @app_commands.describe(gameid="id gry")
    async def join(interaction: discord.Interaction, gameid: int):
        await interaction.response.send_message("w trakcie robienia")


    @bot.tree.command(name="playsounds")
    @app_commands.describe(title="Tittle od the bingo")
    async def playsounds(interaction: discord.Interaction, title: str):
        if not(os.path.exists(os.path.join("playsounds",title +".mp3"))):
            await interaction.response.send_message("Nie ma takiego binda")
            return
        if not bot.voice_clients:
            await interaction.response.send_message("Puszczam dźwięk")
            voicechannel = interaction.user.voice.channel
            vc = await voicechannel.connect()
            name = title + ".mp3"
            name = os.path.join("playsounds", name)
            vc.play(discord.FFmpegPCMAudio(name))
            counter = 0
            duration = int(get_mp3_duration(name)+1)
            while not counter >= duration:
                await asyncio.sleep(1)
                counter = counter + 1
            await vc.disconnect()
        else:
            await interaction.response.send_message("Bot jest połaczony z kanałem")

    @bot.tree.command(name="showsounds")
    async def showsounds(interaction: discord.Interaction):
        data = get_files_without_extension("playsounds")
        pagination = PaginationView(timeout = None)
        pagination.data = data
        await pagination.send(interaction)




    bot.run(TOKEN)


def last_open_bingo(owner):
    folder_path = os.path.join(owner,"data")
    if not os.path.exists(os.path.join(folder_path,"data.json")):
        return 0
    else:
        bingo_owner = Bingo_Owner.load_from_json(owner)
        if(bingo_owner.is_last_bingo_open() is not None):
            return bingo_owner.is_last_bingo_open()
        else:
            return None

def it_is_game(owner):
    folder_path = os.path.join(owner, "data")
    if not os.path.exists(os.path.join(folder_path,"data.json")):
        return False
    else:
        bingo_owner = Bingo_Owner.load_from_json(owner)
        if(bingo_owner.bingo_game is None):
            return False
        else:
            return True

def get_json_filename_by_number(folder_path, json_number):
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]

    if 1 <= json_number <= len(json_files):
        return json_files[json_number - 1]  # Return the nth file from the sorted list
    else:
        return None

def get_files_without_extension(folder_path):
    # Lista, która będzie przechowywać nazwy plików bez rozszerzeń
    file_names_without_extension = []

    # Sprawdzenie, czy ścieżka folderu istnieje
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' nie istnieje.")
        return file_names_without_extension

    # Pobranie listy plików z folderu
    files = os.listdir(folder_path)

    # Pętla po każdym pliku
    for file in files:
        # Sprawdzenie, czy to jest plik (a nie katalog)
        if os.path.isfile(os.path.join(folder_path, file)):
            # Pobranie samej nazwy pliku bez rozszerzenia
            file_name_without_extension, file_extension = os.path.splitext(file)
            # Dodanie nazwy pliku do listy
            file_names_without_extension.append(file_name_without_extension)

    return file_names_without_extension

def get_mp3_duration(file_path):
    try:
        audio = MP3(file_path)
        duration_in_seconds = int(audio.info.length)
        return duration_in_seconds
    except Exception as e:
        print("Wystąpił błąd:", e)
        return None

class PaginationView(discord.ui.View):
    current_page : int = 1
    sep : int = 10

    async def send(self, interaction):
        await interaction.response.send_message(view=self)
        await self.update_message(self.data[:self.sep],interaction)

    def create_embed(self, data):
        embed = discord.Embed(title=f"User List Page {self.current_page} / {int(len(self.data) / self.sep) + 1}")
        for item in data:
            embed.add_field(name=item, value="", inline=False)
        return embed

    async def update_message(self,data, interaction):
        self.update_buttons()
        await interaction.edit_original_response(embed=self.create_embed(data), view=self)

    def update_buttons(self):
        if self.current_page == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.current_page == int(len(self.data) / self.sep) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

    def get_current_page_data(self):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page ==  math.ceil(len(self.data) / self.sep):
            from_item = self.current_page * self.sep - self.sep
            until_item = len(self.data)
        return self.data[from_item:until_item]


    @discord.ui.button(label="|<",
                       style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = 1

        await self.update_message(self.get_current_page_data(),interaction)

    @discord.ui.button(label="<",
                       style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page -= 1
        await self.update_message(self.get_current_page_data(),interaction)

    @discord.ui.button(label=">",
                       style=discord.ButtonStyle.primary)
    async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page += 1
        await self.update_message(self.get_current_page_data(),interaction)

    @discord.ui.button(label=">|",
                       style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.current_page = int(len(self.data) / self.sep) + 1
        await self.update_message(self.get_current_page_data(),interaction)












