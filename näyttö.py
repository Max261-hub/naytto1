import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import calendar
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===============================
# PÄÄIKKUNA
# ===============================
root = tk.Tk()
root.title("Työaikaseuranta")
root.geometry("500x600")

tiedosto = "tyoaika.txt"

# ===============================
# APUFUNKTIO: Päivämäärän tunnistus
# ===============================
def parse_pvm(pvm_str):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(pvm_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Virheellinen päivämäärä: {pvm_str}")

# ===============================
# TIETOJEN TALLENNUS
# ===============================
def tallenna_tiedot():
    nimi = nimi_var.get().strip()
    pvm = pvm_var.get().strip()
    tunnit = tunnit_var.get().strip()
    palkka = palkka_var.get().strip()

    if not (nimi and pvm and tunnit and palkka):
        messagebox.showwarning("Virhe", "Täytä kaikki kentät ennen tallennusta.")
        return

    with open(tiedosto, "a", encoding="utf-8") as f:
        f.write(f"{nimi};{pvm};{tunnit};{palkka}\n")

    messagebox.showinfo("Tallennettu", "Tiedot tallennettu onnistuneesti!")
    nimi_var.set("")
    pvm_var.set("")
    tunnit_var.set("")
    palkka_var.set("")
    paivita_tyontekijat()

# ===============================
# TIETOJEN POISTO
# ===============================
def poista_tiedot():
    nimi = valittu_tyontekija.get()
    if not nimi:
        messagebox.showwarning("Virhe", "Valitse työntekijä ennen poistamista!")
        return

    valinta = yhteenveto_valinta.get()

    if not os.path.exists(tiedosto):
        messagebox.showwarning("Virhe", "Tiedostoa ei löydy.")
        return

    with open(tiedosto, "r", encoding="utf-8") as f:
        rivit = f.readlines()

    poistettavat = []
    nyt = datetime.now()
    for r in rivit:
        osat = r.strip().split(";")
        if len(osat) < 4:
            continue
        n, pvm_str, _, _ = osat
        try:
            pvm = parse_pvm(pvm_str)
        except ValueError:
            continue

        if n == nimi:
            if valinta == "Päivä" and pvm.date() == nyt.date():
                poistettavat.append(r)
            elif valinta == "Viikko" and pvm.isocalendar()[1] == nyt.isocalendar()[1]:
                poistettavat.append(r)
            elif valinta == "Kuukausi" and pvm.month == nyt.month and pvm.year == nyt.year:
                poistettavat.append(r)
            elif valinta == "Vuosi" and pvm.year == nyt.year:
                poistettavat.append(r)

    uudet_rivit = [r for r in rivit if r not in poistettavat]
    with open(tiedosto, "w", encoding="utf-8") as f:
        f.writelines(uudet_rivit)

    messagebox.showinfo("Poistettu", f"Poistettu {len(poistettavat)} merkintää ({valinta}) työntekijältä {nimi}.")

# ===============================
# TYÖNTEKIJÄLISTA
# ===============================
def paivita_tyontekijat():
    if not os.path.exists(tiedosto):
        return
    with open(tiedosto, "r", encoding="utf-8") as f:
        nimet = sorted(set(r.split(";")[0] for r in f if ";" in r))
    tyontekija_menu["values"] = nimet

# ===============================
# YHTEENVETOLASKENTA
# ===============================
def laske_yhteenveto(tyontekija, tyyppi):
    if not os.path.exists(tiedosto):
        return None

    with open(tiedosto, "r", encoding="utf-8") as f:
        rivit = f.readlines()

    nyt = datetime.now()
    tunnit_yht = 0.0
    palkka_yht = 0.0

    for r in rivit:
        osat = r.strip().split(";")
        if len(osat) < 4:
            continue
        nimi, pvm_str, tunnit, palkka = osat
        if nimi != tyontekija:
            continue

        try:
            pvm = parse_pvm(pvm_str)
        except ValueError:
            continue

        if tyyppi == "Päivä" and pvm.date() == nyt.date():
            tunnit_yht += float(tunnit)
            palkka_yht += float(palkka)
        elif tyyppi == "Viikko" and pvm.isocalendar()[1] == nyt.isocalendar()[1]:
            tunnit_yht += float(tunnit)
            palkka_yht += float(palkka)
        elif tyyppi == "Kuukausi" and pvm.month == nyt.month and pvm.year == nyt.year:
            tunnit_yht += float(tunnit)
            palkka_yht += float(palkka)
        elif tyyppi == "Vuosi" and pvm.year == nyt.year:
            tunnit_yht += float(tunnit)
            palkka_yht += float(palkka)

    return {"tunnit": tunnit_yht, "ansiot": palkka_yht}

# ===============================
# PDF-TULOSTUS
# ===============================
def tallenna_yhteenveto_pdf():
    nimi = valittu_tyontekija.get()
    tyyppi = yhteenveto_valinta.get()

    if not nimi:
        messagebox.showwarning("Virhe", "Valitse työntekijä ennen tallennusta.")
        return

    tulos = laske_yhteenveto(nimi, tyyppi)
    if not tulos:
        messagebox.showinfo("Tietoja ei löytynyt", "Ei tallennettuja tietoja.")
        return

    pdf_nimi = f"Yhteenveto_{nimi}_{tyyppi}.pdf"
    c = canvas.Canvas(pdf_nimi, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"{tyyppi}-yhteenveto työntekijälle {nimi}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Työtunnit yhteensä: {tulos['tunnit']:.2f}")
    c.drawString(100, 750, f"Ansiot yhteensä: {tulos['ansiot']:.2f} €")
    c.save()

    messagebox.showinfo("PDF luotu", f"PDF tallennettu nimellä {pdf_nimi}")

# ===============================
# SULJE OHJELMA
# ===============================
def sulje_ohjelma():
    root.destroy()

# ===============================
# KÄYTTÖLIITTYMÄ
# ===============================
tk.Label(root, text="Nimi:").pack()
nimi_var = tk.StringVar()
tk.Entry(root, textvariable=nimi_var).pack()

tk.Label(root, text="Päivämäärä (pp.kk.vvvv tai vvvv-kk-pp):").pack()
pvm_var = tk.StringVar()
tk.Entry(root, textvariable=pvm_var).pack()

tk.Label(root, text="Tunnit:").pack()
tunnit_var = tk.StringVar()
tk.Entry(root, textvariable=tunnit_var).pack()

tk.Label(root, text="Palkka (€):").pack()
palkka_var = tk.StringVar()
tk.Entry(root, textvariable=palkka_var).pack()

tk.Button(root, text="Tallenna tiedot", bg="green", fg="white", command=tallenna_tiedot).pack(pady=5)

tk.Label(root, text="Valitse työntekijä:").pack()
valittu_tyontekija = tk.StringVar()
tyontekija_menu = ttk.Combobox(root, textvariable=valittu_tyontekija, state="readonly", width=25)
tyontekija_menu.pack(pady=5)
paivita_tyontekijat()

tk.Label(root, text="Valitse tarkastelu:").pack()
yhteenveto_valinta = tk.StringVar()
yhteenveto_valinta.set("Päivä")
valinta_menu = ttk.Combobox(root, textvariable=yhteenveto_valinta, values=["Päivä", "Viikko", "Kuukausi", "Vuosi"], state="readonly", width=20)
valinta_menu.pack(pady=5)

tk.Button(root, text="Näytä yhteenveto", bg="blue", fg="white",
          command=lambda: messagebox.showinfo("Yhteenveto", 
              f"{yhteenveto_valinta.get()} yhteenveto työntekijälle {valittu_tyontekija.get()}")).pack(pady=5)

tk.Button(root, text="Tallenna yhteenveto PDF", bg="orange", fg="black", command=tallenna_yhteenveto_pdf).pack(pady=5)
tk.Button(root, text="Poista tiedot", bg="red", fg="white", command=poista_tiedot).pack(pady=5)
tk.Button(root, text="Sulje ohjelma", bg="gray", fg="white", command=sulje_ohjelma).pack(pady=10)

root.mainloop()
