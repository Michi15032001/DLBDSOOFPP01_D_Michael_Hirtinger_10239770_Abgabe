# import der benötigten Bibliotheken

import datetime
import json
import tkinter as tk
from tkinter import messagebox

# Klassen deklaration

class Fach:
    def __init__(self, bezeichnung, note, ects):
        self.bezeichnung = bezeichnung
        self.note = note
        self.ects = ects

    # Erstellen des Dict. für die Datenspeicherung
    def to_dict(self):
        return {
            "bezeichnung": self.bezeichnung,
            "note": self.note,
            "ects": self.ects
        }

class Semester:
    def __init__(self, nummer):
        self.nummer = nummer
        self.faecher = []

    def fach_hinzufuegen(self, bezeichnung, note, ects):
        fach = Fach(bezeichnung, note, ects)
        self.faecher.append(fach)

    # Erstellen des Dict. für die Datenspeicherung
    def to_dict(self):
        return {
            "nummer": self.nummer,
            "faecher": [fach.to_dict() for fach in self.faecher]
        }

class Student:
    def __init__(self, vorname, nachname, studiengang, ectsziel, notenziel):
        self.vorname = vorname
        self.nachname = nachname
        self.studiengang = studiengang
        self.ectsziel = ectsziel
        self.notenziel = notenziel

class AngelegterStudent(Student):
    def __init__(self, vorname, nachname, studiengang, ectsziel, notenziel, anlagedatum=None, userid=None):
        super().__init__(vorname, nachname, studiengang, ectsziel, notenziel)
        self.anlagedatum = anlagedatum if anlagedatum else datetime.datetime.now().isoformat()
        self.userid = userid if userid else 1
        self.semester = []

    def semester_hinzufuegen(self, nummer):
        sem = Semester(nummer)
        self.semester.append(sem)
        return sem

    # Erstellen des Dict. für die Datenspeicherung
    def to_dict(self):
        return {
            "vorname": self.vorname,
            "nachname": self.nachname,
            "studiengang": self.studiengang,
            "ectsziel": self.ectsziel,
            "notenziel": self.notenziel,
            "anlagedatum": self.anlagedatum,
            "userid": self.userid,
            "semester": [sem.to_dict() for sem in self.semester]
        }

class Datenmanager:
    # Versuch Userdaten zu laden falls Datei vorhanden
    @staticmethod
    def loadData():
        try:
            with open('user.json', 'r') as file:
                userdaten = json.load(file)
                vorname = userdaten["vorname"]
                nachname = userdaten["nachname"]
                studiengang = userdaten["studiengang"]
                ectsziel = userdaten["ectsziel"]
                notenziel = userdaten["notenziel"]
                anlagedatum = userdaten.get("anlagedatum")
                userid = userdaten.get("userid")
                user = AngelegterStudent(vorname, nachname, studiengang, ectsziel, notenziel, anlagedatum, userid)

                for sem_data in userdaten.get("semester", []):
                    semester = user.semester_hinzufuegen(sem_data["nummer"])
                    for fach_data in sem_data["faecher"]:
                        semester.fach_hinzufuegen(fach_data["bezeichnung"], fach_data["note"], fach_data["ects"])
                return user

        except FileNotFoundError:
            return None
    # Aufruf der to_dict Funktion + Speichern in JSON
    @staticmethod
    def saveData(user):
        if user:
            with open('user.json', 'w') as file:
                json.dump(user.to_dict(), file, indent=4)

class Interface:
    # Menü in welchem der Benutz die gewünschte Funktion anhand eines Buttons aufrufen kann
    @staticmethod
    def showMenu(user):
        root = tk.Tk()
        root.title("StudyDashboard")
        root.geometry("250x150")

        tk.Button(root, text="Neues Fach anlegen", command=lambda: Interface.neues_fach_anlegen(user)).pack()
        tk.Button(root, text="Dashboard anzeigen", command=lambda: Interface.dashboard_anzeigen(user)).pack()
        tk.Button(root, text="Programm beenden", command=root.quit).pack()

        root.mainloop()

    # Maske zur Anlage von neuen Fächern
    @staticmethod
    def neues_fach_anlegen(user):
        add_fach_window = tk.Tk()
        add_fach_window.title("Neues Fach anlegen")

        tk.Label(add_fach_window, text="Semester:").grid(row=0, column=0)
        entry_semester = tk.Entry(add_fach_window)
        entry_semester.grid(row=0, column=1)

        tk.Label(add_fach_window, text="Fachname:").grid(row=1, column=0)
        entry_fachname = tk.Entry(add_fach_window)
        entry_fachname.grid(row=1, column=1)

        tk.Label(add_fach_window, text="Note:").grid(row=2, column=0)
        entry_note = tk.Entry(add_fach_window)
        entry_note.grid(row=2, column=1)

        tk.Label(add_fach_window, text="ECTS:").grid(row=3, column=0)
        entry_ects = tk.Entry(add_fach_window)
        entry_ects.grid(row=3, column=1)

        tk.Button(add_fach_window, text="Speichern", command=lambda: Interface.speichern_fach(user, entry_semester, entry_fachname, entry_note, entry_ects, add_fach_window)).grid(row=4, columnspan=2)
        tk.Button(add_fach_window, text="Zurück", command=add_fach_window.destroy).grid(row=5, columnspan=2)

    # nach dem ausfüllen des Formulas
    @staticmethod
    def speichern_fach(user, entry_semester, entry_fachname, entry_note, entry_ects, window):
        sem_nummer = int(entry_semester.get())
        fachname = entry_fachname.get()
        note = entry_note.get()
        ects = int(entry_ects.get())

        semester = next((sem for sem in user.semester if sem.nummer == sem_nummer), None)
        if not semester:
            semester = user.semester_hinzufuegen(sem_nummer)

        semester.fach_hinzufuegen(fachname, note, ects)
        datenmanager.saveData(user)
        messagebox.showinfo("Erfolg", "Das Fach wurde angelegt und ist nun in Ihrem Dashboard für Sie einsehbar.")
        window.destroy()

    # Dashboard generieren
    @staticmethod
    def dashboard_anzeigen(user):
        dashboard_window = tk.Tk()
        dashboard_window.title("Dashboard")
        dashboard_window.geometry("800x400")

        pane = tk.PanedWindow(dashboard_window, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(pane)
        right_frame = tk.Frame(pane)

        pane.add(left_frame)
        pane.add(right_frame)

        tk.Label(left_frame, text="Semesterübersicht").pack()
        listbox_semester = tk.Listbox(left_frame)
        listbox_semester.pack(fill=tk.BOTH, expand=True)
        for sem in user.semester:
            listbox_semester.insert(tk.END, f"Semester {sem.nummer}")

        details_text = tk.Text(left_frame, height=10, width=50)
        details_text.pack(fill=tk.BOTH, expand=True)

        # aufrufen der einzelnen Fächer in den Semesterdetails
        listbox_semester.bind("<<ListboxSelect>>", lambda event: Interface.zeige_semester_details(event, user, listbox_semester, details_text))

        user_info_frame = tk.Frame(right_frame, bd=2, relief=tk.SOLID, padx=10, pady=10)
        user_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(user_info_frame, text=f"Studentenprofil: {user.vorname} {user.nachname}", anchor="w").pack(fill=tk.X)
        tk.Label(user_info_frame, text=f"Studiengang: {user.studiengang}", anchor="w").pack(fill=tk.X)
        tk.Label(user_info_frame, text=f"ECTS-Ziel: {user.ectsziel}", anchor="w").pack(fill=tk.X)
        tk.Label(user_info_frame, text=f"Notenziel: {user.notenziel}", anchor="w").pack(fill=tk.X)
        tk.Label(user_info_frame, text=f"Anlagedatum: {user.anlagedatum}", anchor="w").pack(fill=tk.X)

        ziel_status_frame = tk.Frame(right_frame, bd=2, relief=tk.SOLID, padx=10, pady=10)
        ziel_status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(ziel_status_frame, text="Zielübersicht", anchor="w").pack(fill=tk.X)
        tk.Label(ziel_status_frame, text=Interface.berechne_ziele(user), anchor="w", justify="left").pack(fill=tk.X)

        tk.Button(right_frame, text="Zurück", command=dashboard_window.destroy).pack()

    # Laden der Fächer zu einem Semester nach Userclick auf Semster auf der linken Seite des Dashboards
    @staticmethod
    def zeige_semester_details(event, user, listbox_semester, details_text):
        selected_semester = listbox_semester.curselection()
        if selected_semester:
            semester = user.semester[selected_semester[0]]
            details_text.delete(1.0, tk.END)
            for fach in semester.faecher:
                details_text.insert(tk.END, f"{fach.bezeichnung}: Note {fach.note}, {fach.ects} ECTS\n")

    # ECTS-Ziel und Notenziel berechnen
    @staticmethod
    def berechne_ziele(user):
        gesamt_ects = sum(fach.ects for sem in user.semester for fach in sem.faecher)
        gesamt_note = sum(float(fach.note) * fach.ects for sem in user.semester for fach in sem.faecher) / gesamt_ects if gesamt_ects > 0 else 0
        ects_erreicht = gesamt_ects >= int(user.ectsziel)
        note_erreicht = gesamt_note <= float(user.notenziel)

        ziel_text = f"ECTS erreicht: {gesamt_ects}/{user.ectsziel} - {'Ja' if ects_erreicht else 'Nein'}\n"
        ziel_text += f"Durchschnittsnote erreicht: {gesamt_note:.2f}/{user.notenziel} - {'Ja' if note_erreicht else 'Nein'}"

        return ziel_text

    # Anlage falls noch kein Benutzer vorhanden
    @staticmethod
    def createUser():
        user_window = tk.Tk()
        user_window.title("Neuen Benutzer anlegen")

        tk.Label(user_window, text="Vorname:").grid(row=0, column=0)
        entry_vorname = tk.Entry(user_window)
        entry_vorname.grid(row=0, column=1)

        tk.Label(user_window, text="Nachname:").grid(row=1, column=0)
        entry_nachname = tk.Entry(user_window)
        entry_nachname.grid(row=1, column=1)

        tk.Label(user_window, text="Studiengang:").grid(row=2, column=0)
        entry_studiengang = tk.Entry(user_window)
        entry_studiengang.grid(row=2, column=1)

        tk.Label(user_window, text="ECTS-Ziel:").grid(row=3, column=0)
        entry_ectsziel = tk.Entry(user_window)
        entry_ectsziel.grid(row=3, column=1)

        tk.Label(user_window, text="Notenziel:").grid(row=4, column=0)
        entry_notenziel = tk.Entry(user_window)
        entry_notenziel.grid(row=4, column=1)

        tk.Button(user_window, text="Speichern", command=lambda: Interface.speichern_user(entry_vorname, entry_nachname, entry_studiengang, entry_ectsziel, entry_notenziel, user_window)).grid(row=5, columnspan=2)

        user_window.mainloop()

    # Speichern des neu angelegten Benutzers
    @staticmethod
    def speichern_user(entry_vorname, entry_nachname, entry_studiengang, entry_ectsziel, entry_notenziel, window):
        vorname = entry_vorname.get()
        nachname = entry_nachname.get()
        studiengang = entry_studiengang.get()
        ectsziel = entry_ectsziel.get()
        notenziel = entry_notenziel.get()

        user = AngelegterStudent(vorname, nachname, studiengang, ectsziel, notenziel)
        datenmanager.saveData(user)
        window.destroy()
        Interface.showMenu(user)

# Main Ausführung + Logik ob Benutzer bereits vorhanden
if __name__ == "__main__":
    datenmanager = Datenmanager()
    user = datenmanager.loadData()
    if user:
        Interface.showMenu(user)
    else:
        Interface.createUser()