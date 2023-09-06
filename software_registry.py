import configparser
import os
import sqlite3
import sys
import tkinter.ttk as ttk
from sqlite3 import Error
from tkinter import (
    Entry,
    Frame,
    Label,
    LabelFrame,
    Menu,
    StringVar,
    Tk,
    Toplevel,
    messagebox,
)

from tkcalendar import DateEntry


class SoftwareRegistry:
    '''Реестр программного обеспечения.'''

    def __init__(self, window, datebase_path):
        self.db_path = datebase_path
        self.wind = window
        self.wind.title('Реестр программного обеспечения')
        self.x = self.wind.winfo_screenwidth()
        self.y = self.wind.winfo_screenheight()
        self.wind.geometry(
            '{}x{}'.format(int(self.x * 0.8), int(self.y * 0.8)),
        )
        self.wind.protocol(  # Обработка закрытия приложения
            'WM_DELETE_WINDOW',
            self.on_closing,
        )
        self.notebook = ttk.Notebook(self.wind)  # Создание вкладок
        self.notebook.pack(expand=True, fill='both')
        self.erp_ln_frame = ttk.Frame(self.notebook)
        self.erp_ln_frame.pack(expand=True, fill='both')
        self.notebook.add(self.erp_ln_frame, text='ERP LN')
        self.menu = Menu(self.wind)  # Создание меню
        self.action = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Действие', menu=self.action)
        self.action.add_command(
            command=self.add_software,
            label='Добавить запись',
        )
        self.action.add_command(
            command=self.edit_sofware,
            label='Изменить запись',
        )
        self.action.add_command(
            command=self.delete_sofware,
            label='Удалить запись',
        )
        self.action.add_separator()
        self.action.add_command(
            command=self.history,
            label='Открыть историю',
        )
        self.action.add_separator()
        self.action.add_command(command=self.on_closing, label='Выйти')
        columns_list = [
            'Подсистема',
            'Название сеанса',
            'Код сеанса',
            'Обозначение отчета',
            'Аналитик',
            'Программист',
            'Пользователь',
            'Навигатор',
            'Дата разработки ТЗ',
            'Дата разработки ПО',
            'Примечание',
        ]
        self.tree_erp_ln = ttk.Treeview(  # Таблица ERP LN
            self.erp_ln_frame,
            columns=columns_list,
            show='headings',
        )
        self.tree_erp_ln.grid(column=0, row=0, sticky='nesw')
        self.tree_erp_ln.heading('#0', text='ID', anchor='center')
        self.tree_erp_ln.column('#0', width=50, anchor='center')
        for index, column in enumerate(columns_list, start=1):
            self.tree_erp_ln.heading(f'#{index}', text=column, anchor='center')
            self.tree_erp_ln.column(f'#{index}', anchor='center')
        self.x_scroll_erp_ln = (
            ttk.Scrollbar(  # Добавление горизонтальной полосы прокрутки
                self.erp_ln_frame,
                command=self.tree_erp_ln.xview,
                orient='horizontal',
            )
        )
        self.tree_erp_ln.configure(xscrollcommand=self.x_scroll_erp_ln.set)
        self.x_scroll_erp_ln.grid(column=0, row=1, sticky='we')
        self.y_scroll_erp_ln = (
            ttk.Scrollbar(  # Добавление вертикальной полосы прокрутки
                self.erp_ln_frame,
                command=self.tree_erp_ln.yview,
                orient='vertical',
            )
        )
        self.tree_erp_ln.configure(yscrollcommand=self.y_scroll_erp_ln.set)
        self.y_scroll_erp_ln.grid(column=1, row=0, sticky='ns')
        self.tree_erp_ln.bind('<Double-Button-1>', self.double_click_event)
        self.erp_ln_frame.grid_columnconfigure(0, weight=1)
        self.erp_ln_frame.grid_rowconfigure(0, weight=1)
        self.wind.config(menu=self.menu)
        self.get_data()  # Заполнить таблицу данными

    def history(self):
        '''Открыть историю ПО.'''

        if not self.tree_erp_ln.selection():
            messagebox.showwarning('Внимание', 'Необходимо выбрать запись!')
        else:
            self.window_history(
                development_id=self.tree_erp_ln.item(
                    self.tree_erp_ln.selection(),
                )['text'],
                data=self.tree_erp_ln.item(self.tree_erp_ln.selection())[
                    'values'
                ],
            )

    def window_history(self, development_id, data):
        '''Создание окна истории ПО.'''

        self.history_wind = Toplevel()
        self.history_wind.title('История ПО')
        self.history_wind.protocol(  # Обработка закрытия окна
            'WM_DELETE_WINDOW',
            self.on_closing_history,
        )
        self.history_wind.geometry(
            '{}x{}'.format(int(self.x * 0.45), int(self.y * 0.45)),
        )
        self.development_id = development_id
        padding = {'padx': 10, 'pady': 10}
        session_name = Label(
            self.history_wind,
            text=f'Название сеанса: {data[1]}',
            font=(('Segoe UI'), 12),
            **padding,
        )
        session_name.pack(anchor='w')
        self.history_frame = Frame(self.history_wind)
        self.history_frame.pack(expand=True, fill='both')
        self.history_menu = Menu(self.history_wind)  # Создание меню
        self.history_action = Menu(self.history_menu, tearoff=0)
        self.history_menu.add_cascade(
            label='Действие',
            menu=self.history_action,
        )
        self.history_action.add_command(
            command=self.add_history,
            label='Добавить запись',
        )
        self.history_action.add_command(
            command=self.edit_history,
            label='Изменить запись',
        )
        self.history_action.add_command(
            command=self.delete_history,
            label='Удалить запись',
        )
        self.history_action.add_separator()
        self.history_action.add_command(
            command=self.on_closing_history,
            label='Закрыть историю',
        )
        columns_list_history = [
            'Аналитик',
            'Программист',
            'Дата изменения ПО',
            'Примечание',
        ]
        self.tree_history = ttk.Treeview(  # Таблица истории ПО
            self.history_frame,
            columns=columns_list_history,
            show='headings',
        )
        self.tree_history.grid(column=0, row=0, sticky='nesw')
        self.tree_history.heading('#0', text='ID', anchor='center')
        self.tree_history.column('#0', width=50, anchor='center')
        for index, column in enumerate(columns_list_history, start=1):
            self.tree_history.heading(
                f'#{index}',
                text=column,
                anchor='center',
            )
            self.tree_history.column(f'#{index}', anchor='center')
        self.x_scroll_history = (
            ttk.Scrollbar(  # Добавление горизонтальной полосы прокрутки
                self.history_frame,
                command=self.tree_history.xview,
                orient='horizontal',
            )
        )
        self.tree_history.configure(xscrollcommand=self.x_scroll_history.set)
        self.x_scroll_history.grid(column=0, row=1, sticky='we')
        self.y_scroll_histor = (
            ttk.Scrollbar(  # Добавление вертикальной полосы прокрутки
                self.history_frame,
                command=self.tree_history.yview,
                orient='vertical',
            )
        )
        self.tree_history.configure(yscrollcommand=self.y_scroll_histor.set)
        self.y_scroll_histor.grid(column=1, row=0, sticky='ns')
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(0, weight=1)
        self.history_wind.config(menu=self.history_menu)
        self.get_history(self.development_id)  # Заполнить таблицу данными
        self.history_wind.focus_set()
        self.history_wind.grab_set()
        self.history_wind.mainloop()

    def run_query(self, query, parameters=[]):
        '''Подключение и выполнение запросов к базе данных.'''

        try:
            with sqlite3.connect(self.db_path) as connect:
                cursor = connect.cursor()
                cursor.execute('PRAGMA foreign_keys = ON;')
                result = cursor.execute(query, parameters)
                connect.commit()
            return result
        except Error as err:
            messagebox.showerror('Ошибка', f'Ошибка: {err}')
            self.wind.destroy()

    def get_data(self):
        '''Заполнить таблицу данными ПО.'''

        records = self.tree_erp_ln.get_children()
        for element in records:
            self.tree_erp_ln.delete(element)
        query = '''
            SELECT id,
            subsystem,
            session_name,
            session_code,
            report_name,
            analyst,
            developer,
            client,
            navigator,
            date_technical_specs,
            date_development,
            note
            FROM software_registry_erp_ln AS erp_ln
            '''
        datebase_rows = self.run_query(query)
        for row in datebase_rows:
            self.tree_erp_ln.insert('', 'end', text=row[0], values=row[1:])

    def get_history(self, development_id):
        '''Заполнить таблицу данными истории ПО.'''

        records = self.tree_history.get_children()
        for element in records:
            self.tree_history.delete(element)
        query = '''
            SELECT id,
            analyst,
            developer,
            date_last_change,
            note
            FROM stories
            WHERE development_id = ?
            '''
        datebase_rows = self.run_query(query, [development_id])
        for row in datebase_rows:
            self.tree_history.insert('', 'end', text=row[0], values=row[1:])

    def add_software(self):
        '''Добавить запись ПО.'''

        self.window_add_edit_software(
            title='Добавить запись',
            query=(
                '''
                INSERT INTO software_registry_erp_ln (
                    subsystem,
                    session_name,
                    session_code,
                    report_name,
                    analyst,
                    developer,
                    client,
                    navigator,
                    date_technical_specs,
                    date_development,
                    note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
            ),
            message='добавлена',
        )

    def edit_sofware(self):
        '''Изменить запись ПО.'''

        if not self.tree_erp_ln.selection():
            messagebox.showwarning('Внимание', 'Необходимо выбрать запись!')
        else:
            self.window_add_edit_software(
                title='Изменить запись',
                query=(
                    '''
                    UPDATE software_registry_erp_ln
                    SET subsystem = ?,
                    session_name = ?,
                    session_code = ?,
                    report_name = ?,
                    analyst = ?,
                    developer = ?,
                    client = ?,
                    navigator = ?,
                    date_technical_specs = ?,
                    date_development = ?,
                    note = ?
                    WHERE id = ?
                    '''
                ),
                message='изменена',
                edit=self.tree_erp_ln.item(self.tree_erp_ln.selection())[
                    'text'
                ],
            )

    def delete_sofware(self):
        '''Удалить запись ПО.'''

        if not self.tree_erp_ln.selection():
            messagebox.showwarning('Внимание', 'Необходимо выбрать запись!')
        else:
            if messagebox.askyesno(
                'Подтверждение операции',
                'Вы действительно хотите удалить запись?',
            ):
                id = self.tree_erp_ln.item(self.tree_erp_ln.selection())[
                    'text'
                ]
                query = 'DELETE FROM software_registry_erp_ln WHERE id = ?'
                self.run_query(query, [id])
                messagebox.showinfo('Информация', 'Запись успешно удалена')
                self.get_data()

    def create_a_story(self, parameters=[]):
        '''Создать историю ПО.'''

        query = '''
            INSERT INTO stories (
                development_id,
                analyst,
                developer,
                date_last_change,
                note,
                is_initial
            )
            VALUES (
                (
                    SELECT id
                    FROM software_registry_erp_ln
                    WHERE session_name = ?
                ), ?, ?, ?, ?, 'True'
            )
            '''
        self.run_query(
            query,
            [
                parameters[1],
                parameters[4],
                parameters[5],
                parameters[9],
                parameters[10],
            ],
        )

    def add_history(self):
        '''Добавить запись в историю ПО.'''

        self.window_add_edit_history(
            title='Добавить запись',
            query=(
                '''
                INSERT INTO stories (
                    development_id,
                    analyst,
                    developer,
                    date_last_change,
                    note,
                    is_initial
                )
                VALUES (?, ?, ?, ?, ?, 'False')
                '''
            ),
            message='добавлена',
        )

    def edit_history(self):
        '''Изменить запись в истории ПО.'''

        if not self.tree_history.selection():
            messagebox.showwarning(
                'Внимание',
                'Необходимо выбрать запись!',
                parent=self.history_wind,
            )
        else:
            id = self.tree_history.item(self.tree_history.selection())['text']
            is_initial = self.run_query(
                'SELECT is_initial FROM stories WHERE id = ?',
                [id],
            ).fetchone()[0]
            if is_initial == 'True':
                messagebox.showwarning(
                    'Внимание',
                    'Невозможно изменить исходную запись истории ПО!',
                    parent=self.history_wind,
                )
            else:
                self.window_add_edit_history(
                    title='Изменить запись',
                    query=(
                        '''
                        UPDATE stories
                        SET analyst = ?,
                        developer = ?,
                        date_last_change = ?,
                        note = ?
                        WHERE id = ?
                        '''
                    ),
                    message='изменена',
                    edit=id,
                )

    def delete_history(self):
        '''Удалить запись из истории ПО.'''

        if not self.tree_history.selection():
            messagebox.showwarning(
                'Внимание',
                'Необходимо выбрать запись!',
                parent=self.history_wind,
            )
        else:
            if messagebox.askyesno(
                'Подтверждение операции',
                'Вы действительно хотите удалить запись?',
                parent=self.history_wind,
            ):
                id = self.tree_history.item(self.tree_history.selection())[
                    'text'
                ]
                is_initial = self.run_query(
                    'SELECT is_initial FROM stories WHERE id = ?',
                    [id],
                ).fetchone()[0]
                if is_initial == 'True':
                    messagebox.showwarning(
                        'Внимание',
                        'Невозможно удалить исходную запись истории ПО!',
                        parent=self.history_wind,
                    )
                else:
                    query = 'DELETE FROM stories WHERE id = ?'
                    self.run_query(query, [id])
                    messagebox.showinfo(
                        'Информация',
                        'Запись успешно удалена',
                        parent=self.history_wind,
                    )
                    self.get_history(self.development_id)

    def window_add_edit_software(self, title, query, message, edit=None):
        '''Создание меню для добавления или редактирования записи ПО.'''

        self.add_edit_softrware_wind = Toplevel()
        self.add_edit_softrware_wind.title(title)
        self.add_edit_softrware_wind.protocol(  # Обработка закрытия окна
            'WM_DELETE_WINDOW',
            self.on_closing_window,
        )
        self.add_edit_frame = LabelFrame(self.add_edit_softrware_wind)
        self.button_frame = Frame(self.add_edit_softrware_wind)
        padding = {'padx': 10, 'pady': 10}
        self.add_edit_frame.pack(**padding, expand=True)
        self.button_frame.pack(**padding, expand=True)
        Label(self.add_edit_frame, text='Подсистема:').grid(
            **padding,
            column=0,
            row=0,
            sticky='e',
        )
        subsystem = StringVar()
        Entry(self.add_edit_frame, textvariable=subsystem, width=43).grid(
            **padding,
            column=1,
            row=0,
        )
        Label(self.add_edit_frame, text='Название сеанса:').grid(
            **padding,
            column=0,
            row=1,
            sticky='e',
        )
        session_name = StringVar()
        Entry(self.add_edit_frame, textvariable=session_name, width=43).grid(
            **padding,
            column=1,
            row=1,
        )
        Label(self.add_edit_frame, text='Код сеанса:').grid(
            **padding,
            column=0,
            row=2,
            sticky='e',
        )
        session_code = StringVar()
        Entry(self.add_edit_frame, textvariable=session_code, width=43).grid(
            **padding,
            column=1,
            row=2,
        )
        Label(self.add_edit_frame, text='Обозначение отчета:').grid(
            **padding,
            column=0,
            row=3,
            sticky='e',
        )
        report_name = StringVar()
        Entry(self.add_edit_frame, textvariable=report_name, width=43).grid(
            **padding,
            column=1,
            row=3,
        )
        Label(self.add_edit_frame, text='Аналитик:').grid(
            **padding,
            column=0,
            row=4,
            sticky='e',
        )
        analyst = StringVar()
        Entry(self.add_edit_frame, textvariable=analyst, width=43).grid(
            **padding,
            column=1,
            row=4,
        )
        Label(self.add_edit_frame, text='Программист:').grid(
            **padding,
            column=0,
            row=5,
            sticky='e',
        )
        developer = StringVar()
        Entry(self.add_edit_frame, textvariable=developer, width=43).grid(
            **padding,
            column=1,
            row=5,
        )
        Label(self.add_edit_frame, text='Пользователь:').grid(
            **padding,
            column=0,
            row=6,
            sticky='e',
        )
        client = StringVar()
        Entry(self.add_edit_frame, textvariable=client, width=43).grid(
            **padding,
            column=1,
            row=6,
        )

        Label(self.add_edit_frame, text='Навигатор:').grid(
            **padding,
            column=0,
            row=7,
            sticky='e',
        )
        navigator = StringVar()
        Entry(self.add_edit_frame, textvariable=navigator, width=43).grid(
            **padding,
            column=1,
            row=7,
        )
        Label(self.add_edit_frame, text='Дата разработки ТЗ:').grid(
            **padding,
            column=0,
            row=8,
            sticky='e',
        )
        date_technical_specs = StringVar()
        DateEntry(
            self.add_edit_frame,
            textvariable=date_technical_specs,
            width=40,
        ).grid(**padding, column=1, row=8)
        Label(self.add_edit_frame, text='Дата разработки ПО:').grid(
            **padding,
            column=0,
            row=9,
            sticky='e',
        )
        date_development = StringVar()
        DateEntry(
            self.add_edit_frame,
            textvariable=date_development,
            width=40,
        ).grid(**padding, column=1, row=9)
        Label(self.add_edit_frame, text='Примечание:').grid(
            **padding,
            column=0,
            row=10,
            sticky='e',
        )
        note = StringVar()
        Entry(self.add_edit_frame, textvariable=note, width=43).grid(
            **padding,
            column=1,
            row=10,
        )
        if edit is not None:
            data_list = self.tree_erp_ln.item(self.tree_erp_ln.selection())[
                'values'
            ]
            subsystem.set(data_list[0])
            session_name.set(data_list[1])
            session_code.set(data_list[2])
            report_name.set(data_list[3])
            analyst.set(data_list[4])
            developer.set(data_list[5])
            client.set(data_list[6])
            navigator.set(data_list[7])
            date_technical_specs.set(data_list[8])
            date_development.set(data_list[9])
            note.set(data_list[10])
        ttk.Button(
            self.button_frame,
            command=lambda: self.run_add_edit_software(
                query,
                message,
                edit=edit,
                parameters=[
                    subsystem.get(),
                    session_name.get(),
                    session_code.get(),
                    report_name.get(),
                    analyst.get(),
                    developer.get(),
                    client.get(),
                    navigator.get(),
                    date_technical_specs.get(),
                    date_development.get(),
                    note.get(),
                ],
            ),
            text='Сохранить',
            width=20,
        ).grid(padx=40, column=0, row=0)
        ttk.Button(
            self.button_frame,
            command=self.on_closing_window,
            text='Отмена',
            width=20,
        ).grid(padx=40, column=1, row=0)
        self.add_edit_softrware_wind.focus_set()
        self.add_edit_softrware_wind.grab_set()
        self.add_edit_softrware_wind.mainloop()

    def window_add_edit_history(self, title, query, message, edit=None):
        '''Создание меню для добавления или редактирования истории ПО.'''

        self.add_edit_history_wind = Toplevel()
        self.add_edit_history_wind.title(title)
        self.add_edit_history_wind.protocol(  # Обработка закрытия окна
            'WM_DELETE_WINDOW',
            self.on_closing_add_edit_history,
        )
        self.add_edit_history_frame = LabelFrame(self.add_edit_history_wind)
        self.button_history_frame = Frame(self.add_edit_history_wind)
        padding = {'padx': 10, 'pady': 10}
        self.add_edit_history_frame.pack(**padding, expand=True)
        self.button_history_frame.pack(**padding, expand=True)
        Label(self.add_edit_history_frame, text='Аналитик:').grid(
            **padding,
            column=0,
            row=0,
            sticky='e',
        )
        analyst = StringVar()
        Entry(
            self.add_edit_history_frame,
            textvariable=analyst,
            width=43,
        ).grid(**padding, column=1, row=0)
        Label(self.add_edit_history_frame, text='Программист:').grid(
            **padding,
            column=0,
            row=1,
            sticky='e',
        )
        developer = StringVar()
        Entry(
            self.add_edit_history_frame,
            textvariable=developer,
            width=43,
        ).grid(**padding, column=1, row=1)
        Label(self.add_edit_history_frame, text='Дата изменения ПО:').grid(
            **padding,
            column=0,
            row=2,
            sticky='e',
        )
        date_last_change = StringVar()
        DateEntry(
            self.add_edit_history_frame,
            textvariable=date_last_change,
            width=40,
        ).grid(**padding, column=1, row=2)
        Label(self.add_edit_history_frame, text='Примечание:').grid(
            **padding,
            column=0,
            row=3,
            sticky='e',
        )
        note = StringVar()
        Entry(self.add_edit_history_frame, textvariable=note, width=43).grid(
            **padding,
            column=1,
            row=3,
        )
        if edit is not None:
            data_list = self.tree_history.item(self.tree_history.selection())[
                'values'
            ]
            analyst.set(data_list[0])
            developer.set(data_list[1])
            date_last_change.set(data_list[2])
            note.set(data_list[3])
        ttk.Button(
            self.button_history_frame,
            command=lambda: self.run_add_edit_history(
                query,
                message,
                edit=edit,
                parameters=[
                    analyst.get(),
                    developer.get(),
                    date_last_change.get(),
                    note.get(),
                ],
            ),
            text='Сохранить',
            width=20,
        ).grid(padx=40, column=0, row=0)
        ttk.Button(
            self.button_history_frame,
            command=self.on_closing_add_edit_history,
            text='Отмена',
            width=20,
        ).grid(padx=40, column=1, row=0)
        self.add_edit_history_wind.focus_set()
        self.add_edit_history_wind.grab_set()
        self.add_edit_history_wind.mainloop()

    def run_add_edit_software(self, query, message, edit, parameters=[]):
        '''Добавление или редактирование записи ПО.'''

        if edit is not None:
            parameters.append(edit)
            self.run_query(
                '''
                UPDATE stories
                SET analyst = ?,
                developer = ?,
                date_last_change = ?,
                note = ?
                WHERE development_id = ?
                AND is_initial = 'True'
                ''',
                [
                    parameters[4],
                    parameters[5],
                    parameters[9],
                    parameters[10],
                    parameters[11],
                ],
            )
        self.run_query(query, parameters)
        if edit is None:
            self.create_a_story(parameters)
        messagebox.showinfo(
            'Информация',
            f'Запись успешно {message}!',
            parent=self.add_edit_softrware_wind,
        )
        self.get_data()
        self.add_edit_softrware_wind.grab_release()
        self.add_edit_softrware_wind.destroy()

    def run_add_edit_history(self, query, message, edit, parameters=[]):
        '''Добавление или редактирование записи истории ПО.'''

        if edit is not None:
            parameters.append(edit)
        else:
            parameters.insert(0, self.development_id)
        self.run_query(query, parameters)
        messagebox.showinfo(
            'Информация',
            f'Запись успешно {message}!',
            parent=self.add_edit_history_wind,
        )
        self.get_history(self.development_id)
        self.add_edit_history_wind.grab_release()
        self.add_edit_history_wind.destroy()

    def on_closing(self):
        '''Обработка закрытия программы.'''

        if messagebox.askyesno('Подтверждение операции', 'Закрыть программу?'):
            self.wind.destroy()

    def on_closing_window(self):
        '''Обработка закрытия окна добавления или редактирования ПО.'''

        if messagebox.askyesno(
            'Подтверждение операции',
            'Закрыть окно?',
            parent=self.add_edit_softrware_wind,
        ):
            self.add_edit_softrware_wind.grab_release()
            self.add_edit_softrware_wind.destroy()

    def on_closing_history(self):
        '''Обработка закрытия окна истории ПО.'''

        self.history_wind.grab_release()
        self.history_wind.destroy()

    def on_closing_add_edit_history(self):
        '''Обработка закрытия окна добавления или редактирования истории ПО.'''

        if messagebox.askyesno(
            'Подтверждение операции',
            'Закрыть окно?',
            parent=self.add_edit_history_wind,
        ):
            self.add_edit_history_wind.grab_release()
            self.add_edit_history_wind.destroy()

    def double_click_event(self, event):
        if self.tree_erp_ln.selection():
            self.history()


if __name__ == '__main__':
    if not os.path.exists('settings.ini'):
        root = Tk()
        root.withdraw()
        messagebox.showerror('Ошибка', 'Упс, отсутствует файл settings.ini!')
        root.destroy()
        sys.exit()
    config = configparser.ConfigParser()
    try:
        config.read('settings.ini')
        icon_path = config['DEFAULT']['icon_path']
        datebase_path = config['DEFAULT']['datebase_path']
    except KeyError as err:
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            'Ошибка',
            'Упс, файл settings.ini содержит некорректные данные! '
            f'Отсутствует переменная: {err}.',
        )
        root.destroy()
        sys.exit()
    if not os.path.exists(datebase_path):
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            'Ошибка',
            f'Упс, отсутствует файл базы данных: {datebase_path}!',
        )
        root.destroy()
        sys.exit()
    software_registry_window = Tk()
    if os.path.exists(icon_path):
        software_registry_window.iconbitmap(icon_path)
    application = SoftwareRegistry(software_registry_window, datebase_path)
    software_registry_window.mainloop()
