# Hotel Management System with Guest and Reservation Classes

import tkinter as tk
from tkinter import messagebox
import json
from room import Room
from reservation import Reservation
from guest import Guest

#GROUP MEMBERS
#20230067
#20231237
#20230502

# -------------------- Hotel Logic --------------------
class Hotel:
    def __init__(self):
        self.rooms = {}
        self.reservations = {}

    def add_room(self, number):
        if number not in self.rooms:
            self.rooms[number] = Room(number)

    def make_reservation(self, room_number, guest):
        room = self.rooms.get(room_number)
        if room and not room.occupied:
            room.occupied = True
            self.reservations[room_number] = Reservation(room_number, guest)
            return True
        return False

    def cancel_reservation(self, room_number):
        if room_number in self.reservations:
            self.rooms[room_number].occupied = False
            del self.reservations[room_number]
            return True
        return False

    def get_available_rooms(self):
        return [room for room in self.rooms.values() if not room.occupied]

    def save_to_file(self):
        data = {
            "rooms": [{"number": r.number, "occupied": r.occupied} for r in self.rooms.values()],
            "reservations": [
                {
                    "room_number": res.room_number,
                    "guest": {"name": res.guest.name, "contact": res.guest.contact}
                }
                for res in self.reservations.values()
            ]
        }
        with open("hotel_data.json", "w") as f:
            json.dump(data, f)

    def load_from_file(self):
        try:
            with open("hotel_data.json", "r") as f:
                data = json.load(f)
            for r in data["rooms"]:
                room = Room(r["number"])
                room.occupied = r["occupied"]
                self.rooms[r["number"]] = room
            for res in data["reservations"]:
                guest_data = res["guest"]
                guest = Guest(guest_data["name"], guest_data.get("contact", ""))
                self.reservations[res["room_number"]] = Reservation(res["room_number"], guest)
        except FileNotFoundError:
            pass

# -------------------- GUI --------------------
class HotelApp:
    def __init__(self, root, hotel):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.geometry("600x500")
        self.root.configure(bg="#f9fbfd")

        self.hotel = hotel

        self._build_header()
        self._build_controls()
        self._build_output_box()

        self.refresh_available_rooms()

    def _build_header(self):
        header = tk.Label(self.root, text="🏨 Hotel Management System", font=("Helvetica", 18, "bold"), bg="#f9fbfd")
        header.pack(pady=15)

    def _build_controls(self):
        controls = tk.Frame(self.root, bg="#f9fbfd")
        controls.pack()

        btn_style = {"font": ("Helvetica", 11), "bg": "#007acc", "fg": "white", "width": 25, "padx": 4, "pady": 4, "bd": 0}

        tk.Button(controls, text="➕ Add Room", command=self.add_room_popup, **btn_style).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(controls, text="📝 Make Reservation", command=self.make_reservation_popup, **btn_style).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(controls, text="❌ Cancel Reservation", command=self.cancel_reservation_popup, **btn_style).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(controls, text="🔄 Refresh Rooms", command=self.refresh_available_rooms, **btn_style).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(controls, text="💾 Save and Exit", command=self.save_and_exit, **btn_style).grid(row=2, column=0, columnspan=2, pady=10)

    def _build_output_box(self):
        label = tk.Label(self.root, text="Available Rooms:", font=("Helvetica", 13, "bold"), bg="#f9fbfd")
        label.pack(pady=10)
        self.output = tk.Text(self.root, width=70, height=12, font=("Courier New", 10), wrap="word")
        self.output.pack(pady=5)

    def refresh_available_rooms(self):
        self.output.delete("1.0", tk.END)
        available = self.hotel.get_available_rooms()
        if available:
            for room in available:
                self.output.insert(tk.END, f"Room {room.number} is available\n")
        else:
            self.output.insert(tk.END, "No available rooms at the moment.\n")

    def add_room_popup(self):
        self._simple_form("Add Room", ["Room Number"], self.add_room_action)

    def make_reservation_popup(self):
        self._simple_form("Make Reservation", ["Room Number", "Guest Name", "Guest Contact"], self.make_reservation_action)

    def cancel_reservation_popup(self):
        self._simple_form("Cancel Reservation", ["Room Number"], self.cancel_reservation_action)

    def _simple_form(self, title, labels, callback):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("300x300")

        entries = []
        for label in labels:
            tk.Label(win, text=label).pack(pady=5)
            entry = tk.Entry(win)
            entry.pack(pady=5)
            entries.append(entry)

        def submit():
            values = [e.get() for e in entries]
            callback(values)
            win.destroy()

        tk.Button(win, text="Submit", command=submit, bg="#007acc", fg="white").pack(pady=20)

    def add_room_action(self, values):
        room_number = values[0]
        self.hotel.add_room(room_number)
        messagebox.showinfo("Success", f"Room {room_number} added.")
        self.refresh_available_rooms()

    def make_reservation_action(self, values):
        room_number, guest_name, guest_contact = values
        guest = Guest(guest_name, guest_contact)
        if self.hotel.make_reservation(room_number, guest):
            messagebox.showinfo("Success", f"Reservation made for {guest_name} in room {room_number}.")
        else:
            messagebox.showerror("Error", "Room is occupied or doesn't exist.")
        self.refresh_available_rooms()

    def cancel_reservation_action(self, values):
        room_number = values[0]
        if self.hotel.cancel_reservation(room_number):
            messagebox.showinfo("Success", f"Reservation for room {room_number} cancelled.")
        else:
            messagebox.showerror("Error", "No reservation found for that room.")
        self.refresh_available_rooms()

    def save_and_exit(self):
        self.hotel.save_to_file()
        self.root.quit()

# -------------------- Run App --------------------
if __name__ == "__main__":
    hotel = Hotel()
    hotel.load_from_file()
    root = tk.Tk()
    app = HotelApp(root, hotel)
    root.mainloop()
