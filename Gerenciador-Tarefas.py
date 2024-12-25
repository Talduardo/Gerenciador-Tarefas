import flet as ft  # Importando o módulo flet
import sqlite3  # Importando o módulo sqlite3

class Gerenciador_de_Tarefas:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.colors.WHITE38
        self.page.window_width = 400
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'Gerenciador de Tarefas'
        self.task = ''
        self.view = 'all'
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks (name, status)')
        self.results = self.db_execute('SELECT * FROM tasks')
        self.delete_task = self.delete_task
        self.main_page()
        # Centralizando a aplicação
        self.page.window_center()
        self.page.update()

    # Criando o banco de dados
    def db_execute(self, query, params=()):
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()

    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label

        if is_checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE name = ?', [label])
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE name = ?', [label])
        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', [self.view])
        self.update_task_list()

    def tasks_container(self):
        height = self.page.height if self.page.height is not None else 0
        return ft.Container(
            height=height * 1.2,  # Altura da tela
            content=ft.Column(
                controls=[
                    ft.Checkbox(
                        label=res[0],
                        on_change=self.checked,  # Função para marcar a tarefa concluída
                        value=True if res[1] == 'complete' else False
                    )
                    for res in self.results if res
                ]
            )
        )

    def set_value(self, e):
        self.task = e.control.value

    def add(self, e, input_task):
        name = self.task
        status = 'incomplete'

        if name:
            self.db_execute('INSERT INTO tasks VALUES (?, ?)', [name, status])
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()

    def update_task_list(self):
        tasks = self.tasks_container()
        if self.page.controls:
            self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()

    def tabs_changed(self, e):
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "incomplete"')
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "complete"')
            self.view = 'complete'
        self.update_task_list()

# Criando função para deletar as tarefas
    def delete_task(self, e):
        self.db_execute('DELETE FROM tasks WHERE name = ?', [e.control.label])
        self.results = self.db_execute('SELECT * FROM tasks')
        self.update_task_list()

    def main_page(self):
        input_task = ft.TextField(
            hint_text="Insira sua tarefa aqui",
            expand=True,
            on_change=self.set_value
        )

        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(
                    icon=ft.icons.ADD,
                    on_click=lambda e: self.add(e, input_task)
                )
            ]
        )
        # Adicionando a barra de navegação do app
        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text='Tarefas'),
                ft.Tab(text='Em andamento'),
                ft.Tab(text='Concluídas')
            ]
        )

        tasks = self.tasks_container()

        self.page.add(input_bar, tabs, tasks)

def main(page: ft.Page):
    Gerenciador_de_Tarefas(page)

ft.app(target=main)  # Inicializando a aplicação
