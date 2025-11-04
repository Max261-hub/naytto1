import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu, Toplevel, ttk
from tkcalendar import DateEntry
import datetime
import os
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

tiedosto_nimi = "tyoaika.txt"

# -----------------------------
# Tiedoston käsittely
# -----------------------------
def lue_tiedot():
    if not os.path.exists(tiedosto_nimi):
        return []
    with open(tiedosto_nimi, "r", encoding="utf-8") as tiedosto:
        return [r.strip().split(";") for r in tiedosto.readlines() if ";" in r]

def kirjoita_tiedot(rivit):
    with open(tiedosto_nimi, "w", encoding="utf-8") as tiedosto:
        for r in rivit:
            tiedosto.write(";".join(r) + "\n")

# -----------------------------
# Tallennus
# -----------------------------
def tallenna_tyoaika():
    nimi = entry_nimi.get().strip()
    paiva = entry_paiva.get_date()
    tunnit = entry_tunnit.get().strip()
    palkka_str = entry_palkka.get().strip()

    if nimi == "" or tunnit == "" or palkka_str == "":
        messagebox.showwarning("Virhe", "Täytä nimi, tunnit ja palkka!")
        return

    try:
        tunnit = float(tunnit)
        palkka = float(palkka_str)
    except ValueError:
        messagebox.showerror("Virhe", "Tunnit ja palkka täytyy olla numeroita!")
        return

    with open(tiedosto_nimi, "a", encoding="utf-8") as tiedosto:
        tiedosto.write(f"{nimi};{paiva.strftime('%Y-%m-%d')};{tunnit};{palkka}\n")

    if nimi not in tyontekijat:
        tyontekijat.append(nimi)
        paivita_tyontekijat()

    messagebox.showinfo("Tallennettu", f"{nimi} – {paiva.strftime('%d.%m.%Y')}: {tunnit} h tallennettu.")
    entry_tunnit.delete(0, tk.END)
    paivita_viikkolista()

# -----------------------------
# Poistovalikko
# -----------------------------
def avaa_poistovalikko():
    nimi = valittu_nimi.get()
    if not nimi or nimi == "Ei työntekijöitä":
        messagebox.showwarning("Virhe", "Valitse työntekijä ensin!")
        return

    rivit = lue_tiedot()
    paivat = [r[1] for r in rivit if len(r) == 4 and r[0] == nimi]

    ikk = Toplevel(ikkuna)
    ikk.title("Poista tietoja")
    ikk.geometry("350x400")
    ikk.resizable(False, False)
    tk.Label(ikk, text=f"Poista tietoja – {nimi}", font=("Arial", 12, "bold")).pack(pady=10)

    tk.Label(ikk, text="Valitse päivä poistettavaksi:").pack()
    paiva_lista = tk.Listbox(ikk, height=10)
    for p in sorted(paivat):
        paiva_lista.insert(tk.END, p)
    paiva_lista.pack(pady=5, fill="x", padx=20)

    def poista_valittu_paiva():
        valittu = paiva_lista.get(tk.ACTIVE)
        if not valittu:
            messagebox.showwarning("Virhe", "Valitse päivä ensin!")
            return
        rivit_uusi = [r for r in rivit if not (r[0] == nimi and r[1] == valittu)]
        kirjoita_tiedot(rivit_uusi)
        messagebox.showinfo("Poistettu", f"{valittu} poistettu työntekijältä {nimi}.")
        ikk.destroy()
        paivita_tyontekijat()

    ttk.Button(ikk, text="Poista valittu päivä", command=poista_valittu_paiva).pack(pady=5)
    ttk.Button(ikk, text="Poista valittu viikko", command=lambda:[poista_viikko(nimi), ikk.destroy()]).pack(pady=5)
    ttk.Button(ikk, text="Poista valittu kuukausi", command=lambda:[poista_kuukausi(nimi), ikk.destroy()]).pack(pady=5)
    ttk.Button(ikk, text="Poista kaikki työntekijän tiedot", command=lambda:[poista_tyontekija(nimi), ikk.destroy()]).pack(pady=10)
    ttk.Button(ikk, text="Sulje", command=ikk.destroy).pack(pady=5)

# -----------------------------
# Poistotoiminnot
# -----------------------------
def poista_viikko(nimi):
    if valittu_viikko.get() == "Ei viikkoja":
        messagebox.showwarning("Virhe", "Valitse viikko ensin.")
        return
    viikko = int(valittu_viikko.get())
    rivit = lue_tiedot()
    uusi = [r for r in rivit if not (len(r) == 4 and r[0] == nimi and datetime.datetime.strptime(r[1], "%Y-%m-%d").date().isocalendar()[1] == viikko)]
    kirjoita_tiedot(uusi)
    messagebox.showinfo("Poistettu", f"Viikko {viikko} poistettu työntekijältä {nimi}.")
    paivita_viikkolista()

def poista_kuukausi(nimi):
    if valittu_kk.get() == "Ei kuukausia":
        messagebox.showwarning("Virhe", "Valitse kuukausi ensin.")
        return
    kk_nimi, vuosi = valittu_kk.get().split()
    vuosi = int(vuosi)
    kk = list(calendar.month_name).index(kk_nimi)
    rivit = lue_tiedot()
    uusi = [r for r in rivit if not (len(r) == 4 and r[0] == nimi and datetime.datetime.strptime(r[1], "%Y-%m-%d").date().month == kk and datetime.datetime.strptime(r[1], "%Y-%m-%d").date().year == vuosi)]
    kirjoita_tiedot(uusi)
    messagebox.showinfo("Poistettu", f"{kk_nimi} {vuosi} poistettu työntekijältä {nimi}.")
    paivita_viikkolista()

def poista_tyontekija(nimi):
    rivit = lue_tiedot()
    uusi = [r for r in rivit if r[0] != nimi]
    kirjoita_tiedot(uusi)
    messagebox.showinfo("Poistettu", f"Kaikki tiedot työntekijältä {nimi} poistettu.")
    tyontekijat.remove(nimi)
    paivita_tyontekijat()

# -----------------------------
# Päivitystoiminnot
# -----------------------------
def paivita_tyontekijat():
    global tyontekijat
    rivit = lue_tiedot()
    tyontekijat = sorted(set(r[0] for r in rivit)) if rivit else []
    menu = valikko["menu"]
    menu.delete(0, "end")
    for nimi in tyontekijat:
        menu.add_command(label=nimi, command=lambda value=nimi: valittu_nimi.set(value))
    if tyontekijat:
        valittu_nimi.set(tyontekijat[0])
    paivita_viikkolista()

def paivita_viikkolista(*args):
    nimi = valittu_nimi.get()
    rivit = lue_tiedot()
    viikot = set()
    kuukaudet = set()

    for osat in rivit:
        if len(osat) == 4 and osat[0] == nimi:
            paiva = datetime.datetime.strptime(osat[1], "%Y-%m-%d").date()
            viikot.add(paiva.isocalendar()[1])
            kuukaudet.add((paiva.year, paiva.month))

    menu_viikko = viikko_valikko["menu"]
    menu_viikko.delete(0, "end")
    for v in sorted(viikot):
        menu_viikko.add_command(label=str(v), command=lambda val=v: valittu_viikko.set(val))
    valittu_viikko.set("Ei viikkoja" if not viikot else sorted(viikot)[0])

    menu_kk = kuukausi_valikko["menu"]
    menu_kk.delete(0, "end")
    for (vuosi, kk) in sorted(kuukaudet):
        kk_nimi = calendar.month_name[kk]
        menu_kk.add_command(label=f"{kk_nimi} {vuosi}", command=lambda val=(vuosi, kk): valittu_kk.set(f"{kk_nimi} {vuosi}"))
    valittu_kk.set("Ei kuukausia" if not kuukaudet else f"{calendar.month_name[sorted(kuukaudet)[0][1]]} {sorted(kuukaudet)[0][0]}")

# -----------------------------
# Näyttötoiminnot ja PDF
# -----------------------------
def nayta_viikko():
    nimi = valittu_nimi.get()
    viikko = valittu_viikko.get()
    if viikko == "Ei viikkoja":
        messagebox.showinfo("Ei tietoja", "Ei valittua viikkoa.")
        return

    rivit = lue_tiedot()
    paivat = []
    palkka = 0
    yhteensa = 0
    for r in rivit:
        if len(r) == 4 and r[0] == nimi:
            p = datetime.datetime.strptime(r[1], "%Y-%m-%d").date()
            if p.isocalendar()[1] == int(viikko):
                paivat.append((p, float(r[2])))
                palkka = float(r[3])
                yhteensa += float(r[2])

    if not paivat:
        messagebox.showinfo("Ei tietoja", f"Ei tietoja viikolle {viikko}.")
        return

    teksti = f"Viikko {viikko}\n"
    for p, t in paivat:
        teksti += f"{p.strftime('%d.%m.%Y')}: {t} h\n"
    teksti += f"\nYhteensä: {yhteensa:.2f} h\nPalkka: {yhteensa*palkka:.2f} €"

    messagebox.showinfo(f"{nimi} – Viikko {viikko}", teksti)

def nayta_kuukausi():
    nimi = valittu_nimi.get()
    if valittu_kk.get() == "Ei kuukausia":
        messagebox.showinfo("Ei tietoja", "Ei valittua kuukautta.")
        return

    kk_nimi, vuosi = valittu_kk.get().split()
    vuosi = int(vuosi)
    kk = list(calendar.month_name).index(kk_nimi)
    rivit = lue_tiedot()
    paivat = []
    palkka = 0
    yhteensa = 0
    for r in rivit:
        if len(r) == 4 and r[0] == nimi:
            p = datetime.datetime.strptime(r[1], "%Y-%m-%d").date()
            if p.month == kk and p.year == vuosi:
                paivat.append((p, float(r[2])))
                palkka = float(r[3])
                yhteensa += float(r[2])

    if not paivat:
        messagebox.showinfo("Ei tietoja", f"Ei tietoja kuukaudelle {kk_nimi}.")
        return

    teksti = f"{kk_nimi} {vuosi}\n"
    for p, t in paivat:
        teksti += f"{p.strftime('%d.%m.%Y')}: {t} h\n"
    teksti += f"\nYhteensä: {yhteensa:.2f} h\nPalkka: {yhteensa*palkka:.2f} €"

    messagebox.showinfo(f"{nimi} – {kk_nimi}", teksti)

def tallenna_viikko_pdf():
    nimi = valittu_nimi.get()
    viikko = valittu_viikko.get()
    if viikko == "Ei viikkoja":
        messagebox.showinfo("Ei tietoja", "Valitse viikko ensin.")
        return

    rivit = lue_tiedot()
    paivat = []
    palkka = 0
    yhteensa = 0
    for r in rivit:
        if len(r) == 4 and r[0] == nimi:
            p = datetime.datetime.strptime(r[1], "%Y-%m-%d").date()
            if p.isocalendar()[1] == int(viikko):
                paivat.append((p, float(r[2])))
                palkka = float(r[3])
                yhteensa += float(r[2])

    if not paivat:
        messagebox.showinfo("Ei tietoja", f"Ei tietoja viikolle {viikko}.")
        return

    tallenna_pdf_raportti(f"{nimi}_viikko{viikko}.pdf", f"Viikko {viikko}", nimi, paivat, yhteensa, yhteensa*palkka)

def tallenna_kuukausi_pdf():
    nimi = valittu_nimi.get()
    if valittu_kk.get() == "Ei kuukausia":
        messagebox.showinfo("Ei tietoja", "Valitse kuukausi ensin.")
        return
    kk_nimi, vuosi = valittu_kk.get().split()
    vuosi = int(vuosi)
    kk = list(calendar.month_name).index(kk_nimi)
    rivit = lue_tiedot()
    paivat = []
    palkka = 0
    yhteensa = 0
    for r in rivit:
        if len(r) == 4 and r[0] == nimi:
            p = datetime.datetime.strptime(r[1], "%Y-%m-%d").date()
            if p.month == kk and p.year == vuosi:
                paivat.append((p, float(r[2])))
                palkka = float(r[3])
                yhteensa += float(r[2])
    if not paivat:
        messagebox.showinfo("Ei tietoja", f"Ei tietoja kuukaudelle {kk_nimi}.")
        return

    tallenna_pdf_raportti(f"{nimi}_{kk_nimi}_{vuosi}.pdf", f"{kk_nimi} {vuosi}", nimi, paivat, yhteensa, yhteensa*palkka)

def tallenna_pdf_raportti(tiedostonimi, otsikko, nimi, paivat, tunnit, palkka_yht):
    if not os.path.exists("raportit"):
        os.makedirs("raportit")
    polku = os.path.join("raportit", tiedostonimi)
    c = canvas.Canvas(polku, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Työaikaraportti – {nimi}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, otsikko)
    c.drawString(50, 760, "-" * 80)
    y = 740
    for p, t in sorted(paivat):
        c.drawString(50, y, f"{p.strftime('%d.%m.%Y')}: {t:.1f} h")
        y -= 20
    c.drawString(50, y - 10, f"Yhteensä: {tunnit:.1f} h")
    c.drawString(50, y - 30, f"Palkka yhteensä: {palkka_yht:.2f} €")
    c.save()
    messagebox.showinfo("PDF tallennettu", f"Raportti tallennettu: {polku}")

# -----------------------------
# Käyttöliittymä
# -----------------------------
ikkuna = tk.Tk()
ikkuna.title("Työajan seurantaohjelma")
ikkuna.geometry("430x780")
ikkuna.configure(bg="#f0f0f0")

tk.Label(ikkuna, text="🕒 Työajan seuranta", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=10)

tk.Label(ikkuna, text="Työntekijän nimi:", bg="#f0f0f0").pack()
entry_nimi = tk.Entry(ikkuna, width=30)
entry_nimi.pack()

tk.Label(ikkuna, text="Päivämäärä:", bg="#f0f0f0").pack()
entry_paiva = DateEntry(ikkuna, width=27, background="lightblue", date_pattern="dd.mm.yyyy")
entry_paiva.pack()

tk.Label(ikkuna, text="Työtunnit:", bg="#f0f0f0").pack()
entry_tunnit = tk.Entry(ikkuna, width=30)
entry_tunnit.pack()

tk.Label(ikkuna, text="Tuntipalkka (€):", bg="#f0f0f0").pack()
entry_palkka = tk.Entry(ikkuna, width=30)
entry_palkka.insert(0, "16.50")
entry_palkka.pack(pady=3)

tk.Button(ikkuna, text="Tallenna työaika", command=tallenna_tyoaika, width=25, bg="#4CAF50", fg="white").pack(pady=5)
tk.Button(ikkuna, text="Poista tietoja...", command=avaa_poistovalikko, width=25, bg="#FF5722", fg="white").pack(pady=5)

rivit = lue_tiedot()
tyontekijat = sorted(set(r[0] for r in rivit)) if rivit else []
valittu_nimi = StringVar(value=tyontekijat[0] if tyontekijat else "Ei työntekijöitä")
valittu_nimi.trace_add("write", paivita_viikkolista)

tk.Label(ikkuna, text="Valitse työntekijä:", bg="#f0f0f0").pack(pady=(10, 0))
valikko = OptionMenu(ikkuna, valittu_nimi, *tyontekijat)
valikko.pack()

tk.Label(ikkuna, text="Valitse viikko:", bg="#f0f0f0").pack(pady=(10, 0))
valittu_viikko = StringVar(value="Ei viikkoja")
viikko_valikko = OptionMenu(ikkuna, valittu_viikko, "Ei viikkoja")
viikko_valikko.pack()

tk.Label(ikkuna, text="Valitse kuukausi:", bg="#f0f0f0").pack(pady=(10, 0))
valittu_kk = StringVar(value="Ei kuukausia")
kuukausi_valikko = OptionMenu(ikkuna, valittu_kk, "Ei kuukausia")
kuukausi_valikko.pack(pady=(0, 10))

tk.Button(ikkuna, text="Näytä valittu viikko", command=nayta_viikko, bg="#2196F3", fg="white", width=25).pack(pady=3)
tk.Button(ikkuna, text="Tallenna viikko PDF", command=tallenna_viikko_pdf, bg="#9C27B0", fg="white", width=25).pack(pady=3)
tk.Button(ikkuna, text="Näytä valittu kuukausi", command=nayta_kuukausi, bg="#2196F3", fg="white", width=25).pack(pady=3)
tk.Button(ikkuna, text="Tallenna kuukausi PDF", command=tallenna_kuukausi_pdf, bg="#9C27B0", fg="white", width=25).pack(pady=3)

tk.Button(ikkuna, text="Sulje ohjelma", command=ikkuna.destroy, bg="#333", fg="white", width=25).pack(pady=20)

paivita_tyontekijat()
ikkuna.mainloop()
