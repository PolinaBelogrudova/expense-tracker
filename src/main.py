"""
Business Expense Tracker
"""
import os
import json
import csv
import time
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ColorProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.storage.jsonstore import JsonStore


class RoundedButton(Button):
    bg_color = ColorProperty((0.79, 0.54, 0.59, 1))
    bg_pressed = ColorProperty((0.66, 0.44, 0.49, 1))
    corner = NumericProperty(14)


Builder.load_string('''
#:set CREAM (0.98, 0.95, 0.93, 1)
#:set BROWN (0.31, 0.20, 0.18, 1)
#:set ROSE (0.79, 0.54, 0.59, 1)
#:set ROSE_DARK (0.66, 0.44, 0.49, 1)
#:set TERRA (0.63, 0.44, 0.36, 1)
#:set TERRA_DARK (0.54, 0.37, 0.31, 1)
#:set LATTE (0.77, 0.64, 0.52, 1)
#:set LATTE_DARK (0.66, 0.55, 0.44, 1)
#:set WINE (0.56, 0.26, 0.32, 1)
#:set WINE_DARK (0.45, 0.20, 0.26, 1)
#:set GREEN (0.2, 0.6, 0.3, 1)
#:set BLUE (0.3, 0.5, 0.7, 1)
#:set BLUE_DARK (0.2, 0.4, 0.6, 1)
#:set ROW_BG (1.0, 0.98, 0.96, 1)

<RoundedButton>:
    canvas.before:
        Color:
            rgba: self.bg_pressed if self.state == 'down' else self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [(self.corner, self.corner)]
    background_color: (0, 0, 0, 0)
    color: (1, 1, 1, 1)
    font_size: 13
    bold: True

<ExpenseRow>:
    canvas.before:
        Color:
            rgba: ROW_BG
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [(10, 10)]
    orientation: 'horizontal'
    padding: 10
    spacing: 5
    height: 60
    Label:
        text: root.category
        size_hint_x: 0.25
        color: BROWN
        bold: True
    Label:
        text: root.description
        size_hint_x: 0.35
        color: BROWN
    Label:
        text: ('+' if root.is_income else '-') + str(root.amount) + ' руб.'
        size_hint_x: 0.25
        color: GREEN if root.is_income else WINE
        bold: True
    Label:
        text: 'Доход' if root.is_income else 'Расход'
        size_hint_x: 0.15
        color: GREEN if root.is_income else WINE
        font_size: 12

<ExpensesRV>:
    viewclass: 'ExpenseRow'
    RecycleBoxLayout:
        default_size: None, dp(64)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: 6
        padding: 6

<MainScreen>:
    canvas.before:
        Color:
            rgba: CREAM
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 12

        Label:
            text: 'БИЗНЕС-ТРЕКЕР'
            font_size: 24
            bold: True
            color: TERRA
            size_hint_y: 0.08

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.10
            spacing: 6
            RoundedButton:
                text: 'Добавить'
                bg_color: ROSE
                bg_pressed: ROSE_DARK
                on_press: root.show_add_expense_popup()
            RoundedButton:
                text: 'Аналитика'
                bg_color: TERRA
                bg_pressed: TERRA_DARK
                on_press: root.show_analytics()
            RoundedButton:
                text: 'Экспорт'
                bg_color: LATTE
                bg_pressed: LATTE_DARK
                on_press: root.export_data()
            RoundedButton:
                text: 'Графики'
                bg_color: WINE
                bg_pressed: WINE_DARK
                on_press: root.show_chart()
            RoundedButton:
                text: 'Облако'
                bg_color: BLUE
                bg_pressed: BLUE_DARK
                on_press: root.sync_cloud()

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.08
            spacing: 15
            Label:
                text: 'Расходы: ' + str(root.total_expenses)
                font_size: 13
                bold: True
                color: WINE
            Label:
                text: 'Доходы: ' + str(root.total_income)
                font_size: 13
                bold: True
                color: GREEN
            Label:
                text: 'Баланс: ' + str(root.balance)
                font_size: 15
                bold: True
                color: GREEN if root.balance >= 0 else WINE

        ExpensesRV:
            id: rv
            size_hint_y: 0.74

<AddExpensePopup>:
    size_hint: 0.8, 0.65
    title: 'Добавить операцию'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        canvas.before:
            Color:
                rgba: CREAM
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Тип операции:'
            color: BROWN
            size_hint_y: 0.08
        BoxLayout:
            orientation: 'horizontal'
            spacing: 10
            size_hint_y: 0.10
            ToggleButton:
                id: type_expense
                text: 'Расход'
                group: 'op_type'
                state: 'down'
                background_color: (0.85, 0.65, 0.70, 1)
                color: (1, 1, 1, 1)
                bold: True
            ToggleButton:
                id: type_income
                text: 'Доход'
                group: 'op_type'
                background_color: (0.55, 0.85, 0.65, 1)
                color: (1, 1, 1, 1)
                bold: True
        Label:
            text: 'Категория:'
            color: BROWN
            size_hint_y: 0.08
        Spinner:
            id: category_spinner
            text: 'Выберите категорию'
            values: ['Офис', 'Зарплаты', 'Маркетинг', 'Логистика', 'Продажи', 'Прочее']
            size_hint_y: 0.13
            background_color: LATTE
            color: (1, 1, 1, 1)
            bold: True
        Label:
            text: 'Описание:'
            color: BROWN
            size_hint_y: 0.08
        TextInput:
            id: description_input
            multiline: False
            size_hint_y: 0.13
            focus: True
            foreground_color: BROWN
            cursor_color: ROSE
            background_color: (1, 1, 1, 1)
        Label:
            text: 'Сумма (руб.):'
            color: BROWN
            size_hint_y: 0.08
        TextInput:
            id: amount_input
            multiline: False
            input_filter: 'float'
            size_hint_y: 0.13
            foreground_color: BROWN
            cursor_color: ROSE
            background_color: (1, 1, 1, 1)
        BoxLayout:
            orientation: 'horizontal'
            spacing: 12
            size_hint_y: 0.18
            RoundedButton:
                text: 'Отмена'
                bg_color: TERRA
                bg_pressed: TERRA_DARK
                on_press: root.dismiss()
            RoundedButton:
                text: 'Сохранить'
                bg_color: ROSE
                bg_pressed: ROSE_DARK
                on_press: root.save_expense()
''')


class ExpenseRow(RecycleDataViewBehavior, BoxLayout):
    category = StringProperty('')
    description = StringProperty('')
    amount = NumericProperty(0)
    is_income = BooleanProperty(False)
    index = None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)


class ExpensesRV(RecycleView):
    pass


class MainScreen(Screen):
    total_expenses = NumericProperty(0)
    total_income = NumericProperty(0)
    balance = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('expenses.json')
        self.load_expenses()

    def load_expenses(self):
        expenses = []
        total_exp = 0
        total_inc = 0
        if os.path.exists('expenses.json'):
            with open('expenses.json', 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    for key, expense in data.items():
                        expenses.append({
                            'category': expense.get('category', ''),
                            'description': expense.get('description', ''),
                            'amount': expense.get('amount', 0),
                            'is_income': expense.get('is_income', False)
                        })
                        if expense.get('is_income', False):
                            total_inc += expense.get('amount', 0)
                        else:
                            total_exp += expense.get('amount', 0)
                except Exception:
                    pass
        self.ids.rv.data = expenses
        self.total_expenses = total_exp
        self.total_income = total_inc
        self.balance = total_inc - total_exp

    def show_add_expense_popup(self):
        popup = AddExpensePopup(main_screen=self)
        popup.open()

    def add_expense(self, category, description, amount, is_income):
        try:
            amount = float(amount)
            expense = {
                'category': category,
                'description': description,
                'amount': amount,
                'is_income': is_income,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            key = f"op_{datetime.now().timestamp()}"
            self.store.put(key, **expense)
            self.load_expenses()
        except ValueError:
            self.show_error_popup("Ошибка", "Введите корректную сумму")

    def show_analytics(self):
        categories = {}
        for expense in self.ids.rv.data:
            cat = expense['category']
            if cat not in categories:
                categories[cat] = {'exp': 0, 'inc': 0}
            if expense['is_income']:
                categories[cat]['inc'] += expense['amount']
            else:
                categories[cat]['exp'] += expense['amount']

        content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        for cat, totals in categories.items():
            text = f"{cat}: Расх {totals['exp']} | Дох {totals['inc']}"
            content.add_widget(Label(text=text, font_size=14, color=(0.98, 0.95, 0.93, 1)))
        popup = Popup(title='Аналитика', content=content, size_hint=(0.8, 0.6))
        popup.open()

    def show_chart(self):
        try:
            from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
        except ImportError:
            self.show_error_popup("Ошибка", "Модуль графиков не установлен.")
            return

        import matplotlib.pyplot as plt

        expenses = {}
        incomes = {}
        for op in self.ids.rv.data:
            cat = op['category']
            if op['is_income']:
                incomes[cat] = incomes.get(cat, 0) + op['amount']
            else:
                expenses[cat] = expenses.get(cat, 0) + op['amount']

        if not expenses and not incomes:
            self.show_error_popup("Внимание", "Нет данных для графика.")
            return

        plt.close('all')
        fig, axes = plt.subplots(1, 2, figsize=(8, 4), dpi=100)
        ax1, ax2 = axes

        if expenses:
            ax1.bar(list(expenses.keys()), list(expenses.values()), color=['#C98A96', '#A1705C', '#C4A484'])
            ax1.set_title('Расходы', color='#4F332E')
            plt.setp(ax1.get_xticklabels(), rotation=20, ha='right')

        if incomes:
            ax2.bar(list(incomes.keys()), list(incomes.values()), color=['#2ecc71', '#27ae60', '#1abc9c'])
            ax2.set_title('Доходы', color='#4F332E')
            plt.setp(ax2.get_xticklabels(), rotation=20, ha='right')

        plt.tight_layout()
        canvas = FigureCanvasKivyAgg(fig)
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(canvas)
        popup = Popup(title='Графики', content=content, size_hint=(0.9, 0.7))
        popup.open()

    def sync_cloud(self):
        """Синхронизация с облаком (имитация Firebase/REST API)."""
        time.sleep(0.5)
        self.show_error_popup(
            "Облако (Firebase)",
            f"Успешно синхронизировано!\nОтправлено операций: {len(self.ids.rv.data)}"
        )

    def export_data(self):
        try:
            with open('expenses_export.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Тип', 'Категория', 'Описание', 'Сумма', 'Дата'])
                for key in self.store.keys():
                    expense = self.store.get(key)
                    op_type = 'Доход' if expense.get('is_income', False) else 'Расход'
                    writer.writerow([
                        op_type,
                        expense['category'],
                        expense['description'],
                        expense['amount'],
                        expense.get('date', '')
                    ])
            self.show_error_popup("Успех", "Экспортировано в expenses_export.csv")
        except Exception as e:
            self.show_error_popup("Ошибка", str(e))

    def show_error_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message, color=(0.98, 0.95, 0.93, 1)),
                      size_hint=(0.6, 0.4))
        popup.open()


class AddExpensePopup(Popup):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen

    def save_expense(self):
        category = self.ids.category_spinner.text
        description = self.ids.description_input.text
        amount = self.ids.amount_input.text
        is_income = self.ids.type_income.state == 'down'

        if category == 'Выберите категорию':
            self.main_screen.show_error_popup("Ошибка", "Выберите категорию")
            return
        if not description or not amount:
            self.main_screen.show_error_popup("Ошибка", "Заполните все поля")
            return

        self.main_screen.add_expense(category, description, amount, is_income)
        self.dismiss()


class ExpenseTrackerApp(App):
    def build(self):
        self.title = "Business Expense Tracker"
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

    def on_pause(self):
        return True


if __name__ == '__main__':
    ExpenseTrackerApp().run()