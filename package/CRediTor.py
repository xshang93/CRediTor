#!/usr/bin/env python3
"""
Created on Mon Sep  8 11:01:57 2025

@author: xiao

"""
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

APP_NAME = "CRediT Statement Builder"
VERSION = "1.0.0"
AUTHOR = "Xiao Shang"
AUTHOR_EMAIL = "xiao.shang@mail.utoronto.ca"

TITLE_LINE = "CRediT authorship contribution statement"

# Canonical CRediT roles (14)
CRediT_ROLES = [
    "Conceptualization",
    "Data curation",
    "Formal analysis",
    "Funding acquisition",
    "Investigation",
    "Methodology",
    "Project administration",
    "Resources",
    "Software",
    "Supervision",
    "Validation",
    "Visualization",
    "Writing – original draft",
    "Writing – review & editing",
]

# Friendly aliases → canonical
ALIASES = {
    "Writing- Original draft preparation": "Writing – original draft",
    "Writing- Original draft": "Writing – original draft",
    "Writing - Original draft": "Writing – original draft",
    "Writing- original draft": "Writing – original draft",
    "Writing – Original draft": "Writing – original draft",
    "Writing—original draft": "Writing – original draft",
    "Writing- Reviewing and Editing": "Writing – review & editing",
    "Writing - Reviewing and Editing": "Writing – review & editing",
    "Writing- Review & Editing": "Writing – review & editing",
    "Writing - Review & Editing": "Writing – review & editing",
    "Writing—review & editing": "Writing – review & editing",
    "Writing- Reviewing & Editing": "Writing – review & editing",
}

# Concise CRediT role descriptions (adapted from credit.niso.org)
ROLE_DESCRIPTIONS = {
    "Conceptualization": "Ideas; formulation or evolution of overarching research goals and aims.",
    "Data curation": "Management activities to annotate (metadata), scrub, and maintain data for initial use and re-use.",
    "Formal analysis": "Use of statistical, mathematical, computational, or other formal techniques to analyze/synthesize data.",
    "Funding acquisition": "Acquisition of financial support for the project leading to this publication.",
    "Investigation": "Conducting research and investigation processes; performing experiments or data/evidence collection.",
    "Methodology": "Development or design of methodology; creation of models.",
    "Project administration": "Management and coordination responsibility for planning and execution of the research activity.",
    "Resources": "Provision of study materials, reagents, instrumentation, computing resources, or other analysis tools.",
    "Software": "Programming/software development; code implementation; algorithm design; testing of code components.",
    "Supervision": "Oversight and leadership for planning and execution; mentorship external to the core team.",
    "Validation": "Verification/replication of results/experiments and other research outputs.",
    "Visualization": "Preparation or presentation of the published work's visualization/data presentation.",
    "Writing – original draft": "Preparation and writing of the initial draft (including substantive translation).",
    "Writing – review & editing": "Critical review, commentary or revision at any stage, by original research group members.",
}

def normalize_role(role: str) -> str:
    role = (role or "").strip()
    return ALIASES.get(role, role)

class CreditApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        try:
            self.tk.call("tk", "scaling", 1.2)
        except Exception:
            pass
        self.geometry("1200x660")
        self.minsize(1100, 600)

        self._set_window_icon()
        self.authors = {}

        # Tabs: Builder | About
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        builder_frame = ttk.Frame(self.notebook)
        about_frame = ttk.Frame(self.notebook)

        self.notebook.add(builder_frame, text="Builder")
        self.notebook.add(about_frame, text="About")

        self._build_builder_tab(builder_frame)
        self._build_about_tab(about_frame)

    def _set_window_icon(self):
        for p in ("credit.png", "credit.ico"):
            if os.path.exists(p):
                try:
                    if p.lower().endswith(".png"):
                        img = tk.PhotoImage(file=p)
                        self.iconphoto(True, img)
                    else:
                        self.iconbitmap(p)
                except Exception:
                    pass
                break

    # ---------------- Builder Tab ----------------
    def _build_builder_tab(self, root):
        # Grid: 3 columns — Authors | Roles | Description
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=0)

        # Authors
        left = ttk.Frame(root, padding=10)
        left.grid(row=0, column=0, sticky="nsw")
        ttk.Label(left, text="Authors").pack(anchor="w")
        self.lst_authors = tk.Listbox(left, height=18, exportselection=False)
        self.lst_authors.pack(fill="y", expand=False, pady=(4, 8))
        self.lst_authors.bind("<<ListboxSelect>>", self.on_select_author)

        btns_auth = ttk.Frame(left)
        btns_auth.pack(anchor="w", pady=(0, 8))
        ttk.Button(btns_auth, text="Add author", command=self.add_author).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns_auth, text="Rename", command=self.rename_author).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(btns_auth, text="Remove", command=self.remove_author).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(btns_auth, text="Clear All", command=self.clear_all_authors).grid(row=0, column=3)

        # Roles + Descriptions
        middle = ttk.Frame(root, padding=10)
        middle.grid(row=0, column=1, sticky="nsew")
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=1)
        middle.rowconfigure(3, weight=1)

        ttk.Label(middle, text="Assign CRediT Roles", font=("TkDefaultFont", 10, "bold"))\
            .grid(row=0, column=0, columnspan=2, sticky="w")

        search_frame = ttk.Frame(middle)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 4))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Filter roles:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.var_search = tk.StringVar()
        self.ent_search = ttk.Entry(search_frame, textvariable=self.var_search)
        self.ent_search.grid(row=0, column=1, sticky="ew")
        self.ent_search.bind("<KeyRelease>", self.update_role_list)

        ttk.Label(middle, text="Roles for selected author").grid(row=2, column=0, sticky="w", pady=(10, 4))
        ttk.Label(middle, text="All available roles (double-click to add)").grid(row=2, column=1, sticky="w", pady=(10, 4))

        roles_frame = ttk.Frame(middle)
        roles_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        roles_frame.columnconfigure(0, weight=1)
        roles_frame.columnconfigure(1, weight=1)
        roles_frame.rowconfigure(0, weight=1)

        self.lst_assigned = tk.Listbox(roles_frame, selectmode=tk.SINGLE, exportselection=False)
        self.lst_assigned.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.lst_all = tk.Listbox(roles_frame, exportselection=False)
        self.lst_all.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        for r in CRediT_ROLES:
            self.lst_all.insert(tk.END, r)

        self.lst_all.bind("<<ListboxSelect>>", self.on_select_role_any_list)
        self.lst_assigned.bind("<<ListboxSelect>>", self.on_select_role_any_list)
        self.lst_all.bind("<Double-Button-1>", self.add_from_right_list_event)

        role_btns = ttk.Frame(middle)
        role_btns.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(role_btns, text="Remove selected role", command=self.remove_role_from_author).grid(row=0, column=0)
        ttk.Button(role_btns, text="Add selected role from right list", command=self.add_from_right_list).grid(row=0, column=1, padx=(8, 0))

        # Description panel
        # Description panel
        right = ttk.Frame(root, padding=10)
        right.grid(row=0, column=2, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(right, text="Role description", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky="w")

        desc_frame = ttk.Frame(right)
        desc_frame.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(desc_frame, orient="vertical")
        self.txt_desc = tk.Text(
            desc_frame,
            height=12,
            width=45,
            wrap="word",        # proper word wrapping
            yscrollcommand=scrollbar.set
        )
        self.txt_desc.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scrollbar.config(command=self.txt_desc.yview)

        self.txt_desc.configure(state="disabled")

        # Output + actions
        bottom = ttk.Frame(root, padding=10)
        bottom.grid(row=1, column=0, columnspan=3, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=0)

        self.txt_output = tk.Text(bottom, height=7, wrap="word")
        self.txt_output.grid(row=0, column=0, sticky="ew")

        btns = ttk.Frame(bottom)
        btns.grid(row=0, column=1, sticky="e", padx=(8, 0))
        ttk.Button(btns, text="Generate", command=self.generate_output).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Copy (text)", command=self.copy_output).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(btns, text="Save…", command=self.save_output).grid(row=0, column=2)

        self.seed_example()
        self.show_role_description("Conceptualization")

    # ---------------- About Tab ----------------
    def _build_about_tab(self, root):
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        frame = ttk.Frame(root, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)

        hdr = ttk.Label(frame, text=f"{APP_NAME}", font=("TkDefaultFont", 14, "bold"))
        hdr.grid(row=0, column=0, sticky="w")

        ttk.Label(frame, text=f"Version: {VERSION}").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(frame, text=f"Author: {AUTHOR}").grid(row=2, column=0, sticky="w")
        mail = ttk.Label(frame, text=f"Email: {AUTHOR_EMAIL}", foreground="#1e64c8", cursor="hand2")
        mail.grid(row=3, column=0, sticky="w")
        mail.bind("<Button-1>", lambda _e: webbrowser.open(f"mailto:{AUTHOR_EMAIL}"))

        blurb = (
            "CRediTor helps you quickly create CRediT authorship contribution statements.\n"
            "• Add authors, assign roles, and generate a clean statement starting with the standard title line.\n"
            "• Browse official CRediT role definitions in the right-hand description panel.\n"
            "• Copy or save the final statement as plain text."
        )
        txt = tk.Text(frame, height=8, wrap="word", relief="flat")
        txt.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        txt.insert("1.0", blurb)
        txt.configure(state="disabled")

    # ---------------- Author actions ----------------
    def seed_example(self):
        # Example authors
        examples = ["Jolie the Dachshund", "Author 2"]
        for name in examples:
            self.authors[name] = set()
            self.lst_authors.insert(tk.END, name)
        # Preset roles for the examples
        preset = {
            "Jolie the Dachshund": ["Conceptualization", "Methodology", "Software"],
            "Author 2": ["Data curation", "Writing – original draft"],

        }
        for a, roles in preset.items():
            self.authors[a].update(roles)
        # Refresh assigned list if first author selected
        if self.lst_authors.size() > 0:
            self.lst_authors.select_set(0)
            self.on_select_author()

    def add_author(self):
        name = simpledialog.askstring("Add author", "Full name:")
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in self.authors:
            messagebox.showwarning("Exists", f"'{name}' is already in the list.")
            return
        self.authors[name] = set()
        self.lst_authors.insert(tk.END, name)

    def rename_author(self):
        idx = self._selected_author_index()
        if idx is None:
            messagebox.showinfo("Select an author", "Please select an author to rename.")
            return
        old = self.lst_authors.get(idx)
        new = simpledialog.askstring("Rename author", "New name:", initialvalue=old)
        if not new:
            return
        new = new.strip()
        if not new:
            return
        if new != old:
            if new in self.authors:
                messagebox.showwarning("Exists", f"'{new}' is already in the list.")
                return
            self.authors[new] = self.authors.pop(old)
            self.lst_authors.delete(idx)
            self.lst_authors.insert(idx, new)
            self.lst_authors.select_set(idx)
            self.lst_authors.event_generate("<<ListboxSelect>>")

    def remove_author(self):
        idx = self._selected_author_index()
        if idx is None:
            messagebox.showinfo("Select an author", "Please select an author to remove.")
            return
        name = self.lst_authors.get(idx)
        if messagebox.askyesno("Remove author", f"Remove '{name}'?"):
            self.lst_authors.delete(idx)
            self.authors.pop(name, None)
            self.lst_assigned.delete(0, tk.END)

    def clear_all_authors(self):
        if messagebox.askyesno("Clear All", "Remove all authors and their roles?"):
            self.lst_authors.delete(0, tk.END)
            self.lst_assigned.delete(0, tk.END)
            self.authors.clear()

    def _selected_author_index(self):
        sel = self.lst_authors.curselection()
        return sel[0] if sel else None

    def on_select_author(self, _event=None):
        self.refresh_assigned_roles()

    def refresh_assigned_roles(self):
        self.lst_assigned.delete(0, tk.END)
        idx = self._selected_author_index()
        if idx is None:
            return
        author = self.lst_authors.get(idx)
        for r in sorted(self.authors.get(author, set())):
            self.lst_assigned.insert(tk.END, r)

    # ---------------- Role actions ----------------
    def update_role_list(self, _event=None):
        q = self.var_search.get().strip().lower()
        def match(role):
            base = role.lower()
            return all(token in base for token in q.split()) if q else True
        filtered = [r for r in CRediT_ROLES if match(r)]
        self.lst_all.delete(0, tk.END)
        for r in filtered if q else CRediT_ROLES:
            self.lst_all.insert(tk.END, r)
        if self.lst_all.size() > 0:
            self.lst_all.select_clear(0, tk.END)
            self.lst_all.select_set(0)
            self.on_select_role_any_list()

    def selected_author_name(self):
        idx = self._selected_author_index()
        if idx is None:
            return None
        return self.lst_authors.get(idx)

    def add_from_right_list_event(self, _e):
        self.add_from_right_list()

    def add_from_right_list(self):
        author = self.selected_author_name()
        if not author:
            messagebox.showinfo("Select an author", "Please select an author first.")
            return
        sel = self.lst_all.curselection()
        if not sel:
            messagebox.showinfo("Select a role", "Please select a role from the right list.")
            return
        role = normalize_role(self.lst_all.get(sel[0]))
        if role not in CRediT_ROLES:
            messagebox.showwarning("Invalid role", f"'{role}' is not an official CRediT role.")
            return
        if role in self.authors[author]:
            messagebox.showinfo("Already assigned", f"'{role}' is already assigned to {author}.")
            return
        self.authors[author].add(role)
        self.refresh_assigned_roles()

    def remove_role_from_author(self):
        author = self.selected_author_name()
        if not author:
            messagebox.showinfo("Select an author", "Please select an author first.")
            return
        sel = self.lst_assigned.curselection()
        if not sel:
            messagebox.showinfo("Select a role", "Please select a role to remove.")
            return
        role = self.lst_assigned.get(sel[0])
        self.authors[author].discard(role)
        self.refresh_assigned_roles()

    def on_select_role_any_list(self, _event=None):
        # Try assigned list first; if none, use all-roles list
        role = None
        sel_a = self.lst_assigned.curselection()
        if sel_a:
            role = self.lst_assigned.get(sel_a[0])
        else:
            sel_all = self.lst_all.curselection()
            if sel_all:
                role = self.lst_all.get(sel_all[0])
        if role:
            self.show_role_description(role)

    def show_role_description(self, role: str):
        canonical = normalize_role(role)
        desc = ROLE_DESCRIPTIONS.get(canonical, "No description available.")
        self.txt_desc.configure(state="normal")
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", f"{canonical}\n\n{desc}")
        self.txt_desc.configure(state="disabled")

    # ---------------- Output ----------------
    def format_statement_lines(self):
        """Return a list of lines: title + one line per author with roles."""
        lines = [TITLE_LINE]
        for i in range(self.lst_authors.size()):
            name = self.lst_authors.get(i)
            roles = sorted(self.authors.get(name, set()))
            if not roles:
                continue
            lines.append(f"{name}: {', '.join(roles)}.")
        return lines

    def format_statement_text(self) -> str:
        return "\n".join(self.format_statement_lines())

    def generate_output(self):
        statement = self.format_statement_text()
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", statement)
        self.copy_to_clipboard(statement)
        messagebox.showinfo("Generated", "Statement generated and copied to clipboard (plain text).")

    def copy_output(self):
        statement = self.txt_output.get("1.0", tk.END).strip()
        if not statement:
            statement = self.format_statement_text()
        self.copy_to_clipboard(statement)
        messagebox.showinfo("Copied", "Plain text copied to clipboard.")

    def copy_to_clipboard(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
        except Exception:
            pass

    def save_output(self):
        statement = self.txt_output.get("1.0", tk.END).strip() or self.format_statement_text()
        if not statement:
            messagebox.showinfo("Nothing to save", "Please generate a statement first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save statement (plain text)",
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("Markdown", "*.md"), ("All files", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(statement)
            messagebox.showinfo("Saved", f"Saved to:\n{path}")

if __name__ == "__main__":
    app = CreditApp()
    app.mainloop()