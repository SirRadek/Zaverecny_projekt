# -*- coding: utf-8 -*-
from datetime import datetime, date

def validace_jmena(jmeno, field_name="Jméno"):
    """Validuje, že jméno či příjmení obsahuje pouze písmena a alespoň 2 znaky.

    Vrací capitalizovanou verzi vstupu.
    """
    ocistene_jmeno = jmeno.strip()
    if len(ocistene_jmeno) < 2:
        raise ValueError(f"{field_name} musí obsahovat alespoň 2 znaky.")
    if not ocistene_jmeno.isalpha():
        raise ValueError(f"{field_name} může obsahovat pouze písmena.")
    return ocistene_jmeno.capitalize()


def validace_narozeni(datum_str):
    """Validuje datum narození.

    Očekává formát DD.MM.RRRR, kontroluje, že jednotlivé části představují kladná čísla,
    a vypočítá věk – maximální povolený věk je 110 let.

    Vrací dvojici (původní řetězec, věk).
    """
    try:
        datum = datetime.strptime(datum_str, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Datum narození musí být ve formátu DD.MM.RRRR.")

    # Zkontrolujeme, že den, měsíc i rok jsou kladná čísla.
    if datum.day <= 0 or datum.month <= 0 or datum.year <= 0:
        raise ValueError("Datum narození musí obsahovat pouze kladná čísla.")

    dnes = date.today()
    vek = dnes.year - datum.year - ((dnes.month, dnes.day) < (datum.month, datum.day))
    if vek >= 110:
        raise ValueError("Maximální povolený věk je 110 let.")
    return datum_str, vek


def validace_cisla(telefon):
    """Validuje telefonní číslo.

    Telefonní číslo musí obsahovat pouze číslice a jeho délka musí být mezi 9 a 15 číslicemi.
    """
    telefon_ocisteny = telefon.strip()
    if not telefon_ocisteny.isdigit():
        raise ValueError("Telefonní číslo musí obsahovat pouze číslice.")
    if not (9 <= len(telefon_ocisteny) <= 15):
        raise ValueError("Telefonní číslo musí mít mezi 9 a 15 číslicemi.")
    return telefon_ocisteny


def validace_emailu(email):
    """Validuje e-mail.

    E-mail musí obsahovat symbol '@'.
    """
    email_ocisteny = email.strip()
    if "@" not in email_ocisteny:
        raise ValueError("E-mail musí obsahovat symbol '@'.")
    return email_ocisteny