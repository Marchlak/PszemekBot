from PIL import Image, ImageDraw, ImageFont
import os
import json
alphabet = "abcdefghijklmnoprstuvxyzABCDEFGHIJKLMNOPRSTUYWVXYZ"
def generate_image(bingo, table_size, owner,game):
    # Ustawienia obrazka
    edges = 20
    titlle_edge = 36+30
    width = table_size * 100 + edges
    height = table_size * 100 + edges//2 + titlle_edge
    cell_width = 100
    cell_height = 100


    background_color = (255, 255, 255)  # Biały kolor tła
    text_color = (0, 0, 0)  # Czarny kolor tekstu
    title_font_size = 32
    clues = bingo.get_all_words()
    # Tworzenie obrazka
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype("arial.ttf", title_font_size)
    title_text = bingo.get_tittle()
    title_ascent, title_descent = title_font.getmetrics()
    title_text_width = title_font.getmask(title_text).getbbox()[2]
    title_text_height =title_font.getmask(alphabet).getbbox()[3] + title_descent
    title_x = (width - title_text_width)//2
    title_y = (titlle_edge-title_text_height)//2
    draw.text((title_x, title_y), title_text, font=title_font, fill=text_color)
    #tabela

    table_x = (width - cell_width * table_size) / 2
    table_y = titlle_edge



    for row in range(table_size):
        for col in range(table_size):
            #okreslanie pozycji kratki i jej rysowanie
            cell_x = table_x + col * cell_width
            cell_y = table_y + row * cell_height
            draw.rectangle(
                [(cell_x, cell_y), (cell_x + cell_width, cell_y + cell_height)],
                outline=text_color,
            )
            #dopasowywanie rozmiaru czcionki
            cell_text = clues[row%table_size+col*table_size]
            cell_font_size , word_size = cell_font_size_test(cell_text, cell_width)
            cell_font = ImageFont.truetype("arial.ttf", cell_font_size)
            cell_text = split_word(cell_text, 16)
            result = split_text(cell_text, word_size)
            lines = len(result)
            cell_ascent, cell_descent = cell_font.getmetrics()
            cell_text_height = cell_font.getmask(alphabet).getbbox()[3] + cell_descent
            #print("To jest cell_y {} to jest cell_height {} cell_text_height {}, to ilosc linijek {} to tekst{} to linijki{} to dlugosc slowa {}".format(cell_y, cell_height, cell_text_height,lines,cell_text,result,word_size))
            cell_text_y = cell_y + ((cell_height - (lines*cell_text_height)) // 2)
            for index, line in enumerate(result):
                cell_text_width = cell_font.getmask(line).getbbox()[2]
                cell_text_x = cell_x + (cell_width - cell_text_width) // 2
                if(index!=0):
                    cell_text_y += cell_text_height
                draw.text((cell_text_x, cell_text_y), line, font=cell_font, fill=text_color)
    if(game==True):
        bingo_name="bingo_game.png"
    else:
        bingo_name="bingo.png"
    image.save(os.path.join(owner,bingo_name))

def cell_font_size_test(text, size):
    longest_word = Longest_word(text)
    longest_word_lenght = len(longest_word)
    #print("Najdluzsze slowo {} i ile ma {}".format(longest_word, longest_word_lenght))
    for i in range (40,9, -1):
        cell_font_size = i #przypisuje czcionkę
        cell_font = ImageFont.truetype("arial.ttf", cell_font_size) #ustawiam font
        cell_text_width = cell_font.getmask(longest_word).getbbox()[2]
        if(size - cell_font.getmask("a").getbbox()[2] >= cell_text_width):
                for j in range (i,9,-1):
                    new_text = split_text(text,longest_word_lenght)
                    new_longest_word = longest_word + "A"
                    lines = len(new_text)
                    cell_font_size = j
                    cell_font = ImageFont.truetype("arial.ttf", cell_font_size)
                    cell_ascent, cell_descent = cell_font.getmetrics()
                    cell_text_height = cell_font.getmask(alphabet).getbbox()[3] + cell_descent
                    if(size-cell_font.getmask("a").getbbox()[2]>=cell_font.getmask(new_longest_word).getbbox()[2]):
                        longest_word= new_longest_word
                        longest_word_lenght += 1
                    if(size-cell_text_height >= cell_text_height*lines):
                            return j, longest_word_lenght
    return 10, longest_word_lenght




def Longest_word(text):
    if isinstance(text, str):  # Sprawdź, czy argument jest pojedynczym stringiem
        words = text.split()
    elif isinstance(text, list):  # Sprawdź, czy argument jest listą słów
        words = text
    else:
        return "Invalid input. Please provide a string or a list of words."

    if words:
        return max(words, key=len)
    else:
        return None
def split_text(text, max_lenght):
    words = text.split()
    result = []
    actual_line = ''

    for word in words:
        if len(word) > max_lenght:
            raise ValueError("The word '{}' is longer than the maximum length.".format(word))
        if len(word + ' ' + actual_line)<= max_lenght or not actual_line:
            actual_line = actual_line + ' ' + word if actual_line else word
        else:
            result.append(actual_line.strip())
            actual_line = word
    if actual_line:
        result.append(actual_line)
    return result

def split_word(text, max_lenght):
    words = text.split()
    result = []
    max_lenght -= 1
    for word in words:
        word_lenght = len(word)
        number_of_parts = (word_lenght) // max_lenght
        if(word_lenght % max_lenght):
            number_of_parts += 1

        parts = []
        if(number_of_parts>1):
            for i in range(number_of_parts - 1):
                if(i!= number_of_parts - 2):
                    start = i * max_lenght
                    end = (i + 1) * max_lenght
                    part = word[start:end]
                    part += '-'
                elif(word_lenght - (i * max_lenght) != max_lenght+1):
                    start = i * max_lenght
                    part_lenght = word_lenght-start
                    end =  start + part_lenght//2 + part_lenght%2
                    part = word[start:end]
                    part += '-'
                    parts.append(part)
                    start = end
                    end = word_lenght
                    part = word[start:end]
                else:
                    start = i* max_lenght
                    end = word_lenght
                    part = word[start:end]
                parts.append(part)
        else:
            parts.append(word)

        result.append(' '.join(parts))
    return ' '.join(result)


def draw_crossed_square(image_path,row,col,size):
    try:
        # Wczytanie obrazka
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        x=10+(row-1)*100
        y=66+(col-1)*100
        # Rysowanie czerwonej linii przekreślającej kwadrat
        draw.line((x, y, x + 100, y+100), fill="red", width=2)
        draw.line((x+100, y, x, y+100), fill="red", width=2)

        # Zapisanie zmodyfikowanego obrazka
        img.save(image_path)
    except Exception as e:
        print("Wystąpił błąd:", e)

def draw_bingo(image_path,row,col,diag1,diag2,size):
    try:
        # Wczytanie obrazka
        img = Image.open(image_path)
        print(image_path)
        draw = ImageDraw.Draw(img)
        # Rysowanie czerwonej linii przekreślającej kwadrat
        if(row!=0):
            draw.line((10,66+50+(row-1)*100, 10+size*100,66+50+(row-1)*100), fill="black", width=4)
        if(col!=0):
            draw.line((10+50+(100*(col-1)), 66, 10+50+(100*(col-1)), 66+size*100), fill="black", width=4)
        if(diag1!=0):
            draw.line((10, 66, 10 + size*100, 66 + size * 100), fill="black", width=4)
        if(diag2!=0):
            draw.line((10,66 + size*100,size*100+10,66), fill="black", width=4)
        img.save(image_path)
    except Exception as e:
        print("Wystąpił błąd:", e)

def max_tittle_size(title,size):
    title_font_size = 32
    title_font = ImageFont.truetype("arial.ttf", title_font_size)
    title_text_width = title_font.getmask(title).getbbox()[2]
    if(size*100>=title_text_width):
        return True
    else:
        return False








class Bingo:
    def __init__(self, size, name, owner):
        self.size = size
        self.name = name
        self.owner = owner
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.marked = [[False for _ in range(size)] for _ in range(size)]

    def clean_marked(self):
        for i in range(self.size):
            for j in range(self.size):
                self.marked[i][j] = False

    def set_word(self, row, col, word):
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            raise ValueError("Invalid row or column")
        test = split_word(word,16)
        test = split_text(test,16)
        if(len(test) <= 8):
            self.grid[row][col] = word
        else:
            print("bad lenght")


    def get_word(self, row, col):
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            raise ValueError("Invalid row or column")
        return self.grid[row][col]

    def get_tittle(self):
        return self.name

    def get_size(self):
        return self.size

    def mark_cell(self, row, col):
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            raise ValueError("Invalid row or column")
        self.marked[row][col] = True
        new_bingos = self.bingo_check(row,col)
        return new_bingos

    def bingo_check(self, row, col):
        bingos = []

        # Sprawdzanie binga wierszowego
        temp = col+1
        for i in range(self.size):
            if (self.marked[i][col] is False):
                print(i)
                temp=0
        bingos.append(temp)

        temp = row+1
        for i in range(self.size):
            if (self.marked[row][i] is False):
                print(i)
                temp = 0
        bingos.append(temp)

        temp = 0
        if(row == col):
            temp = 1
            for i in range(self.size):
                if(self.marked[i][i] is False):
                    temp = 0
        bingos.append(temp)

        temp = 0
        if (row == self.size-col-1):
            temp = 1
            for i in range(self.size):
                if (self.marked[i][self.size-i-1] is False):
                    temp = 0
        bingos.append(temp)



        return bingos

    def save_to_file(self):
        folder = f"{self.owner}"
        if not os.path.exists(folder):
            os.makedirs(folder)

        data = {
            "name": self.name,
            "size": self.size,
            "grid": self.grid,
            "marked": self.marked
        }

        file_path = os.path.join(folder, f"{self.name}.json")
        with open(file_path, "w") as file:
            json.dump(data, file)

    @classmethod
    def load_from_file(cls, bingo_name, owner):
        folder = f"{owner}"
        file_path = os.path.join(folder, bingo_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Bingo '{bingo_name}' for owner '{owner}' does not exist.")

        with open(file_path, "r") as file:
            data = json.load(file)

        size = data["size"]
        name = data["name"]
        bingo = cls(size, name, owner)
        bingo.grid = data["grid"]
        bingo.marked = data["marked"]

        return bingo

    def print_bingo(self):
        for row in self.grid:
            for word in row:
                if word is None:
                    print(" - ", end="")
                else:
                    print(f" {word} ", end="")
            print()

    def edit_word(self, row, col, new_word):
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            raise ValueError("Invalid row or column")
        test = split_word(new_word, 16)
        test = split_text(test, 16)
        if (len(test) <= 8):
            self.grid[row][col] = new_word
        else:
            print("bad lenght")

    def get_all_words(self):
        return [word if word is not None else "-" for row in self.grid for word in row]


class Bingo_Owner:
    def __init__(self, id_owner, bingo_game, last_open_bingo):
        self.id_owner = id_owner
        self.bingo_game = bingo_game
        self.last_open_bingo = last_open_bingo

    def save_to_json(self):
        data = {
            'id_owner': self.id_owner,
            'bingo_game': self.bingo_game,
            'last_open_bingo': self.last_open_bingo,
        }

        folder_name = str(self.id_owner)
        data_folder = os.path.join(folder_name, 'data')
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        file_path = os.path.join(data_folder, 'data.json')
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)

    @classmethod
    def load_from_json(cls, id_owner):
        folder_name = str(id_owner)
        data_folder = os.path.join(folder_name, 'data')
        file_path = os.path.join(data_folder, 'data.json')

        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
            return cls(data['id_owner'], data['bingo_game'], data['last_open_bingo'])
        else:
            return None

    def is_last_bingo_open(self):
        return self.last_open_bingo




