python
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Файл для хранения избранных
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Привязка Enter к поиску
        self.search_entry.bind("<Return>", lambda event: self.search_user())
        
        # Обновление списка избранных
        self.refresh_favorites_list()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главный контейнер
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_frame = tk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="🐙 GitHub User Finder", 
                               font=("Segoe UI", 22, "bold"), fg="#2c3e50")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Поиск и сохранение пользователей GitHub",
                                  font=("Segoe UI", 11), fg="#7f8c8d")
        subtitle_label.pack()
        
        # Панель поиска
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_label = tk.Label(search_frame, text="Введите username:", font=("Segoe UI", 12, "bold"))
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 12), width=40,
                                     relief="solid", borderwidth=1)
        self.search_entry.pack(side="left", padx=(0, 10))
        
        self.search_button = tk.Button(search_frame, text="🔍 Поиск", 
                                       command=self.search_user,
                                       bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                                       padx=20, pady=5, cursor="hand2", relief="flat")
        self.search_button.pack(side="left")
        
        # Результаты поиска
        results_frame = tk.LabelFrame(main_frame, text="📋 Результаты поиска", 
                                      font=("Segoe UI", 12, "bold"), padx=10, pady=10)
        results_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Таблица для результатов
        columns = ("Логин", "ID", "Имя", "Репозитории", "Подписчики")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        self.tree.heading("Логин", text="👤 Логин")
        self.tree.heading("ID", text="🆔 ID")
        self.tree.heading("Имя", text="📛 Имя")
        self.tree.heading("Репозитории", text="📚 Репозитории")
        self.tree.heading("Подписчики", text="👥 Подписчики")
        
        self.tree.column("Логин", width=180)
        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Имя", width=200)
        self.tree.column("Репозитории", width=120, anchor="center")
        self.tree.column("Подписчики", width=120, anchor="center")
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка добавления
        add_button_frame = tk.Frame(results_frame)
        add_button_frame.pack(fill="x", pady=(10, 0))
        
        self.add_button = tk.Button(add_button_frame, text="⭐ Добавить выбранного в избранное",
                                    command=self.add_selected_to_favorites,
                                    bg="#3498db", fg="white", font=("Segoe UI", 10, "bold"),
                                    padx=15, pady=5, cursor="hand2", relief="flat")
        self.add_button.pack()
        
        # Избранное
        favorites_frame = tk.LabelFrame(main_frame, text="⭐ Избранные пользователи", 
                                        font=("Segoe UI", 12, "bold"), padx=10, pady=10)
        favorites_frame.pack(fill="both", expand=True)
        
        # Список избранных
        list_frame = tk.Frame(favorites_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar_fav = tk.Scrollbar(list_frame)
        scrollbar_fav.pack(side="right", fill="y")
        
        self.favorites_listbox = tk.Listbox(list_frame, font=("Segoe UI", 11), 
                                            yscrollcommand=scrollbar_fav.set,
                                            height=6, selectmode=tk.SINGLE,
                                            relief="solid", borderwidth=1)
        self.favorites_listbox.pack(side="left", fill="both", expand=True)
        scrollbar_fav.config(command=self.favorites_listbox.yview)
        
        # Кнопки управления избранными
        button_frame = tk.Frame(favorites_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        tk.Button(button_frame, text="📋 Показать детали", 
                 command=self.show_favorite_details,
                 bg="#9b59b6", fg="white", cursor="hand2", padx=15, pady=5,
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="🗑️ Удалить из избранного", 
                 command=self.remove_favorite,
                 bg="#e74c3c", fg="white", cursor="hand2", padx=15, pady=5,
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="🔄 Обновить", 
                 command=self.refresh_favorites_list,
                 bg="#95a5a6", fg="white", cursor="hand2", padx=15, pady=5,
                 font=("Segoe UI", 10), relief="flat").pack(side="left", padx=5)
        
        # Статус бар
        self.status_bar = tk.Label(main_frame, text="✅ Готов к работе", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   font=("Segoe UI", 9), fg="#555")
        self.status_bar.pack(fill="x", pady=(10, 0))
    
    def load_favorites(self):
        """Загрузка избранных из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites
