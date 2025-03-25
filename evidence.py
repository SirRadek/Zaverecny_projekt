# -*- coding: utf-8 -*-
import sqlite3
import string
from datetime import datetime, date
from validace import validace_jmena, validace_narozeni, validace_cisla, validace_emailu
from config import DB_NAME


class SpravcePojistenych:
    """Třída pro správu pojištěných."""

    def __init__(self, databaze=DB_NAME):
        self.cesta_databaze = databaze
        self._inicializovat_databazi()

    def _otevrit_spojeni(self):
        """Vrací nové spojení s databází s nastaveným kódováním a registrovanou funkcí pro odstranění interpunkce."""
        conn = sqlite3.connect(self.cesta_databaze)
        conn.execute("PRAGMA encoding = 'UTF-8'")

        # Definice funkce pro odstranění interpunkce.
        def remove_punct(text):
            if text is None:
                return None
            return text.translate(str.maketrans('', '', string.punctuation))

        # Registrovat funkci v SQLite, abychom ji mohli použít v SQL dotazech.
        conn.create_function("remove_punct", 1, remove_punct)
        return conn

    def _inicializovat_databazi(self):
        """Vytvoří databázi a tabulku pojistenců, pokud ještě neexistuje."""
        with self._otevrit_spojeni() as spojeni:
            spojeni.execute("""
                CREATE TABLE IF NOT EXISTS pojistenci (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jmeno TEXT NOT NULL,
                    prijmeni TEXT NOT NULL,
                    datum_narozeni TEXT NOT NULL,
                    telefonni_cislo TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE
                )
            """)

    @staticmethod
    def _spocitej_vek(datum_narozeni):
        """
        Vypočítá věk na základě data narození.
        Očekává formát "dd.mm.yyyy" nebo "YYYY-MM-DD".
        """
        try:
            narozeni = datetime.strptime(datum_narozeni, "%d.%m.%Y")
        except ValueError:
            narozeni = datetime.strptime(datum_narozeni, "%Y-%m-%d")
        dnes = date.today()
        return dnes.year - narozeni.year - ((dnes.month, dnes.day) < (narozeni.month, narozeni.day))

    def pridat_pojisteneho(self, jmeno, prijmeni, datum_narozeni, telefonni_cislo, email):
        """
        Přidá nového pojištěného do databáze pomocí jediného SQL příkazu.
        Vstupní hodnoty jsou validovány.
        """
        validni_jmeno = validace_jmena(jmeno, "Jméno")
        validni_prijmeni = validace_jmena(prijmeni, "Příjmení")
        validni_datum, _ = validace_narozeni(datum_narozeni)
        validni_tel = validace_cisla(telefonni_cislo)
        validni_email = validace_emailu(email)
        try:
            with self._otevrit_spojeni() as spojeni:
                spojeni.execute("""
                    INSERT INTO pojistenci (jmeno, prijmeni, datum_narozeni, telefonni_cislo, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (validni_jmeno, validni_prijmeni, validni_datum, validni_tel, validni_email))
        except sqlite3.IntegrityError:
            raise ValueError(
                "Telefonní číslo nebo e-mail již existují, nebo záznam se stejnými údaji byl již evidován.")

    def seznam_pojistenych(self):
        """
        Vrací seznam všech pojištěných s vypočteným věkem.
        """
        with self._otevrit_spojeni() as spojeni:
            zaznamy = spojeni.execute("SELECT * FROM pojistenci ORDER BY id ASC").fetchall()
        if not zaznamy:
            return "Žádní pojištěnci nejsou evidováni."
        vystup = "\n".join(
            f"ID: {zaznam[0]} | {zaznam[1]} {zaznam[2]} | Věk: {SpravcePojistenych._spocitej_vek(zaznam[3])} | Tel.: {zaznam[4]} | E-mail: {zaznam[5]}"
            for zaznam in zaznamy
        )
        return f"{vystup}\nCelkový počet pojištěných: {len(zaznamy)}"

    def vyhledat_pojisteneho(self, hledani):
        """
        Vyhledá pojištěného podle zadaného kritéria (jméno, příjmení, datum narození,
        telefonní číslo, e-mail nebo ID) jediným SQL dotazem.
        Vyhledávání je nyní case-insensitive a ignoruje i interpunkci.
        """
        # Převod prvního písmene na velké, pokud uživatel zadá malé.
        if hledani and isinstance(hledani, str) and hledani[0].islower():
            hledani = hledani[0].upper() + hledani[1:]

        try:
            hledani_id = int(hledani)
        except ValueError:
            hledani_id = -1

        with self._otevrit_spojeni() as spojeni:
            query = """
                SELECT * FROM pojistenci
                WHERE remove_punct(jmeno) LIKE '%' || remove_punct(?) || '%' COLLATE NOCASE
                   OR remove_punct(prijmeni) LIKE '%' || remove_punct(?) || '%' COLLATE NOCASE
                   OR remove_punct(datum_narozeni) LIKE '%' || remove_punct(?) || '%'
                   OR remove_punct(telefonni_cislo) LIKE '%' || remove_punct(?) || '%'
                   OR remove_punct(email) LIKE '%' || remove_punct(?) || '%' COLLATE NOCASE
                   OR id = ?
            """
            vysledky = spojeni.execute(query, (hledani, hledani, hledani, hledani, hledani, hledani_id)).fetchall()

        if not vysledky:
            return None
        return "\n".join(
            f"ID: {zaznam[0]} | {zaznam[1]} {zaznam[2]} | Věk: {SpravcePojistenych._spocitej_vek(zaznam[3])} | Tel.: {zaznam[4]} | E-mail: {zaznam[5]}"
            for zaznam in vysledky
        )

    def smazat_pojisteneho(self, pojisteny_id):
        """
        Smaže pojištěného s potvrzením od uživatele.
        """
        if input(f"Opravdu chcete smazat pojištěného s ID {pojisteny_id}? (ano/ne): ").lower() != "ano":
            print("Smazání bylo zrušeno.")
            return False
        with self._otevrit_spojeni() as spojeni:
            kurzor = spojeni.execute("DELETE FROM pojistenci WHERE id = ?", (pojisteny_id,))
            if kurzor.rowcount == 0:
                print("Záznam s tímto ID nebyl nalezen.")
                return False
            return True