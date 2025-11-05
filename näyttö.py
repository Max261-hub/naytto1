# näyttö.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import hashlib
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------
# ASETUKSET / TIEDOSTOT
# -------------------------
USERS_FILE = "users.txt"
LOGIN_LOG = "login_log.txt"
TYOAITA_FILE = "tyoaika.txt"
RAPORTIT_DIR = "raportit"

if not os.path.exists(RAPORTIT_DIR):
    os.makedirs(RAPORTIT_DIR)


# -------------------------
# FUNKTIOT
# -------------------------
def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_users() -> dict:
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue
                user, h = line.split(":", 1)
                users[user] = h
    return users


def write_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for u, h in users.items():
            f.write(f"{u}:{h}\n")


def log_login(username: str, success: bool):
    with open(LOGIN_LOG, "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{ts} | {username} | {'OK' if success else 'FAIL'}\n")


def parse_pvm(pvm_str: str) -> datetime:
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(pvm_str, fmt)
        except ValueError:
            continue
    raise ValueError("Päivämäärä väärässä muodossa")


def lue_tiedot():
    if not os.path.exists(TYOAITA_FILE):
        return []
    data = []
    with open(TYOAITA_FILE, "r", encoding="utf-8") as f:
        for r in f:
            r = r.strip()
            if not r or ";" not in r:
                continue
            osat = r.split(";")
            if len(osat) >= 4:
                data.append(osat)
    return data


def kirjoita_tiedot(data):
    with open(TYOAITA_FILE, "w", encoding="utf-8") as f:
        for r in data:
            f.write(";".join(r) + "\n")


# -------------------------
# LOGIN & TILIN LUONTI
# -------------------------
def kirjautuminen():
    login = tk.Tk()
    login.title("Kirjautuminen")
    login.geometry("360x250")
    login.resizable(False, False)

    tk.Label(login, text="Käyttäjätunnus:").pack(pady=(12, 2))
    user_var = tk.StringVar()
    tk.Entry(login, textvariable=user_var).pack()

    tk.Label(login, text="Salasana:").pack(pady=(8, 2))
    pw_var = tk.StringVar()
    tk.Entry(login, textvariable=pw_var, show="*").pack()

    def do_login():
        user = user_var.get().strip()
        pw = pw_var.get()
        if not user or not pw:
            messagebox.showwarning("Virhe", "Täytä kaikki kentät")
            return
        users = read_users()
        if user in users and users[user] == sha256_hash(pw):
            log_login(user, True)
            login.destroy()
            avaa_paavalikko(user)
        else:
            log_login(user, False)
            messagebox.showerror("Virhe", "Väärä käyttäjätunnus tai salasana")

    def open_create_user():
        dlg = tk.Toplevel(login)
        dlg.title("Luo uusi tili")
        dlg.geometry("300x220")
        dlg.resizable(False, False)

        tk.Label(dlg, text="Uusi käyttäjätunnus:").pack(pady=(10, 2))
        new_user = tk.StringVar()
        tk.Entry(dlg, textvariable=new_user).pack()

        tk.Label(dlg, text="Salasana:").pack(pady=(8, 2))
        new_pw = tk.StringVar()
        tk.Entry(dlg, textvariable=new_pw, show="*").pack()

        def create_account():
            u = new_user.get().strip()
            p = new_pw.get()
            if not u or not p:
                messagebox.showwarning("Virhe", "Täytä kaikki kentät")
                return
            users = read_users()
            if u in users:
                messagebox.showerror("Virhe", "Tämä käyttäjätunnus on jo olemassa")
                return
            users[u] = sha256_hash(p)
            write_users(users)
            messagebox.showinfo("Onnistui", "Tili luotu!")
            dlg.destroy()

        tk.Button(dlg, text="Luo tili", bg="#0078D7", fg="white", command=create_account).pack(pady=12, ipadx=8, ipady=4)

    tk.Button(login, text="Kirjaudu", bg="#0078D7", fg="white", command=do_login).pack(pady=10)
    tk.Button(login, text="Luo uusi tili", bg="#6c757d", fg="white", command=open_create_user).pack(pady=4)

    login.mainloop()


# -------------------------
# PÄÄIKKUNA
# -------------------------
def avaa_paavalikko(user):
    root = tk.Tk()
    root.title(f"Työajanseuranta - {user}")
    root.geometry("560x820")
    root.configure(bg="#f7f7f7")
    root.resizable(False, False)

    # Tallennusosio
    frm_top = tk.Frame(root, bg="#f7f7f7")
    frm_top.pack(pady=10)

    tk.Label(frm_top, text="Nimi:", bg="#f7f7f7").grid(row=0, column=0, sticky="w", padx=6)
    nimi_var = tk.StringVar()
    tk.Entry(frm_top, textvariable=nimi_var, width=36).grid(row=0, column=1, padx=6)

    tk.Label(frm_top, text="Päivämäärä:", bg="#f7f7f7").grid(row=1, column=0, sticky="w", padx=6, pady=(8, 0))
    paiva_entry = DateEntry(frm_top, date_pattern="dd.mm.yyyy", width=14)
    paiva_entry.grid(row=1, column=1, sticky="w", padx=6, pady=(8, 0))

    tk.Label(frm_top, text="Tunnit:", bg="#f7f7f7").grid(row=2, column=0, sticky="w", padx=6, pady=(8, 0))
    tunnit_var = tk.StringVar()
    tk.Entry(frm_top, textvariable=tunnit_var, width=36).grid(row=2, column=1, padx=6, pady=(8, 0))

    tk.Label(frm_top, text="Tuntipalkka (€):", bg="#f7f7f7").grid(row=3, column=0, sticky="w", padx=6, pady=(8, 0))
    palkka_var = tk.StringVar(value="16.50")
    tk.Entry(frm_top, textvariable=palkka_var, width=36).grid(row=3, column=1, padx=6, pady=(8, 0))

    def tallenna():
        nimi = nimi_var.get().strip()
        pvm = paiva_entry.get_date().strftime("%d.%m.%Y")
        tunnit = tunnit_var.get().strip()
        palkka = palkka_var.get().strip()
        if not nimi or not tunnit or not palkka:
            messagebox.showwarning("Virhe", "Täytä kaikki kentät.")
            return
        try:
            float(tunnit)
            float(palkka)
        except:
            messagebox.showerror("Virhe", "Tunnit ja palkka pitää olla numeroita.")
            return
        with open(TYOAITA_FILE, "a", encoding="utf-8") as f:
            f.write(f"{nimi};{pvm};{tunnit};{palkka}\n")
        messagebox.showinfo("Tallennettu", f"Tiedot tallennettu {pvm}")
        nimi_var.set(""); tunnit_var.set(""); palkka_var.set("16.50")
        paivita_tyontekijat()

    tk.Button(frm_top, text="Tallenna", bg="#3cb371", fg="white", command=tallenna).grid(row=4, column=0, columnspan=2, pady=10)

    # Keskiosa: valinnat
    frm_mid = tk.Frame(root, bg="#f7f7f7")
    frm_mid.pack(pady=6)

    tk.Label(frm_mid, text="Valitse työntekijä:", bg="#f7f7f7").grid(row=0, column=0, padx=8)
    valittu_nimi = tk.StringVar()
    tyontekija_combo = ttk.Combobox(frm_mid, textvariable=valittu_nimi, state="readonly", width=36)
    tyontekija_combo.grid(row=0, column=1, padx=8, pady=6)

    tk.Label(frm_mid, text="Tarkastelu:", bg="#f7f7f7").grid(row=1, column=0, padx=8)
    valinta = tk.StringVar(value="Päivä")
    valinta_combo = ttk.Combobox(frm_mid, textvariable=valinta,
                                 values=["Päivä", "Viikko", "Kuukausi", "Vuosi"], state="readonly", width=33)
    valinta_combo.grid(row=1, column=1, padx=8, pady=6)

    tk.Label(frm_mid, text="Alkupäivä:", bg="#f7f7f7").grid(row=2, column=0, padx=8)
    alku_entry = DateEntry(frm_mid, date_pattern="dd.mm.yyyy", width=14)
    alku_entry.grid(row=2, column=1, sticky="w", padx=8)

    tk.Label(frm_mid, text="Loppupäivä:", bg="#f7f7f7").grid(row=3, column=0, padx=8)
    loppu_entry = DateEntry(frm_mid, date_pattern="dd.mm.yyyy", width=14)
    loppu_entry.grid(row=3, column=1, sticky="w", padx=8)

    result_label = tk.Label(root, text="", bg="white", bd=1, relief="solid", justify="left", anchor="w", font=("Arial", 11))
    result_label.pack(padx=18, pady=12, fill="x")

    def paivita_tyontekijat():
        nimet = sorted(set([r[0] for r in lue_tiedot()]))
        tyontekija_combo["values"] = nimet
        if nimet:
            valittu_nimi.set(nimet[0])

    paivita_tyontekijat()

    def laske_yhteenveto(nimi, tyyppi, alku=None, loppu=None):
        data = lue_tiedot()
        tunnit = 0
        eurot = 0
        for n, pvm_str, t, palkka in data:
            if n != nimi:
                continue
            try:
                pvm = parse_pvm(pvm_str)
            except:
                continue
            if alku and loppu:
                if not (alku <= pvm <= loppu):
                    continue
            elif tyyppi == "Kuukausi":
                now = datetime.now()
                if pvm.month != now.month or pvm.year != now.year:
                    continue
            elif tyyppi == "Vuosi":
                now = datetime.now()
                if pvm.year != now.year:
                    continue
            try:
                tunnit += float(t)
                eurot += float(t) * float(palkka)
            except:
                pass
        return tunnit, eurot

    def nayta():
        nimi = valittu_nimi.get()
        tyyppi = valinta.get()
        if not nimi:
            messagebox.showwarning("Virhe", "Valitse työntekijä")
            return
        alku = parse_pvm(alku_entry.get())
        loppu = parse_pvm(loppu_entry.get())
        tunnit, eurot = laske_yhteenveto(nimi, tyyppi, alku, loppu)
        result_label.config(text=f"{tyyppi}-yhteenveto {nimi}\nAjalla {alku.strftime('%d.%m.%Y')} - {loppu.strftime('%d.%m.%Y')}\n\nTunnit: {tunnit:.2f}\nAnsiot: {eurot:.2f} €")

    def pdf():
        nimi = valittu_nimi.get()
        tyyppi = valinta.get()
        alku = parse_pvm(alku_entry.get())
        loppu = parse_pvm(loppu_entry.get())
        tunnit, eurot = laske_yhteenveto(nimi, tyyppi, alku, loppu)
        tiedosto = os.path.join(RAPORTIT_DIR, f"{nimi}_{tyyppi}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
        c = canvas.Canvas(tiedosto, pagesize=A4)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 800, f"{tyyppi}-yhteenveto — {nimi}")
        c.setFont("Helvetica", 12)
        c.drawString(50, 770, f"Ajalta: {alku.strftime('%d.%m.%Y')} - {loppu.strftime('%d.%m.%Y')}")
        c.drawString(50, 740, f"Tunnit yhteensä: {tunnit:.2f} h")
        c.drawString(50, 720, f"Ansiot yhteensä: {eurot:.2f} €")
        c.save()
        messagebox.showinfo("PDF luotu", f"Tallennettu {tiedosto}")

    def poista():
        nimi = valittu_nimi.get()
        alku = parse_pvm(alku_entry.get())
        loppu = parse_pvm(loppu_entry.get())
        data = lue_tiedot()
        uusi = []
        for r in data:
            try:
                pvm = parse_pvm(r[1])
                if r[0] == nimi and alku <= pvm <= loppu:
                    continue
            except:
                pass
            uusi.append(r)
        kirjoita_tiedot(uusi)
        messagebox.showinfo("Poistettu", "Merkinnät poistettu.")
        paivita_tyontekijat()

    # Napit
    btn_frame = tk.Frame(root, bg="#f7f7f7")
    btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="Näytä yhteenveto", bg="#1E90FF", fg="white", command=nayta).grid(row=0, column=0, padx=6, pady=6)
    tk.Button(btn_frame, text="Tallenna PDF", bg="#FFA500", fg="black", command=pdf).grid(row=0, column=1, padx=6, pady=6)
    tk.Button(btn_frame, text="Poista tiedot", bg="#FF3333", fg="white", command=poista).grid(row=1, column=0, padx=6, pady=6)
    tk.Button(btn_frame, text="Sulje ohjelma", bg="#555555", fg="white", command=root.destroy).grid(row=1, column=1, padx=6, pady=6)

    # Salasanan vaihto
    def vaihda_salasana():
        dlg = tk.Toplevel(root)
        dlg.title("Vaihda salasana")
        dlg.geometry("320x220")
        dlg.resizable(False, False)

        tk.Label(dlg, text="Vanha salasana:").pack(pady=(10, 2))
        old_var = tk.StringVar()
        tk.Entry(dlg, textvariable=old_var, show="*").pack()

        tk.Label(dlg, text="Uusi salasana:").pack(pady=(8, 2))
        new_var = tk.StringVar()
        tk.Entry(dlg, textvariable=new_var, show="*").pack()

        def save_pw():
            oldp = old_var.get()
            newp = new_var.get()
            users = read_users()
            if users.get(user) != sha256_hash(oldp):
                messagebox.showerror("Virhe", "Vanha salasana väärin.")
                return
            users[user] = sha256_hash(newp)
            write_users(users)
            messagebox.showinfo("Onnistui", "Salasana vaihdettu.")
            dlg.destroy()

        tk.Button(dlg, text="Tallenna", bg="#0078D7", fg="white", command=save_pw).pack(pady=12, ipadx=6, ipady=4)

    tk.Button(root, text="Vaihda salasana", bg="#6c757d", fg="white", command=vaihda_salasana).pack(pady=(6, 12))

    root.mainloop()


# -------------------------
# KÄYNNISTYS
# -------------------------
if __name__ == "__main__":
    kirjautuminen()
