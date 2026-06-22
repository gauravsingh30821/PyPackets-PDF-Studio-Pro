
"""
PyPackets PDF Studio Pro v6.1 Ultimate
Bug-fixed edition

Changes:
- Removed PdfMerger dependency
- PDF merging now uses PdfWriter (works with modern pypdf)
- Better error handling
- Recent activity panel
- History export CSV
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from pypdf import PdfReader, PdfWriter
from PIL import Image
import sqlite3, csv, os
from datetime import datetime

DB = "pdfstudio.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPackets PDF Studio Pro")
        self.root.geometry("1400x850")

        self.init_db()
        self.build_ui()
        self.update_stats()

    def init_db(self):
        con = sqlite3.connect(DB)
        con.execute("""
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            created TEXT
        )
        """)
        con.commit()
        con.close()

    def add_history(self, action):
        con = sqlite3.connect(DB)
        con.execute(
            "INSERT INTO history(action,created) VALUES(?,?)",
            (action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        con.commit()
        con.close()
        self.update_stats()

    def build_ui(self):
        left = ctk.CTkFrame(self.root, width=260)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(
            left,
            text="PyPackets\nPDF Studio Pro",
            font=("Arial", 26, "bold")
        ).pack(pady=20)

        tools = [
            ("Merge PDFs", self.merge),
            ("Split PDF", self.split),
            ("Extract Pages", self.extract),
            ("Rotate PDF", self.rotate),
            ("Protect PDF", self.protect),
            ("Remove Password", self.unprotect),
            ("Image → PDF", self.image_to_pdf),
            ("PDF Metadata", self.metadata),
            ("Export History CSV", self.export_history),
            ("Toggle Theme", self.theme)
        ]

        for text, cmd in tools:
            ctk.CTkButton(left, text=text, command=cmd).pack(fill="x", padx=10, pady=4)

        self.main = ctk.CTkFrame(self.root)
        self.main.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            self.main,
            text="Ultimate Dashboard v6.1",
            font=("Arial", 30, "bold")
        ).pack(pady=10)

        self.stat_label = ctk.CTkLabel(self.main, text="Operations: 0")
        self.stat_label.pack()

        self.log = ctk.CTkTextbox(self.main)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

        self.write("PyPackets PDF Studio Pro v6.1 Ready")

    def write(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def update_stats(self):
        con = sqlite3.connect(DB)
        total = con.execute("SELECT COUNT(*) FROM history").fetchone()[0]
        con.close()
        if hasattr(self, "stat_label"):
            self.stat_label.configure(text=f"Total Operations: {total}")

    def theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    def merge(self):
        try:
            files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
            if not files:
                return

            out = filedialog.asksaveasfilename(defaultextension=".pdf")
            if not out:
                return

            writer = PdfWriter()

            for pdf in files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    writer.add_page(page)

            with open(out, "wb") as f:
                writer.write(f)

            self.add_history("Merge PDFs")
            self.write("Merge complete")
            messagebox.showinfo("Success", "PDFs merged successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def split(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf:
            return
        folder = filedialog.askdirectory()
        if not folder:
            return

        reader = PdfReader(pdf)

        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            with open(os.path.join(folder, f"page_{i+1}.pdf"), "wb") as f:
                writer.write(f)

        self.add_history("Split PDF")

    def extract(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf:
            return

        start = simpledialog.askinteger("Start", "Start Page")
        end = simpledialog.askinteger("End", "End Page")

        if start is None or end is None:
            return

        reader = PdfReader(pdf)
        writer = PdfWriter()

        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])

        out = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not out:
            return

        with open(out, "wb") as f:
            writer.write(f)

        self.add_history("Extract Pages")

    def rotate(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf:
            return

        reader = PdfReader(pdf)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(90)
            writer.add_page(page)

        out = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not out:
            return

        with open(out, "wb") as f:
            writer.write(f)

        self.add_history("Rotate PDF")

    def protect(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf:
            return

        pwd = simpledialog.askstring("Password", "Enter Password")
        if not pwd:
            return

        reader = PdfReader(pdf)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(pwd)

        out = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not out:
            return

        with open(out, "wb") as f:
            writer.write(f)

        self.add_history("Protect PDF")

    def unprotect(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf:
            return

        pwd = simpledialog.askstring("Password", "Current Password")

        reader = PdfReader(pdf)
        if reader.is_encrypted:
            reader.decrypt(pwd)

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        out = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not out:
            return

        with open(out, "wb") as f:
            writer.write(f)

        self.add_history("Remove Password")

    def image_to_pdf(self):
        imgs = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not imgs:
            return

        out = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not out:
            return

        images = [Image.open(i).convert("RGB") for i in imgs]
        images[0].save(out, save_all=True, append_images=images[1:])

        self.add_history("Image To PDF")

    def metadata(self):
        pdf = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf:
            return

        reader = PdfReader(pdf)
        messagebox.showinfo("Metadata", str(reader.metadata))
        self.add_history("Metadata View")

    def export_history(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return

        con = sqlite3.connect(DB)
        rows = con.execute("SELECT * FROM history").fetchall()
        con.close()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Action", "Created"])
            writer.writerows(rows)

        messagebox.showinfo("Success", "History exported.")

root = ctk.CTk()
App(root)
root.mainloop()
