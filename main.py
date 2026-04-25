python
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Личная кинотека")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Файл для хранения фильмов
        self.movies_file = "movies.json"
        self.movies = self.load_movies()
        
        # Список жанров для выпадающего списка
        self.genres = ["Боевик", "Комедия", "Драма", "Ужасы", "Фантастика", 
                       "Триллер", "Мелодрама", "Детектив", "Приключения", 
                       "Анимация", "Документальный", "Криминал", "Вестерн"]
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Отображение всех фильмов при запуске
        self.display_movies()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главный контейнер
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_label = tk.Label(main_frame, text="🎬 Movie Library - Личная кинотека", 
                               font=("Segoe UI", 20, "bold"), fg="#2c3e50")
        title_label.pack(pady=(0, 15))
        
        # === Форма добавления фильма ===
        form_frame = tk.LabelFrame(main_frame, text="➕ Добавление нового фильма", 
                                   font=("Segoe UI", 12, "bold"), padx=15, pady=15)
        form_frame.pack(fill="x", pady=(0, 15))
        
        # Поля ввода
        fields_frame = tk.Frame(form_frame)
        fields_frame.pack(fill="x")
        
        # Название
        tk.Label(fields_frame, text="Название:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), width=25)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Жанр (выпадающий список)
        tk.Label(fields_frame, text="Жанр:", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.genre_combo = ttk.Combobox(fields_frame, values=self.genres, font=("Segoe UI", 11), width=15)
        self.genre_combo.grid(row=0, column=3, padx=5, pady=5)
        self.genre_combo.set("Выберите жанр")
        
        # Год выпуска
        tk.Label(fields_frame, text="Год выпуска:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.year_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), width=25)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Рейтинг
        tk.Label(fields_frame, text="Рейтинг (0-10):", font=("Segoe UI", 10, "bold")).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.rating_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), width=25)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        button_frame = tk.Frame(form_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.add_button = tk.Button(button_frame, text="➕ Добавить фильм", 
                                    command=self.add_movie,
                                    bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                                    padx=20, pady=8, cursor="hand2", relief="flat")
        self.add_button.pack()
        
        # === Панель фильтрации ===
        filter_frame = tk.LabelFrame(main_frame, text="🔍 Фильтрация фильмов", 
                                     font=("Segoe UI", 12, "bold"), padx=15, pady=10)
        filter_frame.pack(fill="x", pady=(0, 15))
        
        filter_inner = tk.Frame(filter_frame)
        filter_inner.pack(fill="x")
        
        # Фильтр по жанру
        tk.Label(filter_inner, text="Жанр:", font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.filter_genre_combo = ttk.Combobox(filter_inner, values=["Все"] + self.genres, 
                                               font=("Segoe UI", 10), width=15)
        self.filter_genre_combo.pack(side="left", padx=5)
        self.filter_genre_combo.set("Все")
        
        # Фильтр по году
        tk.Label(filter_inner, text="Год:", font=("Segoe UI", 10)).pack(side="left", padx=(20, 5))
        self.filter_year_entry = tk.Entry(filter_inner, font=("Segoe UI", 10), width=10)
        self.filter_year_entry.pack(side="left", padx=5)
        
        # Кнопка применения фильтров
        self.filter_button = tk.Button(filter_inner, text="🔍 Применить фильтр", 
                                       command=self.apply_filter,
                                       bg="#3498db", fg="white", font=("Segoe UI", 10),
                                       padx=15, pady=5, cursor="hand2", relief="flat")
        self.filter_button.pack(side="left", padx=(20, 5))
        
        # Кнопка сброса фильтров
        self.reset_button = tk.Button(filter_inner, text="🔄 Сбросить фильтр", 
                                      command=self.reset_filter,
                                      bg="#95a5a6", fg="white", font=("Segoe UI", 10),
                                      padx=15, pady=5, cursor="hand2", relief="flat")
        self.reset_button.pack(side="left", padx=5)
        
        # === Таблица с фильмами ===
        table_frame = tk.LabelFrame(main_frame, text="📋 Список фильмов", 
                                    font=("Segoe UI", 12, "bold"), padx=10, pady=10)
        table_frame.pack(fill="both", expand=True)
        
        # Создание таблицы
        columns = ("ID", "Название", "Жанр", "Год", "Рейтинг")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Настройка колонок
        self.tree.heading("ID", text="№")
        self.tree.heading("Название", text="🎬 Название")
        self.tree.heading("Жанр", text="🎭 Жанр")
        self.tree.heading("Год", text="📅 Год")
        self.tree.heading("Рейтинг", text="⭐ Рейтинг")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Название", width=300)
        self.tree.column("Жанр", width=150, anchor="center")
        self.tree.column("Год", width=100, anchor="center")
        self.tree.column("Рейтинг", width=100, anchor="center")
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.pack(side="top", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Кнопки управления
        control_frame = tk.Frame(table_frame)
        control_frame.pack(fill="x", pady=(10, 0))
        
        self.delete_button = tk.Button(control_frame, text="🗑️ Удалить выбранный фильм", 
                                       command=self.delete_movie,
                                       bg="#e74c3c", fg="white", font=("Segoe UI", 10),
                                       padx=15, pady=5, cursor="hand2", relief="flat")
        self.delete_button.pack(side="left", padx=5)
        
        self.edit_button = tk.Button(control_frame, text="✏️ Редактировать выбранный", 
                                     command=self.edit_movie,
                                     bg="#f39c12", fg="white", font=("Segoe UI", 10),
                                     padx=15, pady=5, cursor="hand2", relief="flat")
        self.edit_button.pack(side="left", padx=5)
        
        # Статистика
        self.stats_label = tk.Label(main_frame, text="", font=("Segoe UI", 10), fg="#7f8c8d")
        self.stats_label.pack(fill="x", pady=(10, 0))
        
        # Статус бар
        self.status_bar = tk.Label(main_frame, text="✅ Готов к работе", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   font=("Segoe UI", 9), fg="#555")
        self.status_bar.pack(fill="x", pady=(10, 0))
        
        # Обновление статистики
        self.update_stats()
    
    def load_movies(self):
        """Загрузка фильмов из JSON файла"""
        if os.path.exists(self.movies_file):
            try:
                with open(self.movies_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_movies(self):
        """Сохранение фильмов в JSON файл"""
        with open(self.movies_file, 'w', encoding='utf-8') as f:
            json.dump(self.movies, f, indent=2, ensure_ascii=False)
    
    def add_movie(self):
        """Добавление нового фильма"""
        # Получение данных из полей
        title = self.title_entry.get().strip()
        genre = self.genre_combo.get()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()
        
        # Проверка названия
        if not title:
            messagebox.showwarning("Ошибка ввода", "Введите название фильма!")
            return
        
        # Проверка жанра
        if genre not in self.genres:
            messagebox.showwarning("Ошибка ввода", "Выберите корректный жанр!")
            return
        
        # Проверка года
        if not year:
            messagebox.showwarning("Ошибка ввода", "Введите год выпуска!")
            return
        
        try:
            year_int = int(year)
            current_year = datetime.now().year
            if year_int < 1888 or year_int > current_year:
                messagebox.showwarning("Ошибка ввода", f"Год должен быть от 1888 до {current_year}!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Год должен быть числом!")
            return
        
        # Проверка рейтинга
        if not rating:
            messagebox.showwarning("Ошибка ввода", "Введите рейтинг!")
            return
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                messagebox.showwarning("Ошибка ввода", "Рейтинг должен быть от 0 до 10!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Рейтинг должен быть числом!")
            return
        
        # Создание записи о фильме
        movie = {
            "id": len(self.movies) + 1 if self.movies else 1,
            "title": title,
            "genre": genre,
            "year": year_int,
            "rating": rating_float
        }
        
        # Добавление в список
        self.movies.append(movie)
        self.save_movies()
        
        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.genre_combo.set("Выберите жанр")
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        
        # Обновление отображения
        self.display_movies()
        self.update_stats()
        self.status_bar.config(text=f"✅ Фильм '{title}' успешно добавлен!")
        
        messagebox.showinfo("Успех", f"Фильм '{title}' добавлен в библиотеку!")
    
    def display_movies(self, movies_list=None):
        """Отображение фильмов в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Если список не передан, используем все фильмы
        if movies_list is None:
            movies_list = self.movies
        
        # Добавление фильмов в таблицу
        for movie in movies_list:
            # Форматирование рейтинга
            rating_display = f"{movie['rating']:.1f}" if isinstance(movie['rating'], float) else str(movie['rating'])
            # Звёздочки для рейтинга
            stars = "⭐" * int(movie['rating'] // 2) + "☆" * (5 - int(movie['rating'] // 2))
            
            self.tree.insert("", "end", values=(
                movie['id'],
                movie['title'],
                movie['genre'],
                movie['year'],
                f"{rating_display} {stars}"
            ))
    
    def apply_filter(self):
        """Применение фильтрации"""
        selected_genre = self.filter_genre_combo.get()
        filter_year = self.filter_year_entry.get().strip()
        
        filtered_movies = self.movies.copy()
        
        # Фильтрация по жанру
        if selected_genre != "Все":
            filtered_movies = [m for m in filtered_movies if m['genre'] == selected_genre]
        
        # Фильтрация по году
        if filter_year:
            try:
                year_int = int(filter_year)
                filtered_movies = [m for m in filtered_movies if m['year'] == year_int]
            except ValueError:
                messagebox.showwarning("Ошибка", "Введите корректный год для фильтрации!")
                return
        
        self.display_movies(filtered_movies)
        self.status_bar.config(text=f"🔍 Найдено фильмов: {len(filtered_movies)}")
        
        if len(filtered_movies) == 0:
            messagebox.showinfo("Результат", "Фильмы не найдены!")
    
    def reset_filter(self):
        """Сброс фильтрации"""
        self.filter_genre_combo.set("Все")
        self.filter_year_entry.delete(0, tk.END)
        self.display_movies()
        self.update_stats()
        self.status_bar.config(text="🔄 Фильтр сброшен")
    
    def delete_movie(self):
        """Удаление выбранного фильма"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
            return
        
        # Получение ID фильма
        item = self.tree.item(selection[0])
        movie_id = int(item['values'][0])
        
        # Поиск фильма по ID
        movie_to_delete = None
        for movie in self.movies:
            if movie['id'] == movie_id:
                movie_to_delete = movie
                break
        
        if movie_to_delete:
            if messagebox.askyesno("Подтверждение", f"Удалить фильм '{movie_to_delete['title']}'?"):
                self.movies = [m for m in self.movies if m['id'] != movie_id]
                # Перенумерация ID
                for i, movie in enumerate(self.movies):
                    movie['id'] = i + 1
                self.save_movies()
                self.display_movies()
                self.update_stats()
                self.status_bar.config(text=f"🗑️ Фильм '{movie_to_delete['title']}' удалён")
                messagebox.showinfo("Успех", "Фильм удалён!")
    
    def edit_movie(self):
        """Редактирование выбранного фильма"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите фильм для редактирования!")
            return
        
        # Получение ID фильма
        item = self.tree.item(selection[0])
        movie_id = int(item['values'][0])
        
        # Поиск фильма
        movie = None
        for m in self.movies:
            if m['id'] == movie_id:
                movie = m
                break
        
        if movie:
            self.open_edit_window(movie)
    
    def open_edit_window(self, movie):
        """Окно редактирования фильма"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Редактирование: {movie['title']}")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        
        # Центрирование окна
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Поля редактирования
        tk.Label(edit_window, text="Редактирование фильма", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        frame = tk.Frame(edit_window, padx=20, pady=10)
        frame.pack(fill="both", expand=True)
        
        # Название
        tk.Label(frame, text="Название:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        title_entry = tk.Entry(frame, font=("Segoe UI", 11), width=30)
        title_entry.insert(0, movie['title'])
        title_entry.grid(row=0, column=1, pady=5)
        
        # Жанр
        tk.Label(frame, text="Жанр:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        genre_combo = ttk.Combobox(frame, values=self.genres, font=("Segoe UI", 11), width=27)
        genre_combo.set(movie['genre'])
        genre_combo.grid(row=1, column=1, pady=5)
        
        # Год
        tk.Label(frame, text="Год выпуска:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        year_entry = tk.Entry(frame, font=("Segoe UI", 11), width=30)
        year_entry.insert(0, str(movie['year']))
        year_entry.grid(row=2, column=1, pady=5)
        
        # Рейтинг
        tk.Label(frame, text="Рейтинг (0-10):", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        rating_entry = tk.Entry(frame, font=("Segoe UI", 11), width=30)
        rating_entry.insert(0, str(movie['rating']))
        rating_entry.grid(row=3, column=1, pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(edit_window)
        btn_frame.pack(pady=20)
        
        def save_changes():
            # Валидация
            new_title = title_entry.get().strip()
            new_genre = genre_combo.get()
            new_year = year_entry.get().strip()
            new_rating = rating_entry.get().strip()
            
            if not new_title:
                messagebox.showwarning("Ошибка", "Введите название!")
                return
            
            if new_genre not in self.genres:
                messagebox.showwarning("Ошибка", "Выберите корректный жанр!")
                return
            
            try:
                new_year_int = int(new_year)
                current_year = datetime.now().year
                if new_year_int < 1888 or new_year_int > current_year:
                    messagebox.showwarning("Ошибка", f"Год должен быть от 1888 до {current_year}!")
                    return
            except ValueError:
                messagebox.showwarning("Ошибка", "Год должен быть числом!")
                return
            
            try:
                new_rating_float = float(new_rating)
                if new_rating_float < 0 or new_rating_float > 10:
                    messagebox.showwarning("Ошибка", "Рейтинг должен быть от 0 до 10!")
                    return
            except ValueError:
                messagebox.showwarning("Ошибка", "Рейтинг должен быть числом!")
                return
            
            # Сохранение изменений
            movie['title'] = new_title
            movie['genre'] = new_genre
            movie['year'] = new_year_int
            movie['rating'] = new_rating_float
            
            self.save_movies()
            self.display_movies()
            self.update_stats()
            edit_window.destroy()
            self.status_bar.config(text=f"✏️ Фильм '{new_title}' обновлён")
            messagebox.showinfo("Успех", "Фильм обновлён!")
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save_changes,
                 bg="#2ecc71", fg="white", padx=20, pady=5, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="❌ Отмена", command=edit_window.destroy,
                 bg="#95a5a6", fg="white", padx=20, pady=5, cursor="hand2").pack(side="left", padx=5)
    
    def update_stats(self):
        """Обновление статистики"""
        total = len(self.movies)
        if total > 0:
            avg_rating = sum(m['rating'] for m in self.movies) / total
            # Жанры
            genres_count = {}
            for m in self.movies:
                genres_count[m['genre']] = genres_count.get(m['genre'], 0) + 1
            most_common_genre = max(genres_count, key=genres_count.get) if genres_count else "Нет"
            
            stats_text = f"📊 Статистика: {total} фильмов | ⭐ Средний рейтинг: {avg_rating:.1f} | 🎭 Самый популярный жанр: {most_common_genre}"
        else:
            stats_text = "📊 Фильмов пока нет. Добавьте первый фильм!"
        
        self.stats_label.config(text=stats_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()
