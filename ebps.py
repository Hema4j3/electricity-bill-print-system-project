import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Database Setup
def connect_db():
    conn = sqlite3.connect("electricity_billing.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        units INTEGER NOT NULL,
                        total_bill REAL NOT NULL)''')
    conn.commit()
    conn.close()

# Function to Calculate and Save Bill
def calculate_bill():
    try:
        name = name_entry.get().strip()
        units_text = units_entry.get().strip()

        if not name:
            messagebox.showerror("Error", "Customer name is required!")
            return
        if not units_text.isdigit():
            messagebox.showerror("Error", "Please enter a valid positive number for units!")
            return

        units = int(units_text)
        if units < 0:
            messagebox.showerror("Error", "Units cannot be negative!")
            return

        rate_per_unit = 6  # Rate per unit in ₹
        total_bill = units * rate_per_unit

        save_bill(name, units, total_bill)
        messagebox.showinfo("Success", f"Bill generated for {name}and saved successfully.\nTotal: ₹{total_bill}")
        clear_fields()
        display_bills()
    except ValueError:
        messagebox.showerror("Error", "Invalid input for units!")

# Save Bill to Database
def save_bill(name, units, total_bill):
    conn = sqlite3.connect("electricity_billing.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, units, total_bill) VALUES (?, ?, ?)", (name, units, total_bill))
    conn.commit()
    conn.close()

# Delete Selected Bill
def delete_bill():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Please select a bill to delete.")
        return

    bill_details = tree.item(selected_item)["values"]
    if not bill_details:
        messagebox.showerror("Error", "Invalid selection.")
        return

    bill_id = bill_details[0]

    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete Bill ID {bill_id}?")
    if not confirm:
        return

    conn = sqlite3.connect("electricity_billing.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()

    display_bills()
    messagebox.showinfo("Success", f"Bill ID {bill_id} deleted successfully.")

# Clear Entire Table
def clear_table():
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete all records?")
    if confirm:
        conn = sqlite3.connect("electricity_billing.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers")
        conn.commit()
        conn.close()
        display_bills()
        messagebox.showinfo("Success", "All records deleted!")

# Update Selected Bill
def update_bill():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Please select a bill to update.")
        return

    bill_details = tree.item(selected_item)["values"]
    if not bill_details:
        messagebox.showerror("Error", "Invalid selection.")
        return

    bill_id = bill_details[0]
    name = name_entry.get().strip()
    units_text = units_entry.get().strip()

    if not name:
        messagebox.showerror("Error", "Customer name is required!")
        return
    if not units_text.isdigit():
        messagebox.showerror("Error", "Please enter a valid positive number for units!")
        return

    units = int(units_text)
    if units < 0:
        messagebox.showerror("Error", "Units cannot be negative!")
        return

    total_bill = units * 6  # Rate per unit is ₹6

    conn = sqlite3.connect("electricity_billing.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET name = ?, units = ?, total_bill = ? WHERE id = ?",
                   (name, units, total_bill, bill_id))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Bill ID {bill_id} updated successfully.")
    clear_fields()
    display_bills()

# Display Bills in Table
def display_bills():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("electricity_billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    records = cursor.fetchall()
    conn.close()
    for record in records:
        tree.insert("", "end", values=record)

# Clear Input Fields
def clear_fields():
    name_entry.delete(0, tk.END)
    units_entry.delete(0, tk.END)

# Print Bill (Generate Bill Slip)

def print_bill():
    selected_item = tree.focus()  # Get selected row
    if not selected_item:
        messagebox.showerror("Error", "Please select a bill to print.")
        return

    bill_details = tree.item(selected_item)["values"]
    if not bill_details:
        messagebox.showerror("Error", "Invalid bill selection.")
        return

    try:
        bill_id, name, units, total_bill = bill_details
    except ValueError:
        messagebox.showerror("Error", "Failed to retrieve bill details. Please check the data.")
        return

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bill_text = f"""
    ⚡ ELECTRICITY BILL RECEIPT ⚡
    ---------------------------------
    Date: {date_time}
    Bill ID: {bill_id}
    Customer: {name}
    Units Consumed: {units} kWh
    Rate per Unit: ₹6
    ---------------------------------
    Total Bill: ₹{total_bill}
    ---------------------------------
    Thank you for your payment!
    """

    # Save bill slip as a text file with UTF-8 encoding
    file_name = f"Bill_{bill_id}.txt"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(bill_text)

    messagebox.showinfo("Success", f"Bill slip saved as {file_name}")
    print(bill_text)  # Print in the console for testing

    # Open a new window to display the bill
    bill_window = tk.Toplevel(root)
    bill_window.title(f"Bill Slip - {bill_id}")
    bill_window.geometry("400x300")
    bill_window.configure(bg="#1E1E2E")

    bill_label = tk.Label(bill_window, text="Bill Receipt", font=("Arial", 14, "bold"), bg="#1E1E2E", fg="cyan")
    bill_label.pack(pady=5)

    bill_textbox = tk.Text(bill_window, font=("Arial", 12), bg="black", fg="white", wrap="word", padx=10, pady=10)
    bill_textbox.insert(tk.END, bill_text)
    bill_textbox.config(state="disabled")
    bill_textbox.pack(fill="both", expand=True)

    # Print the bill (send to printer)
    try:
        os.startfile(file_name, "print")  # Windows OS
    except AttributeError:
        try:
            os.system(f"lpr {file_name}")  # macOS & Linux
        except Exception as e:
            messagebox.showerror("Error", f"Printing failed: {e}")

    messagebox.showinfo("Success", f"Bill slip saved as Bill_{bill_id}.txt")
    print(bill_text)  # Print in the console for testing

# Display Bills
def display_bills():
    for row in tree.get_children():
        tree.delete(row)
    conn = sqlite3.connect("electricity_billing.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    records = cursor.fetchall()
    conn.close()
    for record in records:
        tree.insert("", "end", values=record)
# gui
connect_db()
root = tk.Tk()
root.title("Electricity Bill Print  System")
root.geometry("800x500")
root.configure(bg="#1E1E2E")

# Title Label
title_label = tk.Label(root, text="⚡ Electricity Bill Print System ⚡", font=("Arial", 18, "bold"), bg="#1E1E2E", fg="cyan")
title_label.pack(pady=10)

# Form Frame
form_frame = tk.Frame(root, bg="#2C3E50", padx=10, pady=10)
form_frame.pack(pady=5, fill="x")

# Labels and Entries
tk.Label(form_frame, text="Bill ID (for update/delete):", bg="#2C3E50", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
id_entry = tk.Entry(form_frame, font=("Arial", 12))
id_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Customer Name:", bg="#2C3E50", fg="white", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
name_entry = tk.Entry(form_frame, font=("Arial", 12))
name_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Units Consumed:", bg="#2C3E50", fg="white", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
units_entry = tk.Entry(form_frame, font=("Arial", 12))
units_entry.grid(row=2, column=1, padx=5, pady=5)

# Buttons
btn_frame = tk.Frame(root, bg="#1E1E2E")
btn_frame.pack(pady=5, fill="x")

ttk.Button(btn_frame, text="➕ Add Bill", command=calculate_bill).grid(row=0, column=0, padx=10, pady=5)
ttk.Button(btn_frame, text="✏️ Update Bill", command=update_bill).grid(row=0, column=1, padx=10, pady=5)
ttk.Button(btn_frame, text="🗑️ Delete Bill", command=delete_bill).grid(row=0, column=2, padx=10, pady=5)
ttk.Button(btn_frame, text="🔄 Refresh Bills", command=display_bills).grid(row=0, column=3, padx=10, pady=5)
ttk.Button(btn_frame, text="🧹 Clear Fields", command=clear_fields).grid(row=0, column=4, padx=10, pady=5)
ttk.Button(btn_frame, text="🗑️ Clear Table", command=clear_table).grid(row=0, column=5, padx=10, pady=5)
ttk.Button(btn_frame, text="🖨️ Print Bill", command=print_bill).grid(row=0, column=6, padx=10, pady=5)

# Table Display
table_frame = tk.Frame(root, bg="#1E1E2E")
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("ID", "Name", "Units", "Total Bill")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

tree.heading("ID", text="Bill ID", anchor="center")
tree.heading("Name", text="Customer Name", anchor="center")
tree.heading("Units", text="Units Consumed (kWh)", anchor="center")
tree.heading("Total Bill", text="Total Bill (₹)", anchor="center")

for col in columns:
    tree.column(col, width=160, anchor="center")

tree.pack(fill="both", expand=True)

display_bills()
root.mainloop()