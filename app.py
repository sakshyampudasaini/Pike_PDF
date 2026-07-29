
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

from core import PDFVaultEngine

# Set application appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PDFVaultApp(TkinterDnD.Tk if hasattr(TkinterDnD, 'Tk') else ctk.CTk):
    def __init__(self):
        super().__init__()

        self.engine = PDFVaultEngine()
        self.title("PDF Vault - Security Suite")
        self.geometry("1000x680")
        self.minsize(900, 600)

        self.selected_files: list[str] = []

        self._build_ui()

    def _build_ui(self):
        # Top Header
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.pack(side="top", fill="x")

        title_lbl = ctk.CTkLabel(
            header,
            text="🔒 PDF VAULT",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title_lbl.pack(side="left", padx=20, pady=15)

        subtitle_lbl = ctk.CTkLabel(
            header,
            text="Professional PDF Security & Encryption Suite",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle_lbl.pack(side="left", pady=15)

        # Main Layout: Sidebar Navigation + Tab Container
        self.tabview = ctk.CTkTabview(self, width=960, height=580)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)

        # Create Tabs
        self.tab_process = self.tabview.add("Operations")
        self.tab_tools = self.tabview.add("Password Tools")
        self.tab_history = self.tabview.add("History & Audit")

        self._setup_operations_tab()
        self._setup_tools_tab()
        self._setup_history_tab()

    # ------------------ TAB 1: OPERATIONS ------------------

    def _setup_operations_tab(self):
        parent = self.tab_process

        # File Drop / Select Area
        self.drop_frame = ctk.CTkFrame(parent, border_width=2, corner_radius=10)
        self.drop_frame.pack(fill="x", padx=10, pady=10)

        drop_lbl = ctk.CTkLabel(
            self.drop_frame,
            text="📁 Drag & Drop PDF Files Here OR Click to Select",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        drop_lbl.pack(pady=(15, 5))

        btn_select = ctk.CTkButton(
            self.drop_frame, text="Browse Files", command=self._select_files
        )
        btn_select.pack(pady=(0, 15))

        # Enable Drag & Drop if tkinterdnd2 is available
        try:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind("<<Drop>>", self._on_file_drop)
        except Exception:
            pass

        # Selected Files Label
        self.lbl_files_count = ctk.CTkLabel(parent, text="No files selected", text_color="gray")
        self.lbl_files_count.pack(anchor="w", padx=15)

        # Settings Form
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Operation Mode
        ctk.CTkLabel(form_frame, text="Operation:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.opt_mode = ctk.CTkOptionMenu(
            form_frame,
            values=["Encrypt", "Decrypt", "Change Password", "Remove Password"],
            command=self._on_mode_change,
        )
        self.opt_mode.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Passwords Inputs
        ctk.CTkLabel(form_frame, text="Password / Current Password:").grid(
            row=1, column=0, padx=10, pady=8, sticky="e"
        )
        self.ent_pwd1 = ctk.CTkEntry(form_frame, show="*", width=250)
        self.ent_pwd1.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        self.lbl_pwd2 = ctk.CTkLabel(form_frame, text="New Password:")
        self.lbl_pwd2.grid(row=2, column=0, padx=10, pady=8, sticky="e")
        self.ent_pwd2 = ctk.CTkEntry(form_frame, show="*", width=250)
        self.ent_pwd2.grid(row=2, column=1, padx=10, pady=8, sticky="w")
        self.lbl_pwd2.grid_remove()
        self.ent_pwd2.grid_remove()

        # Output Directory
        ctk.CTkLabel(form_frame, text="Output Directory:").grid(
            row=3, column=0, padx=10, pady=8, sticky="e"
        )
        self.ent_out_dir = ctk.CTkEntry(form_frame, width=320)
        self.ent_out_dir.grid(row=3, column=1, padx=10, pady=8, sticky="w")
        btn_out_dir = ctk.CTkButton(form_frame, text="Browse...", width=80, command=self._select_out_dir)
        btn_out_dir.grid(row=3, column=2, padx=5, pady=8)

        # Progress Section
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", padx=10, pady=10)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=15, pady=(15, 5))

        self.lbl_status = ctk.CTkLabel(progress_frame, text="Ready", text_color="gray")
        self.lbl_status.pack(pady=(0, 10))

        # Run Button
        self.btn_run = ctk.CTkButton(
            parent,
            text="🚀 Execute Operation",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            command=self._start_batch_thread,
        )
        self.btn_run.pack(fill="x", padx=10, pady=10)

    def _on_mode_change(self, choice: str):
        if choice == "Change Password":
            self.lbl_pwd2.grid()
            self.ent_pwd2.grid()
        else:
            self.lbl_pwd2.grid_remove()
            self.ent_pwd2.grid_remove()

    def _select_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")]
        )
        if files:
            self.selected_files = list(files)
            self.lbl_files_count.configure(
                text=f"{len(self.selected_files)} file(s) selected"
            )

    def _on_file_drop(self, event):
        files = self.tk.splitlist(event.data)
        pdf_files = [f for f in files if f.lower().endswith(".pdf")]
        if pdf_files:
            self.selected_files = pdf_files
            self.lbl_files_count.configure(
                text=f"{len(self.selected_files)} file(s) selected (Dropped)"
            )

    def _select_out_dir(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.ent_out_dir.delete(0, tk.END)
            self.ent_out_dir.insert(0, folder)

    def _start_batch_thread(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select at least one PDF file.")
            return

        pwd1 = self.ent_pwd1.get().strip()
        pwd2 = self.ent_pwd2.get().strip()
        mode = self.opt_mode.get()
        out_dir = self.ent_out_dir.get().strip()

        if mode in ["Encrypt", "Decrypt", "Remove Password"] and not pwd1:
            messagebox.showwarning("Warning", "Password field cannot be empty.")
            return

        if mode == "Change Password" and (not pwd1 or not pwd2):
            messagebox.showwarning("Warning", "Both current and new passwords are required.")
            return

        threading.Thread(
            target=self._run_batch_process,
            args=(mode, pwd1, pwd2, out_dir),
            daemon=True,
        ).start()

    def _run_batch_process(self, mode: str, pwd1: str, pwd2: str, out_dir: str):
        self.btn_run.configure(state="disabled")
        total = len(self.selected_files)

        for idx, in_file in enumerate(self.selected_files, start=1):
            file_name = os.path.basename(in_file)
            self.lbl_status.configure(text=f"Processing ({idx}/{total}): {file_name}")

            # Construct Output Path
            if out_dir and os.path.exists(out_dir):
                target_dir = out_dir
            else:
                target_dir = os.path.dirname(in_file)

            base, ext = os.path.splitext(file_name)
            out_file = os.path.join(target_dir, f"{base}_{mode.lower().replace(' ', '_')}{ext}")

            try:
                if mode == "Encrypt":
                    self.engine.encrypt_pdf(in_file, out_file, pwd1)
                elif mode == "Decrypt":
                    self.engine.decrypt_pdf(in_file, out_file, pwd1)
                elif mode == "Change Password":
                    self.engine.change_password(in_file, out_file, pwd1, pwd2)
                elif mode == "Remove Password":
                    self.engine.remove_password(in_file, out_file, pwd1)
            except Exception as e:
                self.engine.add_history_entry(mode, in_file, out_file, f"Error: {str(e)}")

            self.progress_bar.set(idx / total)

        self.lbl_status.configure(text="Batch operation completed!")
        self.btn_run.configure(state="normal")
        self._refresh_history_table()
        messagebox.showinfo("Success", "All operations completed!")

    # ------------------ TAB 2: TOOLS ------------------

    def _setup_tools_tab(self):
        parent = self.tab_tools

        # Generator Block
        gen_frame = ctk.CTkFrame(parent)
        gen_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            gen_frame, text="🔑 Password Generator", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)

        opts_frame = ctk.CTkFrame(gen_frame)
        opts_frame.pack(fill="x", padx=10, pady=5)

        self.chk_digits = ctk.CTkCheckBox(opts_frame, text="Digits (0-9)")
        self.chk_digits.select()
        self.chk_digits.pack(side="left", padx=10, pady=10)

        self.chk_symbols = ctk.CTkCheckBox(opts_frame, text="Symbols (!@#$)")
        self.chk_symbols.select()
        self.chk_symbols.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(opts_frame, text="Length:").pack(side="left", padx=(15, 5))
        self.spn_length = ctk.CTkEntry(opts_frame, width=50)
        self.spn_length.insert(0, "16")
        self.spn_length.pack(side="left", padx=5)

        btn_gen = ctk.CTkButton(opts_frame, text="Generate", command=self._generate_pwd)
        btn_gen.pack(side="right", padx=10)

        self.ent_gen_result = ctk.CTkEntry(gen_frame, font=ctk.CTkFont(size=14))
        self.ent_gen_result.pack(fill="x", padx=10, pady=10)

        # Analyzer Block
        analyzer_frame = ctk.CTkFrame(parent)
        analyzer_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            analyzer_frame,
            text="📊 Password Strength Analyzer",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=10, pady=10)

        self.ent_analyze_pwd = ctk.CTkEntry(
            analyzer_frame, placeholder_text="Type password to analyze..."
        )
        self.ent_analyze_pwd.pack(fill="x", padx=10, pady=5)
        self.ent_analyze_pwd.bind("<KeyRelease>", self._analyze_pwd_event)

        self.pwd_score_bar = ctk.CTkProgressBar(analyzer_frame)
        self.pwd_score_bar.set(0)
        self.pwd_score_bar.pack(fill="x", padx=10, pady=10)

        self.lbl_strength_res = ctk.CTkLabel(
            analyzer_frame, text="Rating: N/A", font=ctk.CTkFont(weight="bold")
        )
        self.lbl_strength_res.pack(anchor="w", padx=10)

        self.lbl_strength_feedback = ctk.CTkLabel(
            analyzer_frame, text="", text_color="gray", wraplength=700
        )
        self.lbl_strength_feedback.pack(anchor="w", padx=10, pady=(0, 10))

    def _generate_pwd(self):
        try:
            length = int(self.spn_length.get())
        except ValueError:
            length = 16

        pwd = self.engine.generate_password(
            length=length,
            use_digits=bool(self.chk_digits.get()),
            use_symbols=bool(self.chk_symbols.get()),
        )
        self.ent_gen_result.delete(0, tk.END)
        self.ent_gen_result.insert(0, pwd)

        # Trigger analysis
        self.ent_analyze_pwd.delete(0, tk.END)
        self.ent_analyze_pwd.insert(0, pwd)
        self._analyze_pwd_event(None)

    def _analyze_pwd_event(self, event):
        pwd = self.ent_analyze_pwd.get()
        rating, score, feedback = self.engine.analyze_password_strength(pwd)

        self.pwd_score_bar.set(score)
        self.lbl_strength_res.configure(text=f"Rating: {rating} ({int(score * 100)}%)")
        self.lbl_strength_feedback.configure(text=feedback)

    # ------------------ TAB 3: HISTORY ------------------

    def _setup_history_tab(self):
        parent = self.tab_history

        # Controls Bar
        ctrl_frame = ctk.CTkFrame(parent)
        ctrl_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(ctrl_frame, text="Filter:").pack(side="left", padx=5)
        self.ent_search_history = ctk.CTkEntry(
            ctrl_frame, placeholder_text="Search files or operations..."
        )
        self.ent_search_history.pack(side="left", fill="x", expand=True, padx=5)
        self.ent_search_history.bind("<KeyRelease>", lambda e: self._refresh_history_table())

        btn_export_csv = ctk.CTkButton(ctrl_frame, text="Export CSV", command=self._export_csv)
        btn_export_csv.pack(side="right", padx=5)

        btn_export_json = ctk.CTkButton(ctrl_frame, text="Export JSON", command=self._export_json)
        btn_export_json.pack(side="right", padx=5)

        # History Text Area / Table
        self.txt_history = ctk.CTkTextbox(parent, font=ctk.CTkFont(family="Courier", size=12))
        self.txt_history.pack(fill="both", expand=True, padx=10, pady=10)

        self._refresh_history_table()

    def _refresh_history_table(self):
        self.txt_history.delete("1.0", tk.END)
        query = self.ent_search_history.get().lower()

        header = f"{'Timestamp':<20} | {'Operation':<16} | {'File Name':<25} | {'Status':<15}\n"
        header += "-" * 82 + "\n"
        self.txt_history.insert(tk.END, header)

        for item in self.engine.history:
            searchable = f"{item['timestamp']} {item['operation']} {item['input_file']} {item['status']}".lower()
            if query in searchable:
                line = f"{item['timestamp']:<20} | {item['operation']:<16} | {item['input_file'][:23]:<25} | {item['status']:<15}\n"
                self.txt_history.insert(tk.END, line)

    def _export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            self.engine.export_logs_csv(path)
            messagebox.showinfo("Success", "Logs exported to CSV successfully!")

    def _export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            self.engine.export_logs_json(path)
            messagebox.showinfo("Success", "Logs exported to JSON successfully!")


if __name__ == "__main__":
    app = PDFVaultApp()
    app.mainloop()