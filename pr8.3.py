import tkinter as tk
from tkinter import filedialog, messagebox
import random
import os
from datetime import datetime

# ─── Проверка зависимостей ───────────────────────────────────────
try:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.chart import BarChart, Reference
    HAS_XLSX = True
except ImportError:
    HAS_XLSX = False


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
class ReportGeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Генератор Word и Excel отчётов")
        root.geometry("1180x820")
        root.minsize(1080, 780)
        root.configure(bg=BG)
        root.resizable(False, False)

        # Данные
        self.values = []    # список результатов (int)

        self._build_ui()
        self._check_deps()

    # ════════════════════════════════════════════════════════════
    # UI
    # ════════════════════════════════════════════════════════════
    def _build_ui(self):
        tk.Label(self.root, text="Генератор Word и Excel отчётов",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(10, 2))

        tk.Label(self.root,
                 text="Таблица: Номер измерения · Результат (0…100)",
                 font=("Segoe UI", 9),
                 bg=BG, fg=MUTED).pack(pady=(0, 8))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 8))

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._build_params(left)
        self._build_table(right)

        # Нижняя панель
        bottom = tk.Frame(self.root, bg=CARD,
                          highlightthickness=1,
                          highlightbackground=BORDER)
        bottom.pack(padx=20, pady=(0, 16), fill="x")

        row = tk.Frame(bottom, bg=CARD)
        row.pack(fill="x", padx=14, pady=10)

        self._btn(row, "🎲 Заполнить автоматически",
                  ACCENT, ACCENT_HOVER,
                  self.autofill).pack(side="left", padx=(0, 6))

        self._btn(row, "💾 Сохранить оба файла",
                  GREEN, GREEN_HOVER,
                  self.save_files).pack(side="left", padx=6)

        self.status = tk.Label(row, text="Готово",
                               font=("Segoe UI", 9),
                               bg=CARD, fg=MUTED)
        self.status.pack(side="right")

    def _build_params(self, parent):
        # Количество
        card1 = tk.Frame(parent, bg=CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        card1.pack(fill="x", pady=(0, 8))

        tk.Label(card1, text="ПАРАМЕТРЫ ВЫБОРКИ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner = tk.Frame(card1, bg=CARD)
        inner.pack(fill="x", padx=14, pady=(0, 12))

        tk.Label(inner, text="Количество строк:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(anchor="w")

        self.rows_lbl = tk.Label(inner, text="20",
                                 font=("Consolas", 11, "bold"),
                                 bg=CARD, fg=ACCENT)
        self.rows_lbl.pack(anchor="e")

        self.rows_scale = tk.Scale(inner, from_=1, to=500,
                                   orient="horizontal",
                                   length=300, showvalue=False,
                                   bg=CARD, fg=TEXT, troughcolor="#ececf0",
                                   activebackground=ACCENT,
                                   highlightthickness=0, bd=0,
                                   sliderlength=16, width=8,
                                   command=lambda v: self.rows_lbl.config(
                                       text=str(int(float(v)))))
        self.rows_scale.set(20)
        self.rows_scale.pack(fill="x", pady=(2, 8))

        # Диапазон
        range_frame = tk.Frame(inner, bg=CARD)
        range_frame.pack(fill="x", pady=(4, 0))

        tk.Label(range_frame, text="Диапазон:",
                 font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0, 6))

        self.min_entry = tk.Entry(range_frame, width=6,
                                  font=("Consolas", 10),
                                  bd=1, relief="solid",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  justify="center")
        self.min_entry.insert(0, "0")
        self.min_entry.pack(side="left", ipady=3)

        tk.Label(range_frame, text="…",
                 font=("Segoe UI", 10),
                 bg=CARD, fg=MUTED).pack(side="left", padx=4)

        self.max_entry = tk.Entry(range_frame, width=6,
                                  font=("Consolas", 10),
                                  bd=1, relief="solid",
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  justify="center")
        self.max_entry.insert(0, "100")
        self.max_entry.pack(side="left", ipady=3)

        # Способ
        card2 = tk.Frame(parent, bg=CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        card2.pack(fill="x", pady=(0, 8))

        tk.Label(card2, text="СПОСОБ ЗАПОЛНЕНИЯ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner2 = tk.Frame(card2, bg=CARD)
        inner2.pack(fill="x", padx=14, pady=(0, 10))

        self.method = tk.StringVar(value="auto")

        for text, val in [("🎲 Автоматически (случайно)", "auto"),
                          ("✏️ Вручную (в таблице)", "manual")]:
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
                           ).pack(fill="x", pady=2)

        # Заголовок отчёта
        card3 = tk.Frame(parent, bg=CARD,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        card3.pack(fill="x", pady=(0, 8))

        tk.Label(card3, text="ЗАГОЛОВОК ОТЧЁТА",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        inner3 = tk.Frame(card3, bg=CARD)
        inner3.pack(fill="x", padx=14, pady=(0, 10))

        self.title_entry = tk.Entry(inner3, font=("Segoe UI", 11),
                                    bd=1, relief="solid",
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.title_entry.insert(0, "Результаты измерений")
        self.title_entry.pack(fill="x", ipady=4)

        # Инфо
        info = tk.Frame(parent, bg=CARD,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        info.pack(fill="x")

        tk.Label(info, text="ТРЕБОВАНИЯ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w"
                 ).pack(fill="x", padx=14, pady=(10, 4))

        self.deps_label = tk.Label(info, text="",
                                   font=("Segoe UI", 9),
                                   bg=CARD, fg=TEXT,
                                   justify="left", anchor="w",
                                   wraplength=280)
        self.deps_label.pack(fill="x", padx=14, pady=(0, 10))

    def _build_table(self, parent):
        card = tk.Frame(parent, bg=CARD,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg=CARD)
        header.pack(fill="x", padx=14, pady=(10, 4))

        tk.Label(header, text="ТАБЛИЦА ДАННЫХ",
                 font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=MUTED, anchor="w").pack(side="left")

        # Статистика справа
        self.stats_label = tk.Label(header, text="",
                                    font=("Consolas", 9),
                                    bg=CARD, fg=MUTED, anchor="e")
        self.stats_label.pack(side="right")

        wrap = tk.Frame(card, bg=CARD)
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # Canvas + Scrollbar для таблицы
        self.table_canvas = tk.Canvas(wrap, bg="white",
                                      highlightthickness=1,
                                      highlightbackground=BORDER)
        self.table_canvas.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(wrap, command=self.table_canvas.yview,
                          bd=0, relief="flat", width=10)
        sb.pack(side="right", fill="y")
        self.table_canvas.config(yscrollcommand=sb.set)

        self.table_frame = tk.Frame(self.table_canvas, bg="white")
        self.table_canvas.create_window((0, 0), window=self.table_frame,
                                        anchor="nw")

        self.table_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.config(
                scrollregion=self.table_canvas.bbox("all")))

        self.table_canvas.bind(
            "<Configure>",
            lambda e: self.table_canvas.itemconfig(
                self.table_canvas.find_all()[0],
                width=e.width) if self.table_canvas.find_all() else None)

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
    # ПРОВЕРКА ЗАВИСИМОСТЕЙ
    # ════════════════════════════════════════════════════════════
    def _check_deps(self):
        status = []
        if HAS_DOCX:
            status.append("✅ python-docx установлен")
        else:
            status.append("❌ python-docx НЕ установлен\n"
                          "   pip install python-docx")
        if HAS_XLSX:
            status.append("✅ openpyxl установлен")
        else:
            status.append("❌ openpyxl НЕ установлен\n"
                          "   pip install openpyxl")

        self.deps_label.config(text="\n".join(status))

    # ════════════════════════════════════════════════════════════
    # ЗАПОЛНЕНИЕ
    # ════════════════════════════════════════════════════════════
    def autofill(self):
        try:
            n = int(self.rows_scale.get())
            vmin = int(self.min_entry.get())
            vmax = int(self.max_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте числовые поля")
            return

        self.values = [random.randint(vmin, vmax) for _ in range(n)]
        self._render_table()

    def _render_table(self):
        # Очищаем
        for w in self.table_frame.winfo_children():
            w.destroy()

        # Заголовок таблицы
        header = tk.Frame(self.table_frame, bg="#0a84ff")
        header.pack(fill="x")

        tk.Label(header, text="№",
                 font=("Segoe UI", 10, "bold"),
                 bg="#0a84ff", fg="white", width=6).pack(side="left")
        tk.Label(header, text="Результат",
                 font=("Segoe UI", 10, "bold"),
                 bg="#0a84ff", fg="white", width=15).pack(side="left")

        # Строки
        for i, val in enumerate(self.values, start=1):
            row = tk.Frame(self.table_frame, bg="white")
            row.pack(fill="x")

            bg_color = "#f8f8f8" if i % 2 == 0 else "white"

            tk.Label(row, text=str(i),
                     font=("Consolas", 10),
                     bg=bg_color, fg=TEXT,
                     width=6, anchor="center",
                     ).pack(side="left", ipady=3, fill="y")
            tk.Label(row, text=str(val),
                     font=("Consolas", 10),
                     bg=bg_color, fg=TEXT,
                     width=15, anchor="center",
                     ).pack(side="left", ipady=3, fill="y")

        # Статистика
        if self.values:
            mn = min(self.values)
            mx = max(self.values)
            avg = sum(self.values) / len(self.values)
            self.stats_label.config(
                text=f"n = {len(self.values)}   "
                     f"min = {mn}   max = {mx}   "
                     f"avg = {avg:.1f}")
        else:
            self.stats_label.config(text="")

    def _manual_values(self):
        """Собирает значения из ручной таблицы, если есть."""
        if not self.values:
            return []
        return self.values

    # ════════════════════════════════════════════════════════════
    # СОХРАНЕНИЕ
    # ════════════════════════════════════════════════════════════
    def save_files(self):
        if not HAS_DOCX:
            messagebox.showerror("Ошибка",
                                 "Установите python-docx:\n"
                                 "pip install python-docx")
            return
        if not HAS_XLSX:
            messagebox.showerror("Ошибка",
                                 "Установите openpyxl:\n"
                                 "pip install openpyxl")
            return

        if not self.values:
            self.autofill()
            if not self.values:
                return

        # Папка
        path = filedialog.askdirectory(title="Куда сохранить отчёты?")
        if not path:
            return

        try:
            n = len(self.values)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base = os.path.join(path, f"report_{ts}")

            # Word
            docx_path = base + ".docx"
            self._save_word(docx_path)

            # Excel
            xlsx_path = base + ".xlsx"
            self._save_excel(xlsx_path)

            self.status.config(text="Файлы сохранены", fg=GREEN)
            messagebox.showinfo(
                "Готово",
                f"Сохранено:\n{docx_path}\n{xlsx_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")
            self.status.config(text=f"Ошибка: {e}", fg=RED)

    # ─── WORD ──────────────────────────────────────────────────
    def _save_word(self, path):
        doc = Document()

        # Заголовок
        title = self.title_entry.get() or "Результаты измерений"
        heading = doc.add_heading(title, level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Информация
        info = doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = info.add_run(
            f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}  ·  "
            f"Объём выборки: {len(self.values)}")
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

        doc.add_paragraph()

        # Таблица
        table = doc.add_table(rows=1, cols=2)
        table.style = "Light Grid Accent 1"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Заголовки
        header_cells = table.rows[0].cells
        header_cells[0].text = "Номер измерения"
        header_cells[1].text = "Результат"

        for cell in header_cells:
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in paragraph.runs:
                    r.font.bold = True
                    r.font.size = Pt(11)

        # Данные
        for i, val in enumerate(self.values, start=1):
            row = table.add_row().cells
            row[0].text = str(i)
            row[1].text = str(val)
            for cell in row:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in paragraph.runs:
                        r.font.size = Pt(10)

        # Ширина колонок
        for row in table.rows:
            row.cells[0].width = Cm(5)
            row.cells[1].width = Cm(5)

        # Статистика
        doc.add_paragraph()
        mn = min(self.values)
        mx = max(self.values)
        avg = sum(self.values) / len(self.values)

        stats = doc.add_paragraph()
        stats.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = stats.add_run("Статистика:")
        run.bold = True
        run.font.size = Pt(11)

        doc.add_paragraph(
            f"Минимум: {mn}\n"
            f"Максимум: {mx}\n"
            f"Среднее: {avg:.2f}\n"
            f"Объём выборки: {len(self.values)}"
        )

        doc.save(path)

    # ─── EXCEL ─────────────────────────────────────────────────
    def _save_excel(self, path):
        wb = Workbook()

        # ─── Лист 1: Данные ────────────────────────────────────
        ws = wb.active
        ws.title = "Данные"

        # Заголовки
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill("solid", fgColor="0A84FF")
        center_align = Alignment(horizontal="center", vertical="center")
        thin = Side(style="thin", color="CCCCCC")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        ws["A1"] = "Номер измерения"
        ws["B1"] = "Результат"

        for cell in ("A1", "B1"):
            ws[cell].font = header_font
            ws[cell].fill = header_fill
            ws[cell].alignment = center_align
            ws[cell].border = border

        # Данные
        for i, val in enumerate(self.values, start=2):
            ws[f"A{i}"] = i - 1
            ws[f"B{i}"] = val
            ws[f"A{i}"].alignment = center_align
            ws[f"B{i}"].alignment = center_align
            ws[f"A{i}"].border = border
            ws[f"B{i}"].border = border

        # Ширина
        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 15

        # Диаграмма
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Результаты измерений"
        chart.y_axis.title = "Значение"
        chart.x_axis.title = "Номер измерения"

        data = Reference(ws, min_col=2, min_row=1,
                         max_row=len(self.values) + 1)
        cats = Reference(ws, min_col=1, min_row=2,
                         max_row=len(self.values) + 1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        ws.add_chart(chart, "D2")

        # ─── Лист 2: Статистика ────────────────────────────────
        ws2 = wb.create_sheet("Статистика")

        stats = [
            ("Показатель", "Значение"),
            ("Объём выборки", len(self.values)),
            ("Минимум", min(self.values)),
            ("Максимум", max(self.values)),
            ("Сумма", sum(self.values)),
            ("Среднее", round(sum(self.values) / len(self.values), 2)),
            ("Медиана", sorted(self.values)[len(self.values) // 2]),
        ]

        for row_idx, (label, value) in enumerate(stats, start=1):
            ws2[f"A{row_idx}"] = label
            ws2[f"B{row_idx}"] = value

            if row_idx == 1:
                ws2[f"A{row_idx}"].font = header_font
                ws2[f"B{row_idx}"].font = header_font
                ws2[f"A{row_idx}"].fill = header_fill
                ws2[f"B{row_idx}"].fill = header_fill
                ws2[f"A{row_idx}"].alignment = center_align
                ws2[f"B{row_idx}"].alignment = center_align

            ws2[f"A{row_idx}"].border = border
            ws2[f"B{row_idx}"].border = border

        ws2.column_dimensions["A"].width = 22
        ws2.column_dimensions["B"].width = 15

        wb.save(path)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()
