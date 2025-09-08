#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 11:01:57 2025

@author: xiao

# credit_statement_builder.py
# Tkinter-based CRediT statement builder
# Run: python credit_statement_builder.py

"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog

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

# Some venues phrase two writing roles with alternate wording; include friendly variants for search
ALIASES = {
    "Writing- Original draft preparation": "Writing – original draft",
    "Writing- Original draft": "Writing – original draft",
    "Writing - Original draft": "Writing – original draft",
    "Writing- Reviewing and Editing": "Writing – review & editing",
    "Writing - Reviewing and Editing": "Writing – review & editing",
    "Writing- Review & Editing": "Writing – review & editing",
    "Writing - Review & Editing": "Writing – review & editing",
}

def normalize_role(role: str) -> str:
    role = role.strip()
    return ALIASES.get(role, role)

class CreditApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CRediT Statement Builder")
        self.geometry("980x600")
        self.minsize(900, 540)

        # Data: authors -> set(roles)
        self.authors = {}  # { "Name": set(["Conceptualization", ...]) }

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Left: Authors panel
        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsw")

        lbl_auth = ttk.Label(left, text="Authors")
        lbl_auth.pack(anchor="w")

        self.lst_authors = tk.Listbox(left, height=16, exportselection=False)
        self.lst_authors.pack(fill="y", expand=False, pady=(4, 8))
        self.lst_authors.bind("<<ListboxSelect>>", self.on_select_author)

        btns_auth = ttk.Frame(left)
        btns_auth.pack(anchor="w", pady=(0, 8))
        ttk.Button(btns_auth, text="Add author", command=self.add_author).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns_auth, text="Rename", command=self.rename_author).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(btns_auth, text="Remove", command=self.remove_author).grid(row=0, column=2)

        # Middle/Right: Roles panel
        right = ttk.Frame(self, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.columnconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)

        section = ttk.Label(right, text="Assign CRediT Roles", font=("TkDefaultFont", 10, "bold"))
        section.grid(row=0, column=0, columnspan=2, sticky="w")

        # Searchable dropdown
        search_frame = ttk.Frame(right)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 4))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search role:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.var_search = tk.StringVar()
        self.ent_search = ttk.Entry(search_frame, textvariable=self.var_search)
        self.ent_search.grid(row=0, column=1, sticky="ew")
        self.ent_search.bind("<KeyRelease>", self.update_role_list)

        ttk.Label(search_frame, text="Role:").grid(row=0, column=2, sticky="w", padx=(12, 8))
        self.var_role = tk.StringVar()
        self.cmb_roles = ttk.Combobox(search_frame, textvariable=self.var_role, values=CRediT_ROLES, state="readonly")
        self.cmb_roles.grid(row=0, column=3, sticky="ew")
        self.cmb_roles.bind("<Button-1>", lambda e: self.update_role_list())  # refresh before open

        ttk.Button(search_frame, text="Add role to selected author", command=self.add_role_to_author)\
            .grid(row=0, column=4, padx=(12, 0))

        # Assigned roles list
        ttk.Label(right, text="Roles for selected author").grid(row=2, column=0, sticky="w", pady=(10, 4))
        ttk.Label(right, text="All available roles").grid(row=2, column=1, sticky="w", pady=(10, 4))

        roles_frame = ttk.Frame(right)
        roles_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        roles_frame.columnconfigure(0, weight=1)
        roles_frame.columnconfigure(1, weight=1)
        roles_frame.rowconfigure(0, weight=1)

        self.lst_assigned = tk.Listbox(roles_frame, selectmode=tk.SINGLE)
        self.lst_assigned.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.lst_all = tk.Listbox(roles_frame)
        self.lst_all.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        for r in CRediT_ROLES:
            self.lst_all.insert(tk.END, r)

        role_btns = ttk.Frame(right)
        role_btns.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Button(role_btns, text="Remove selected role", command=self.remove_role_from_author).grid(row=0, column=0)
        ttk.Button(role_btns, text="Add selected role from right list", command=self.add_from_right_list).grid(row=0, column=1, padx=(8, 0))

        # Bottom: Output area + actions
        bottom = ttk.Frame(self, padding=10)
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=0)

        self.txt_output = tk.Text(bottom, height=5, wrap="word")
        self.txt_output.grid(row=0, column=0, sticky="ew")
        btns = ttk.Frame(bottom)
        btns.grid(row=0, column=1, sticky="e", padx=(8, 0))
        ttk.Button(btns, text="Generate", command=self.generate_output).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btns, text="Copy", command=self.copy_output).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(btns, text="Save…", command=self.save_output).grid(row=0, column=2)

        # Seed with example authors (optional)
        self.seed_example()

    # ------------- Author actions -------------
    def seed_example(self):
        # Example to show format; can be removed safely
        examples = ["Xiao Shang"]
        for name in examples:
            self.authors[name] = set()
            self.lst_authors.insert(tk.END, name)
        # Pre-assign a couple roles to demonstrate
        preset = {
            "Xiao Shang": ["Conceptualization", "Methodology", "Software"]
           
        }
        for a, roles in preset.items():
            self.authors[a].update(roles)

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

    # ------------- Role actions -------------
    def update_role_list(self, _event=None):
        """Filter roles by search box and refresh the combobox + right list."""
        q = self.var_search.get().strip().lower()
        def match(role):
            base = role.lower()
            return all(token in base for token in q.split()) if q else True

        filtered = [r for r in CRediT_ROLES if match(r)]
        # For aliases that match search, show them as suggestions mapping to canonical
        alias_hits = []
        for alias, canonical in ALIASES.items():
            if q and all(t in alias.lower() for t in q.split()):
                if canonical in CRediT_ROLES and canonical not in filtered:
                    alias_hits.append(alias + "  →  " + canonical)
        self.cmb_roles["values"] = filtered + (["—"] if (filtered and alias_hits) else []) + alias_hits
        if filtered:
            self.var_role.set(filtered[0])
        else:
            self.var_role.set("")

        # Update the right list to reflect current search (as a browseable catalog)
        self.lst_all.delete(0, tk.END)
        for r in filtered if q else CRediT_ROLES:
            self.lst_all.insert(tk.END, r)

    def selected_author_name(self):
        idx = self._selected_author_index()
        if idx is None:
            return None
        return self.lst_authors.get(idx)

    def add_role_to_author(self):
        author = self.selected_author_name()
        if not author:
            messagebox.showinfo("Select an author", "Please select an author first.")
            return
        raw = self.var_role.get()
        role = raw.split("→")[-1].strip() if "→" in raw else raw
        role = normalize_role(role)
        if not role:
            messagebox.showinfo("Pick a role", "Please choose a role.")
            return
        if role not in CRediT_ROLES:
            messagebox.showwarning("Invalid role", f"'{role}' is not an official CRediT role.")
            return
        if role in self.authors[author]:
            messagebox.showinfo("Already assigned", f"'{role}' is already assigned to {author}.")
            return
        self.authors[author].add(role)
        self.refresh_assigned_roles()

    def add_from_right_list(self):
        author = self.selected_author_name()
        if not author:
            messagebox.showinfo("Select an author", "Please select an author first.")
            return
        sel = self.lst_all.curselection()
        if not sel:
            messagebox.showinfo("Select a role", "Please select a role from the right list.")
            return
        role = self.lst_all.get(sel[0])
        role = normalize_role(role)
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

    # ------------- Output -------------
    def format_statement(self) -> str:
        # Authors appear in the order listed in the UI
        items = []
        for i in range(self.lst_authors.size()):
            name = self.lst_authors.get(i)
            roles = sorted(self.authors.get(name, set()))
            if not roles:
                continue
            # Prefer the user's example punctuation and spacing style
            # e.g., Zhang San: Conceptualization, Methodology, Software.
            items.append(f"{name}: {', '.join(roles)}.")
        return " ".join(items)

    def generate_output(self):
        statement = self.format_statement()
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", statement)
        self.copy_to_clipboard(statement)
        messagebox.showinfo("Generated", "Statement generated and copied to clipboard!")

    def copy_output(self):
        statement = self.txt_output.get("1.0", tk.END).strip()
        if not statement:
            self.generate_output()
            return
        self.copy_to_clipboard(statement)
        messagebox.showinfo("Copied", "Statement copied to clipboard.")

    def copy_to_clipboard(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()  # keeps clipboard after app closes (on some OS)
        except Exception:
            pass

    def save_output(self):
        statement = self.txt_output.get("1.0", tk.END).strip() or self.format_statement()
        if not statement:
            messagebox.showinfo("Nothing to save", "Please generate a statement first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save statement",
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
