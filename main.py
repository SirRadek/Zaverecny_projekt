# -*- coding: utf-8 -*-
import sys
from evidence import SpravcePojistenych  # Třída pro práci s databází
from config import DB_NAME, PASSWORD
from validace import validace_jmena, validace_narozeni, validace_cisla, validace_emailu

def ziskej_validovany_input(prompt, validator, field_label=None):
    """
    Obecná funkce, která opakovaně vyžaduje vstup od uživatele,
    dokud neposkytne platnou hodnotu dle zadaného validačního pravidla.
    """
    while True:
        data = input(prompt).strip()
        try:
            if field_label is None:
                return validator(data)
            else:
                return validator(data, field_label)
        except ValueError as e:
            print("Chyba:", e)

def repeat_cycle_prompt_with_confirm():
    """
    Nabídne otázku, zda chceme pokračovat v aktuální akci.
    Vrací:
      True  -> opakovat akci
      False -> vrátit se do menu
    """
    while True:
        result = input("Chcete pokračovat? Napište Ano/Ne: ").strip()
        if result.lower() == "ano":
            return True
        elif result.lower() == "ne":
            return False
        else:
            print("Neplatná volba. Zadejte 'Ano' nebo 'Ne'.")

def main():
    spravce = SpravcePojistenych(DB_NAME)

    while True:
        print("\n==========================")
        print(" Evidence pojištěných")
        print("==========================")
        print("1. Přidat pojištěného")
        print("2. Seznam pojištěných")
        print("3. Vyhledat pojištěného")
        print("4. Smazat pojištěného")
        print("5. Ukončit")
        volba = input("Vyberte možnost: ")

        if volba == "1":
            heslo = input("Pro přidání pojištěného zadejte heslo: ")
            if heslo != PASSWORD:
                print("Chybné heslo! Návrat do hlavního menu.")
                continue  # Vrací uživatele zpět do hlavního menu

            while True:
                jmeno = ziskej_validovany_input("Zadejte jméno: ", validace_jmena, "Jméno")
                prijmeni = ziskej_validovany_input("Zadejte příjmení: ", validace_jmena, "Příjmení")
                datum_narozeni = ziskej_validovany_input(
                    "Zadejte datum narození (DD.MM.RRRR): ",
                    lambda vstup: validace_narozeni(vstup)[0]
                )
                telefon = ziskej_validovany_input("Zadejte telefonní číslo: ", validace_cisla)
                email = ziskej_validovany_input("Zadejte e-mail: ", validace_emailu)

                try:
                    spravce.pridat_pojisteneho(jmeno, prijmeni, datum_narozeni, telefon, email)
                    print("Pojištěný byl úspěšně přidán.")
                except ValueError as err:
                    print("Chyba při přidávání:", err)

                if not repeat_cycle_prompt_with_confirm():
                    break

        elif volba == "2":
            vystup = spravce.seznam_pojistenych()
            print("\n" + vystup)
            if not repeat_cycle_prompt_with_confirm():
                continue

        elif volba == "3":
            while True:
                hledani = input("Zadejte hledaný výraz (ID, jméno, atd.): ")
                vysledek = spravce.vyhledat_pojisteneho(hledani)
                if vysledek:
                    print("\n" + vysledek)
                else:
                    print("Nenalezen žádný odpovídající záznam.")
                if not repeat_cycle_prompt_with_confirm():
                    break

        elif volba == "4":
            while True:
                heslo = input("Pro smazání zadejte heslo: ")
                if heslo != PASSWORD:
                    print("Chybné heslo!")
                    if not repeat_cycle_prompt_with_confirm():
                        break
                    continue
                id_str = input("Zadejte ID pojištěného k smazání: ")
                try:
                    pojisteny_id = int(id_str)
                except ValueError:
                    print("Neplatné ID, zadejte prosím číslo.")
                    if not repeat_cycle_prompt_with_confirm():
                        break
                    continue
                spravce.smazat_pojisteneho(pojisteny_id)
                print("Pojištěný byl úspěšně smazán.")
                if not repeat_cycle_prompt_with_confirm():
                    break

        elif volba == "5":
            print("Ukončuji aplikaci...")
            sys.exit(0)

        else:
            print("Neplatná volba, zkuste to znovu.")
            continue

if __name__ == '__main__':
    main()