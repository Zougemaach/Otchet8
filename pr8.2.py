import tkinter as tk
from tkinter import filedialog, messagebox
import random
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


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class EWBFileApp:
    def __init__(self, root):
        self.root = root
        root.title("Генератор файла для осциллографа EWB")
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
        tk.Label(self.root, text="Генератор файла для осциллографа EWB",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(10, 2))

        tk.Label(self.root,
                 text="Формат таблицы: Time | V1 (0 В или 5 В)",
                 font=("Segoe UI", 9),
                 bg=BG, fg=MUTED).pack(pady=(0, 8))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 8))

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._build_params(left)
        self._build_preview(right)

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

    def _build_params(self, parent):
        # Шаг времени
        card1 = tk.Frame(parent, bg=CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        card1.pack(fill="x", pady=(0, 8))

        tk.Label(card1, text="ПАРАМЕТРЫ СИГНАЛА",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner = tk.Frame(card1, bg=CARD)
        inner.pack(fill="x", padx=14, pady=(0, 10))

        # Шаг
        tk.Label(inner, text="Шаг времени (с):",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        self.time_step = tk.Entry(inner, width=10,
                                  font=("Consolas", 11),
                                  bd=1, relief="solid",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  justify="center")
        self.time_step.insert(0, "0.01")
        self.time_step.pack(anchor="w", pady=(2, 8), ipady=3)

        # Количество бит
        tk.Label(inner, text="Количество бит:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        self.bits_count = tk.IntVar(value=8)
        self.bits_lbl = tk.Label(inner, text="8",
                                 font=("Consolas", 11, "bold"),
                                 bg=CARD, fg=ACCENT)
        self.bits_lbl.pack(anchor="e")

        self.bits_scale = tk.Scale(inner, from_=1, to=100,
                                   orient="horizontal",
                                   length=300, showvalue=False,
                                   bg=CARD, fg=TEXT, troughcolor="#ececf0",
                                   activebackground=ACCENT,
                                   highlightthickness=0, bd=0,
                                   sliderlength=16, width=8,
                                   command=lambda v: self.bits_lbl.config(
                                       text=str(int(float(v)))))
        self.bits_scale.set(8)
        self.bits_scale.pack(fill="x", pady=(2, 8))

        # Сэмплов на бит
        tk.Label(inner, text="Сэмплов на бит:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        self.samples_per_bit = tk.IntVar(value=2)
        self.samples_lbl = tk.Label(inner, text="2",
                                    font=("Consolas", 11, "bold"),
                                    bg=CARD, fg=ACCENT)
        self.samples_lbl.pack(anchor="e")

        self.samples_scale = tk.Scale(inner, from_=1, to=20,
                                      orient="horizontal",
                                      length=300, showvalue=False,
                                      bg=CARD, fg=TEXT, troughcolor="#ececf0",
                                      activebackground=ACCENT,
                                      highlightthickness=0, bd=0,
                                      sliderlength=16, width=8,
                                      command=lambda v: self.samples_lbl.config(
                                          text=str(int(float(v)))))
        self.samples_scale.set(2)
        self.samples_scale.pack(fill="x", pady=(2, 0))

        # Способ формирования
        card2 = tk.Frame(parent, bg=CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        card2.pack(fill="x", pady=(0, 8))

        tk.Label(card2, text="СПОСОБ ФОРМИРОВАНИЯ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner2 = tk.Frame(card2, bg=CARD)
        inner2.pack(fill="x", padx=14, pady=(0, 10))

        self.method = tk.StringVar(value="random")

        methods = [
            ("🎲 Случайно", "random"),
            ("✏️ Вручную", "manual"),
            ("🔁 Периодический (0101…)", "periodic"),
            ("⚡ Импульсы (0…01…)", "pulse"),
        ]

        for text, val in methods:
            tk.Radiobutton(inner2, text=text,
                           variable=self.method, value=val,
                           font=("Segoe UI", 10),
                           bg=CARD, fg=TEXT,
                           activebackground=CARD,
                           activeforeground=ACCENT,
                           selectcolor=CARD,
                           anchor="w",
                           bd=0, highlightthickness=0,
                           cursor="hand2",
                           command=self._on_method_change,
                           ).pack(fill="x", pady=2)

        # Поле для ручного ввода
        self.manual_entry = tk.Entry(inner2, width=35,
                                     font=("Consolas", 11),
                                     bd=1, relief="solid",
                                     highlightthickness=1,
                                     highlightbackground=BORDER,
                                     justify="left",
                                     state="disabled")
        self.manual_entry.pack(fill="x", pady=(8, 0), ipady=4)

        # Заголовок файла
        card3 = tk.Frame(parent, bg=CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        card3.pack(fill="x", pady=(0, 8))

        tk.Label(card3, text="ЗАГОЛОВОК ФАЙЛА",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner3 = tk.Frame(card3, bg=CARD)
        inner3.pack(fill="x", padx=14, pady=(0, 10))

        tk.Label(inner3, text="Имя схемы:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        self.circuit_name = tk.Entry(inner3, width=30,
                                     font=("Consolas", 10),
                                     bd=1, relief="solid",
                                     highlightthickness=1,
                                     highlightbackground=BORDER)
        self.circuit_name.insert(0, "untitled")
        self.circuit_name.pack(fill="x", pady=(2, 0), ipady=3)

    def _build_preview(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="ПРЕДПРОСМОТР ФАЙЛА",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        wrap = tk.Frame(card, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        self.preview = tk.Text(wrap,
                               font=("Consolas", 11),
                               bg="#ffffff", fg="#000000",
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

        # Теги
        self.preview.tag_configure("title", font=("Consolas", 14, "bold"))
        self.preview.tag_configure("header",
                                   font=("Consolas", 11, "bold"))
        self.preview.tag_configure("col1", foreground="#0a84ff")
        self.preview.tag_configure("col2", foreground="#30d158")
        self.preview.tag_configure("comment", foreground="#888888")

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
    # ЛОГИКА
    # ════════════════════════════════════════════════════════════
    def _on_method_change(self):
        if self.method.get() == "manual":
            self.manual_entry.config(state="normal")
        else:
            self.manual_entry.config(state="disabled")

    def _generate_bits(self):
        """Возвращает список битов согласно выбранному методу."""
        try:
            n = int(self.bits_scale.get())
        except ValueError:
            n = 8

        method = self.method.get()

        if method == "random":
            return [random.randint(0, 1) for _ in range(n)]

        elif method == "manual":
            text = self.manual_entry.get().strip()
            bits = [int(c) for c in text if c in "01"]
            if not bits:
                return [0] * n
            # Повторяем или обрезаем до n
            if len(bits) < n:
                bits = (bits * ((n // len(bits)) + 1))[:n]
            else:
                bits = bits[:n]
            return bits

        elif method == "periodic":
            return [i % 2 for i in range(n)]

        elif method == "pulse":
            # 4 нуля, 1 единица
            pattern = [0, 0, 0, 0, 1]
            bits = []
            while len(bits) < n:
                bits.extend(pattern)
            return bits[:n]

        return [0] * n

    def _generate_content(self):
        """Собирает строки файла EWB."""
        lines = []

        try:
            time_step = float(self.time_step.get().replace(",", "."))
            if time_step <= 0:
                time_step = 0.01
        except ValueError:
            time_step = 0.01

        samples = int(self.samples_scale.get())
        circuit_name = self.circuit_name.get().strip() or "untitled"

        # Заголовок
        lines.append(("title",
                      f"ASCII output data for Electronics Workbench "
                      f"circuit {circuit_name}"))
        lines.append(("comment", ""))
        lines.append(("header", f"{'Time':>12}    {'V1':>4}"))
        lines.append(("comment", ""))

        # Биты
        bits = self._generate_bits()

        # Генерируем строки
        t = 0.0
        for bit in bits:
            for _ in range(samples):
                lines.append(("data",
                              f"{t:>12.5f}    {bit * 5:>4}"))
                t += time_step

        return lines

    def generate_preview(self):
        lines = self._generate_content()

        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")

        for tag, text in lines:
            if tag == "title":
                self.preview.insert("end", text + "\n", "title")
            elif tag == "header":
                self.preview.insert("end", text + "\n", "header")
            elif tag == "comment":
                self.preview.insert("end", text + "\n", "comment")
            else:
                # Разделяем на две колонки
                parts = text.split()
                if len(parts) == 2:
                    self.preview.insert("end", f"{parts[0]:>12}    ",
                                        "col1")
                    self.preview.insert("end", f"{parts[1]:>4}\n",
                                        "col2")
                else:
                    self.preview.insert("end", text + "\n")

        self.preview.config(state="disabled")
        self.status.config(text=f"Строк: {len(lines)}", fg=GREEN)

    def save_file(self):
        default = f"ewb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            initialfile=default)
        if not path:
            return

        try:
            lines = self._generate_content()
            with open(path, "w", encoding="utf-8") as f:
                for _, text in lines:
                    f.write(text + "\n")

            self.status.config(
                text=f"Сохранено: {os.path.basename(path)}", fg=GREEN)

            if messagebox.askyesno(
                "Готово",
                f"Файл сохранён:\n{path}\n\nОткрыть папку?"):
                self._open_path(os.path.dirname(path))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def open_folder(self):
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
    app = EWBFileApp(root)
    root.mainloop()
