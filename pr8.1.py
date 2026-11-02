import tkinter as tk
from tkinter import filedialog, messagebox
import random
import math
import os
from datetime import datetime


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#f7f7f9"
CARD = "#ffffff"
BORDER = "#e5e5ea"
TEXT = "#1c1c1e"
MUTED = "#8a8a8e"

ACCENT = "#0a84ff"
ACCENT_HOVER = "#0066cc"
GREEN = "#30d158"
GREEN_HOVER = "#20a544"
ORANGE = "#ff9f0a"
ORANGE_HOVER = "#cc7f08"
RED = "#e53935"
RED_HOVER = "#c62828"
PURPLE = "#8e44ad"
PURPLE_HOVER = "#7d3c98"


# ─── Функции ─────────────────────────────────────────────────────
FUNCTIONS = {
    "sin(x)": lambda x: math.sin(x),
    "cos(x)": lambda x: math.cos(x),
    "tan(x)": lambda x: math.tan(x) if abs(math.cos(x)) > 1e-6 else float('nan'),
    "x²":     lambda x: x ** 2,
    "√|x|":   lambda x: math.sqrt(abs(x)),
    "eˣ":     lambda x: math.exp(min(x, 50)),  # защита от переполнения
}


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class FileGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Генератор текстового файла")
        root.geometry("1180x820")
        root.minsize(1080, 780)
        root.configure(bg=BG)
        root.resizable(False, False)

        self._build_ui()
        self.generate_preview()

    # ════════════════════════════════════════════════════════════
    # UI
    # ════════════════════════════════════════════════════════════
    def _build_ui(self):
        tk.Label(self.root, text="Генератор текстового файла",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(10, 2))

        tk.Label(self.root,
                 text="Текст · Случайные числа · Значения функции",
                 font=("Segoe UI", 9),
                 bg=BG, fg=MUTED).pack(pady=(0, 8))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._build_left(left)
        self._build_right(right)

        # Нижняя панель
        bottom = tk.Frame(self.root, bg=CARD,
                          highlightthickness=1,
                          highlightbackground=BORDER)
        bottom.pack(padx=20, pady=(0, 16), fill="x")

        row = tk.Frame(bottom, bg=CARD)
        row.pack(fill="x", padx=14, pady=10)

        self._btn(row, "🔄 Предпросмотр", ACCENT, ACCENT_HOVER,
                  self.generate_preview).pack(side="left", padx=(0, 6))
        self._btn(row, "💾 Сохранить файл", GREEN, GREEN_HOVER,
                  self.save_file).pack(side="left", padx=6)
        self._btn(row, "📂 Открыть папку", ORANGE, ORANGE_HOVER,
                  self.open_folder).pack(side="left", padx=6)

        self.status = tk.Label(row, text="Готово",
                               font=("Segoe UI", 9),
                               bg=CARD, fg=MUTED)
        self.status.pack(side="right")

    def _build_left(self, parent):
        # ─── Текст ─────────────────────────────────────────────
        text_card = tk.Frame(parent, bg=CARD,
                             highlightthickness=1,
                             highlightbackground=BORDER)
        text_card.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(text_card, text="ПРОИЗВОЛЬНЫЙ ТЕКСТ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        self.text_input = tk.Text(text_card, height=6,
                                  font=("Consolas", 11),
                                  bg="#fafafa", fg=TEXT,
                                  bd=1, relief="solid",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  highlightcolor=ACCENT,
                                  wrap="word",
                                  padx=8, pady=6)
        self.text_input.pack(fill="x", padx=14, pady=(0, 12))
        self.text_input.insert("1.0",
            "Это тестовый файл, созданный приложением.\n"
            "Он содержит текст, случайные числа и значения функции.")

        # ─── Случайные числа ───────────────────────────────────
        rnd_card = tk.Frame(parent, bg=CARD,
                            highlightthickness=1,
                            highlightbackground=BORDER)
        rnd_card.pack(fill="x", pady=(0, 8))

        tk.Label(rnd_card, text="СЛУЧАЙНЫЕ ЧИСЛА",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner = tk.Frame(rnd_card, bg=CARD)
        inner.pack(fill="x", padx=14, pady=(0, 10))

        # Количество
        tk.Label(inner, text="Количество:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0, 6))

        self.count_var = tk.IntVar(value=20)
        self.count_lbl = tk.Label(inner, text="20",
                                  font=("Consolas", 11, "bold"),
                                  bg=CARD, fg=ACCENT, width=5)
        self.count_lbl.pack(side="left", padx=(0, 6))

        self.count_scale = tk.Scale(inner, from_=1, to=1000,
                                    orient="horizontal",
                                    length=150, showvalue=False,
                                    bg=CARD, fg=TEXT, troughcolor="#ececf0",
                                    activebackground=ACCENT,
                                    highlightthickness=0, bd=0,
                                    sliderlength=14, width=8,
                                    command=lambda v: self.count_lbl.config(
                                        text=str(int(float(v)))))
        self.count_scale.set(20)
        self.count_scale.pack(side="left", padx=(0, 20))

        # Диапазон
        tk.Label(inner, text="Диапазон:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0, 6))

        self.min_entry = tk.Entry(inner, width=6, font=("Consolas", 10),
                                  bd=1, relief="solid",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  justify="center")
        self.min_entry.insert(0, "-100")
        self.min_entry.pack(side="left", padx=(0, 4), ipady=3)

        tk.Label(inner, text="…",
                 font=("Segoe UI", 10),
                 bg=CARD, fg=MUTED).pack(side="left", padx=(0, 4))

        self.max_entry = tk.Entry(inner, width=6, font=("Consolas", 10),
                                  bd=1, relief="solid",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  justify="center")
        self.max_entry.insert(0, "100")
        self.max_entry.pack(side="left", ipady=3)

        # ─── Функция ───────────────────────────────────────────
        func_card = tk.Frame(parent, bg=CARD,
                             highlightthickness=1,
                             highlightbackground=BORDER)
        func_card.pack(fill="x", pady=(0, 8))

        tk.Label(func_card, text="ФУНКЦИЯ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner2 = tk.Frame(func_card, bg=CARD)
        inner2.pack(fill="x", padx=14, pady=(0, 10))

        # Выбор функции
        self.func_var = tk.StringVar(value="sin(x)")
        self.func_menu = tk.OptionMenu(inner2, self.func_var,
                                       *FUNCTIONS.keys(),
                                       command=lambda _: self.generate_preview())
        self.func_menu.config(font=("Segoe UI", 10),
                              bg="#fafafa", fg=TEXT,
                              bd=1, relief="solid",
                              highlightthickness=0,
                              width=10)
        self.func_menu.pack(side="left", padx=(0, 20))

        # Параметры X
        tk.Label(inner2, text="X от:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0, 4))

        self.x_from = tk.Entry(inner2, width=6, font=("Consolas", 10),
                               bd=1, relief="solid",
                               highlightthickness=1,
                               highlightbackground=BORDER,
                               justify="center")
        self.x_from.insert(0, "0")
        self.x_from.pack(side="left", padx=(0, 8), ipady=3)

        tk.Label(inner2, text="до:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0, 4))

        self.x_to = tk.Entry(inner2, width=6, font=("Consolas", 10),
                             bd=1, relief="solid",
                             highlightthickness=1,
                             highlightbackground=BORDER,
                             justify="center")
        self.x_to.insert(0, "6.28")
        self.x_to.pack(side="left", padx=(0, 8), ipady=3)

        tk.Label(inner2, text="шаг:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0, 4))

        self.x_step = tk.Entry(inner2, width=6, font=("Consolas", 10),
                               bd=1, relief="solid",
                               highlightthickness=1,
                               highlightbackground=BORDER,
                               justify="center")
        self.x_step.insert(0, "0.5")
        self.x_step.pack(side="left", ipady=3)

    def _build_right(self, parent):
        # ─── Предпросмотр ──────────────────────────────────────
        preview_card = tk.Frame(parent, bg=CARD,
                                highlightthickness=1,
                                highlightbackground=BORDER)
        preview_card.pack(fill="both", expand=True)

        tk.Label(preview_card, text="ПРЕДПРОСМОТР ФАЙЛА",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        wrap = tk.Frame(preview_card, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        self.preview = tk.Text(wrap,
                               font=("Consolas", 10),
                               bg="#0a0a1a", fg="#e8e8f0",
                               insertbackground="white",
                               bd=0, relief="flat",
                               highlightthickness=0,
                               wrap="none",
                               padx=10, pady=8,
                               state="disabled")
        self.preview.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(wrap, command=self.preview.yview,
                          bd=0, relief="flat", width=10)
        sb.pack(side="right", fill="y")
        self.preview.config(yscrollcommand=sb.set)

        # Теги для цветов
        self.preview.tag_configure("header", foreground="#00e5ff",
                                   font=("Consolas", 10, "bold"))
        self.preview.tag_configure("comment", foreground="#888888")
        self.preview.tag_configure("text", foreground="#ffffff")
        self.preview.tag_configure("number", foreground="#fdd835")
        self.preview.tag_configure("func", foreground="#30d158")

    def _btn(self, parent, text, bg, hover, command):
        btn = tk.Button(parent, text=text,
                        font=("Segoe UI", 10, "bold"),
                        bg=bg, fg="white",
                        activebackground=hover,
                        activeforeground="white",
                        bd=0, padx=12, pady=8, cursor="hand2",
                        command=command)

        def on_enter(e): btn.config(bg=hover)
        def on_leave(e): btn.config(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ════════════════════════════════════════════════════════════
    # ГЕНЕРАЦИЯ
    # ════════════════════════════════════════════════════════════
    def _generate_content(self):
        """Собирает содержимое файла как список кортежей (тип, текст)."""
        lines = []

        # Заголовок
        lines.append(("header", "=" * 60))
        lines.append(("header", "СГЕНЕРИРОВАННЫЙ ФАЙЛ"))
        lines.append(("header", "=" * 60))
        lines.append(("comment", f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"))
        lines.append(("comment", ""))

        # 1. Текст
        text = self.text_input.get("1.0", "end-1c").strip()
        lines.append(("header", "1. ПОЛЬЗОВАТЕЛЬСКИЙ ТЕКСТ"))
        lines.append(("header", "-" * 60))
        for line in text.split("\n"):
            lines.append(("text", line))
        lines.append(("comment", ""))

        # 2. Случайные числа
        lines.append(("header", "2. СЛУЧАЙНЫЕ ЧИСЛА"))
        lines.append(("header", "-" * 60))

        try:
            count = int(self.count_scale.get())
            rmin = int(self.min_entry.get())
            rmax = int(self.max_entry.get())
        except ValueError:
            count, rmin, rmax = 20, -100, 100

        lines.append(("comment",
                      f"Количество: {count}  ·  "
                      f"Диапазон: {rmin} … {rmax}"))
        lines.append(("comment", ""))

        random.seed(42)  # фиксируем seed, чтобы предпросмотр и файл совпадали
        numbers = [random.randint(rmin, rmax) for _ in range(count)]

        # По 10 чисел в строке
        per_line = 10
        for i in range(0, len(numbers), per_line):
            chunk = numbers[i:i + per_line]
            lines.append(("number",
                          "  ".join(f"{n:>5}" for n in chunk)))
        random.seed()  # возвращаем настоящий рандом

        lines.append(("comment", ""))

        # 3. Функция
        lines.append(("header", "3. ЗНАЧЕНИЯ ФУНКЦИИ"))
        lines.append(("header", "-" * 60))

        func_name = self.func_var.get()
        func = FUNCTIONS.get(func_name)

        try:
            x_from = float(self.x_from.get().replace(",", "."))
            x_to = float(self.x_to.get().replace(",", "."))
            x_step = float(self.x_step.get().replace(",", "."))
            if x_step <= 0:
                x_step = 0.5
        except ValueError:
            x_from, x_to, x_step = 0.0, 6.28, 0.5

        lines.append(("comment",
                      f"Функция: {func_name}  ·  "
                      f"X от {x_from} до {x_to} с шагом {x_step}"))
        lines.append(("comment", ""))
        lines.append(("header",
                      f"{'x':>10}  │  {'f(x)':>15}"))
        lines.append(("header", "-" * 32))

        if func:
            x = x_from
            while x <= x_to + x_step * 0.01:
                try:
                    y = func(x)
                    if math.isnan(y) or math.isinf(y):
                        y_str = "не определено"
                    else:
                        y_str = f"{y:>15.6f}"
                except (ValueError, OverflowError):
                    y_str = "ошибка"

                lines.append(("func",
                              f"{x:>10.3f}  │  {y_str}"))
                x += x_step

        lines.append(("comment", ""))
        lines.append(("header", "=" * 60))
        lines.append(("comment", "Конец файла"))
        lines.append(("header", "=" * 60))

        return lines

    def generate_preview(self):
        """Обновляет предпросмотр."""
        lines = self._generate_content()

        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")

        for tag, text in lines:
            self.preview.insert("end", text + "\n", tag)

        self.preview.config(state="disabled")
        self.status.config(text=f"Строк: {len(lines)}", fg=GREEN)

    # ════════════════════════════════════════════════════════════
    # СОХРАНЕНИЕ
    # ════════════════════════════════════════════════════════════
    def save_file(self):
        default_name = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            initialfile=default_name)
        if not path:
            return

        try:
            lines = self._generate_content()
            with open(path, "w", encoding="utf-8") as f:
                for tag, text in lines:
                    f.write(text + "\n")

            self.status.config(text=f"Сохранено: {os.path.basename(path)}",
                               fg=GREEN)

            if messagebox.askyesno("Готово",
                                   f"Файл сохранён:\n{path}\n\n"
                                   f"Открыть папку?"):
                self._open_path(os.path.dirname(path))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def open_folder(self):
        """Открывает папку с последним сохранённым файлом или домашнюю."""
        self._open_path(os.path.expanduser("~"))

    def _open_path(self, path):
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.name == "posix":
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть: {e}")


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FileGeneratorApp(root)
    root.mainloop()
