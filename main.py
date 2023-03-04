import os
from dotenv import load_dotenv

import tkinter as tk
from tkinter import ttk, BOTH
from screeninfo import get_monitors

from Telegram import Telegram
from util import *

class CrisEletronicosAgenda(tk.Tk):
    __windows = {}
    __file_paths = {}
    __canvas_backgrounds = {}

    def __init__(self):
        load_dotenv()
        self.telegram = Telegram(os.getenv('TELEGRAM_BOT_TOKEN'))
        self.monitor_specs = get_monitors()[0].__dict__

        self.__file_paths['customers_path'] = os.getenv('CUSTOMERS_FILE_PATH')
        self.__file_paths['employees_path'] = os.getenv('EMPLOYEES_TOKENS_FILE_PATH')
        for file_path in self.__file_paths.values():
            if not os.path.isfile(file_path):
                make_paths(file_path)
        
        self.load_customers()

        tk.Tk.__init__(self, baseName='Cris Eletrônicos')

        self.set_app_config()
        self.set_styles()
        self.create_table()

        # Criação de rótulos e campos de entrada de dados
        tk.Label(self, text="Nome:").pack()
        self.nome = tk.Entry(self)
        self.nome.pack()

        tk.Label(self, text="Endereço:").pack()
        self.endereco = tk.Entry(self)
        self.endereco.pack()

        tk.Label(self, text="Telefone:").pack()
        self.telefone = tk.Entry(self)
        self.telefone.pack()

        # Criação do botão de cadastro
        self.botao_cadastro = tk.Button(self, text="Cadastrar", command=self.cadastrar)
        self.botao_cadastro.pack()

    def set_app_config(self):
        # Setting app window size to 70% of the monitor's height and width
        self.total_screen_width = self.winfo_screenwidth()
        self.total_screen_height = self.winfo_screenheight()
        screen_width = int(self.total_screen_width * 0.7)
        screen_height = int(self.total_screen_height * 0.7)

        # Defines the window's initial position
        x = (self.total_screen_width - screen_width) // 2
        y = (self.total_screen_height - screen_height) // 2

        self.geometry(f"{screen_width}x{screen_height}+{x}+{y}")
        self.title("Cris Eletrônicos")
        
        # This canvas plays the role of the "main background"
        self.__canvas_backgrounds['app'] = tk.Canvas(self, width=self.total_screen_width, height=self.total_screen_height)
        self.__canvas_backgrounds['app'].pack(expand=True, fill="both")

    def set_canvas_background_style(self, canvas=None):
        if canvas is None:
            canvas = self.__canvas_backgrounds['app']
        # Iterate through colors and makes a gradient effect (currently from white to light blue)
        int_largura_total_tela = int(self.total_screen_width)
        for x in range(int_largura_total_tela, -1, -1):
            quocient = int_largura_total_tela / 255
            blue = int(x / quocient)
            red = 255 - (255 - blue)
            green = 255 - (130 - int(blue / 2))
            blue = 255
            canvas.create_rectangle(int_largura_total_tela - x, 0, int_largura_total_tela - x + 2, self.total_screen_height, fill=rgb_to_hex(red, green, blue), outline=rgb_to_hex(red, green, blue))

    def set_styles(self):
        self.set_canvas_background_style()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#DDD", foreground="#000", fieldbackground="black", rowheight=25)
        style.map('Treeview', background=[('selected', '#000')])
        style.configure("Treeview.Heading", borderwidth=1, relief="solid", background="#222", foreground="#DDD", fieldbackground="black")
        style.configure("Treeview", borderwidth=0, relief="solid", highlightthickness=0, bordercolor="black", border="2")
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) # adiciona arredondamento

        self.style = style

    def create_table(self):
        table_background = tk.Canvas(self.__canvas_backgrounds['app'])
        table_background.place(relx=0.5, rely=0.5, anchor="center")

        column_config = {
            'standard': { 
                'width': 180,
                'anchor': 'center'
            },
            'col2': { 
                'width': 300,
                'anchor': 'w'
            },
        }

        tree = ttk.Treeview(table_background, columns=tuple([f'col{id + 1}' for id in range(0, len(self.headers) + 1)]), show="headings", style="Treeview")
        tree.column("#0", width=0, stretch="NO")
        for id, header in enumerate(self.headers):
            column_id = f'col{id + 1}'
            config = None
            try:
                config = column_config[column_id]
            except KeyError:
                config = column_config['standard']

            tree.column(column_id, width=config['width'], anchor=config['anchor'])
            tree.heading(column_id, text=header.capitalize())

        for id, customer_data in self.customers.items():
            tree.insert("", tk.END, values=tuple(customer_data.values()))

        tree.pack(fill=BOTH, expand=True)
        
        self.__canvas_backgrounds['table'] = table_background


    def load_customers(self):
        customer_path = self.__file_paths['customers_path']
        try:
            with open(customer_path, 'r') as customers_file:
                self.headers = customers_file.readline().split(';')
                self.customers = {index: {self.headers[index]: data for index, data in enumerate(customer_data.split(';'))} for index, customer_data in enumerate(customers_file.readlines())}
        except FileNotFoundError:
            open(customer_path, 'w')
            self.customers = {}

    def new_window(self, window_name, size='400x200', toplevel=None):
        # Toplevel object which will
        # be treated as a new window
        
        if toplevel is None:
            toplevel = self

        new_window = tk.Toplevel(toplevel)
        new_window.title(window_name)
        new_window.geometry(size)

        self.__windows[window_name] = new_window

    def get_all_entry_widgets_text_content(self)-> dict:
        children_widgets = self.winfo_children()

        entries = {}
        for index, child_widget in enumerate(children_widgets):
            if child_widget.winfo_class() == 'Entry':
                entries[children_widgets[index - 1].cget("text")] = child_widget.get()

        return entries

    def serialize_cliente(self, fields_and_values_dict: dict) -> str:
        serialized_cliente = ';'.join([f'{campo}{valor}' for campo, valor in fields_and_values_dict.items()])

        file_dir = r'C:\clientes'

        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        
        with open(f'{file_dir}\\clientes.txt', 'a+') as cliente_file:
            cliente_file.write(serialized_cliente + '\n')


    def cadastrar(self):
        fields_and_values_dict = self.get_all_entry_widgets_text_content()
        self.serialize_cliente(fields_and_values_dict)

if __name__ == "__main__":
    app = CrisEletronicosAgenda()
    app.mainloop()


