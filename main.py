import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup

# Caminho para o banco de dados
db_path = 'armazem_bd.db'

class DatabaseApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Conexão ao banco de dados
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Obter lista de tabelas
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        self.tables = [row[0] for row in self.cursor.fetchall()]

        # Spinner para escolher a tabela
        self.table_spinner = Spinner(
            text="Tipo de Acessório",
            values=self.tables,
            size_hint=(1, 0.2)
        )
        self.table_spinner.bind(text=self.on_table_selected)
        self.layout.add_widget(self.table_spinner)

        # Layout onde os campos para inserção de dados serão gerados
        self.fields_layout = BoxLayout(orientation='vertical', spacing=10)
        self.layout.add_widget(self.fields_layout)

        # Botão para inserir dados
        self.submit_button = Button(
            text="Inserir Dados",
            size_hint=(1, 0.2)
        )
        self.submit_button.bind(on_press=self.insert_data)
        self.layout.add_widget(self.submit_button)

        return self.layout

    def on_table_selected(self, spinner, text):
        # Limpa o layout de campos quando uma nova tabela é selecionada
        self.fields_layout.clear_widgets()

        # Obter colunas da tabela selecionada
        self.cursor.execute(f"PRAGMA table_info({text})")
        self.columns = [col[1] for col in self.cursor.fetchall()]

        # Criar campos de entrada baseados nas colunas da tabela
        self.inputs = {}
        for column in self.columns:
            label = Label(text=column, size_hint=(1, 0.1))
            text_input = TextInput(size_hint=(1, 0.1))
            self.fields_layout.add_widget(label)
            self.fields_layout.add_widget(text_input)
            self.inputs[column] = text_input

    def insert_data(self, instance):
        # Obter os valores inseridos pelo usuário
        table_name = self.table_spinner.text
        if table_name == "Tipo de Acessório":
            self.show_popup("Erro", "Por favor, selecione um acessório")
            return

        values = [self.inputs[column].text for column in self.columns]

        # Gerar a query para inserir dados
        placeholders = ', '.join('?' * len(self.columns))
        query = f"INSERT INTO {table_name} ({', '.join(self.columns)}) VALUES ({placeholders})"

        try:
            # Executar a query de inserção
            self.cursor.execute(query, values)
            self.conn.commit()
            self.show_popup("Sucesso", "Dados inseridos com sucesso.")
            # Limpar os campos após a inserção
            for text_input in self.inputs.values():
                text_input.text = ""
        except sqlite3.Error as e:
            self.show_popup("Erro", str(e))

    def show_popup(self, title, message):
        # Exibir um popup com mensagem de sucesso ou erro
        popup_layout = BoxLayout(orientation='vertical', padding=10)
        popup_label = Label(text=message)
        close_button = Button(text="Fechar", size_hint=(1, 0.2))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)
        popup = Popup(title=title, content=popup_layout, size_hint=(0.7, 0.7))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def on_stop(self):
        # Fechar a conexão com o banco de dados ao encerrar o aplicativo
        self.conn.close()

if __name__ == '__main__':
    DatabaseApp().run()
