# Smarte Abfüllanlage  

### Aufgabenstellung

#### 1. **Station 1: Schreiben der RFID-Tags**
Ein Python-Modul `station1.py` soll entwickelt werden, das die Flaschen-ID auf den RFID-Tag einer Flasche schreibt. Hierbei wird die erste noch nicht vergebene Flaschen-ID genutzt.  
- Die Funktionalität umfasst die Dokumentation des Schreibvorgangs sowohl im erfolgreichen als auch im nicht erfolgreichen Fall.  
- Der Ablauf wird in einer Log-Datei `station1.log` protokolliert, die den Start der Station sowie die Ergebnisse des Schreibens festhält.  

#### 2. **Station 2: Ermittlung der Füllmenge**
Ein weiteres Python-Modul `station2.py` soll programmiert werden, das anhand der Flaschen-ID vom RFID-Tag die korrekte Füllmenge für die jeweilige Flasche ermittelt.  
- Es werden mindestens zwei verschiedene Flaschen und deren Füllmengen berücksichtigt.  
- Der Ablauf wird in einer Log-Datei `station2.log` dokumentiert, die die Füllmengen und den Prozessverlauf beschreibt.

#### 3. **Zustandsübergangsdiagramme für Fehlermanagement**
Für beide Stationen sollen Zustandsübergangsdiagramme erstellt werden, die den Ablauf und das funktionierende Fehlermanagement abbilden.  
- Die Diagramme dokumentieren mögliche Fehlerzustände (z. B. Timeout, unlesbarer RFID-Tag) und wie diese behandelt werden.  
- Sie werden als Teil der Dokumentation in die `README.md` des Projektrepositories eingefügt.

#### 4. **State-Machine für Fehlermanagement**
Die Module `station1.py` und `station2.py` sollen jeweils um eine State-Machine erweitert werden, um ein sinnvolles Fehlermanagement zu ermöglichen.  
- Die State-Machines stellen sicher, dass z. B. beim Entfernen eines RFID-Tags während des Prozesses oder bei anderen Fehlern geeignete Reaktionen ausgelöst werden.  
- Fehlerzustände und Übergänge zwischen den Zuständen werden klar definiert.

#### 5. **Bonus: QR-Code für abgefüllte Flaschen**
Zusätzlich wird eine Bonusfunktion implementiert, bei der für alle korrekt abgefüllten Flaschen ein QR-Code generiert wird. Dieser QR-Code enthält:
- Die Flaschen-ID
- Die Rezeptnummer
- Das Abfülldatum  

## Station 1

![Station 1 Diagramm](//www.plantuml.com/plantuml/png/VP71IlGm58NtVOgp_g6BVsRS595Xg888RYgu41UPzamR9abBUhFmVNmJNypKcb8KPzNSVkUxzyBTZwAy16koJZS4xI1lQ3ZMNW-YUvUz_7j5dj-W4YNydsNp5mMUeqUeSCB3z4eWHJV5_1_qP-MSp7mJnQhkFFNnWdjLu4bRza4IkSvJrqLtSBhk1FIdthIUiKWpKf_jAlqxjqN4mrJJ4_SbWcjGAWaMsaqFkgDovnHUBLSUC5xUOYtiVWZhQ0hS-b5e377WA1_lejlWsYpDM-WTEqDlQPe5xxwk4wzKeA9hY4SL9qqxVUj_ytsiWpMV)
### Zusammenfassung der implementierten Funktionen

Das Python-Modul `station_1_state_machine.py` implementiert eine State-Machine zur Verwaltung des RFID-Tagging-Prozesses für Flaschen. Es erfüllt die Aufgabenstellung, indem es sowohl erfolgreiche als auch fehlerhafte Szenarien abdeckt. Die wichtigsten Funktionen und Mechanismen sind:

#### 1. **State-Machine-Architektur**
- Die State-Machine besteht aus sechs Zuständen (`State0` bis `State5`), die den gesamten Prozess strukturieren:
  - **State0:** Initialisierung von RFID-Reader und Datenbank.
  - **State1:** Warten auf eine RFID-Karte.
  - **State2:** Überprüfung des RFID-Tags und Zuordnung einer neuen Flaschen-ID.
  - **State3:** Aktualisierung der Datenbank mit der Flaschen-ID und dem Zeitstempel.
  - **State4:** Abschluss eines erfolgreichen Prozesses und Neustart für die nächste Flasche.
  - **State5:** Fehlerbehandlung und Abbruch des Prozesses.

#### 2. **Fehlermanagement**
- Verschiedene Fehlerfälle, wie z. B. Verbindungsprobleme mit der Datenbank, fehlerhaftes Lesen oder Schreiben von RFID-Tags und fehlende ungetaggte Flaschen, werden erkannt und entsprechend behandelt.
- Das System schreibt Fehlerberichte in das Log-File `station1.log` und beendet den Prozess sauber.

#### 3. **Logging**
- Alle relevanten Vorgänge, einschließlich erfolgreicher und fehlerhafter Schritte, werden im Log-File `station1.log` dokumentiert.
- Das Log-File enthält Informationen wie Startzeit, Detektion der Karte, erfolgreiche Tagging-Prozesse und Fehlermeldungen.

#### 4. **Interaktion mit der Datenbank**
- Es wird eine SQLite-Datenbank verwendet, um Flaschen-IDs und deren Tagging-Status zu speichern.
- Die Datenbank wird bei erfolgreichem Tagging mit einem Zeitstempel und einem Status-Update aktualisiert.

#### 5. **Wiederholung und Robustheit**
- Nach einem erfolgreichen Prozess kehrt das System automatisch zu `State1` zurück, um die nächste RFID-Karte zu bearbeiten.
- Bei auftretenden Fehlern, wie z. B. Zeitüberschreitungen oder fehlerhaftem RFID-Tagging, versucht das System, in einen stabilen Zustand zurückzukehren.

---

### Erfüllung der Aufgabenstellung

Die Aufgabenstellung wurde vollständig umgesetzt:
1. **Flaschen-ID auf RFID-Tag schreiben:** Erfolgreich umgesetzt. Eine neue Flaschen-ID wird aus der Datenbank abgerufen und auf den RFID-Chip geschrieben.
2. **Dokumentation mit Log-File:** Alle relevanten Informationen, einschließlich Erfolg und Fehler, werden in der Datei `station1.log` protokolliert.
3. **Fehlermanagement:** Fehler wie Datenbankprobleme, unlesbare RFID-Karten und fehlende ungetaggte Flaschen werden erkannt und entsprechend behandelt.
4. **State-Machine:** Eine sinnvolle State-Machine wurde implementiert, die den gesamten Prozess abbildet und Fehlerfälle berücksichtigt.

---




## Station 2
![Station 2 Diagramm](//www.plantuml.com/plantuml/png/RP4_JyGm3CNtV0hFI3Vmfmi3EX2w1IP0Oa0CwVKrhKXTb3WBdnxtL4TGtLRr_TxFZhpFufEKARgFYq_QtT6hUC4bERT-tDAx0Y1VUZf4duy3B3BwIg4r8gGlponRf57aRPmm5t6kbfvEveWCjfyxQrpN7AcVOqWOZmC5dAURIhDYebnVkDk0zg3dHR62V-JErS4l-C6ta2-P7X_8jwdqO8khwyR8Vnh50yuNcbhOhkdSnZXoFwV9opWpU5aae0KRjHZrNahVQ-9Rd8Rg0UASywAhumuO8bABmNCN2mTBp6041Ko87SJjmLsPuYy0)
### Zusammenfassung der implementierten Funktionen für Station 2

Das Python-Modul `station_2_state_machine.py` implementiert eine State-Machine zur Bestimmung der Füllmengen basierend auf RFID-Tags und zur Generierung eines QR-Codes für korrekt abgefüllte Flaschen. Es erfüllt die Aufgabenstellung durch klare und robuste Zustandslogik. Die wichtigsten Funktionen sind:

#### 1. **State-Machine-Architektur**
- Die State-Machine besteht aus sechs Zuständen (`State0` bis `State5`), die den Prozess strukturieren:
  - **State0:** Initialisierung von RFID-Reader und Datenbankverbindung.
  - **State1:** Warten auf das Vorhalten einer RFID-Karte.
  - **State2:** Auslesen der Flaschen-ID vom RFID-Tag.
  - **State3:** Abrufen der Rezeptdetails aus der Datenbank.
  - **State4:** Ausgeben der Füllmengen und Generieren eines QR-Codes.
  - **State5:** Fehlerbehandlung und Abbruch des Prozesses.

#### 2. **Füllmengenberechnung**
- Die Rezeptdetails, die Granulat-ID und die benötigte Menge umfassen, werden aus der Datenbank abgerufen.
- Alle Füllmengen werden geloggt und in einer standardisierten Form ausgegeben.

#### 3. **QR-Code-Generierung**
- Für jede korrekt abgefüllte Flasche wird ein QR-Code erstellt, der die Flaschen-ID, die Rezept-ID und das Datum enthält.
- Der QR-Code wird als PNG-Datei im Verzeichnis `qr_codes` gespeichert.

  
![QR-Code Bottle 1](qr_codes/qr_bottle_1.png)
![QR-Code Bottle 2](qr_codes/qr_bottle_2.png)
#### 4. **Logging**
- Alle Vorgänge und Fehler werden detailliert im Log-File `station2.log` dokumentiert.
- Das Log-File enthält:
  - Informationen zu erfolgreich gelesenen RFID-Tags.
  - Details zu den Füllmengen der Flasche.
  - Speicherort des QR-Codes.
  - Fehlerberichte bei Problemen.

#### 5. **Fehlermanagement**
- Fehler wie nicht lesbare RFID-Tags, fehlende Rezeptdetails oder Probleme bei der QR-Code-Generierung werden erkannt und behandelt.
- Bei Fehlern wird der Prozess sauber abgebrochen und ein Eintrag im Log-File erstellt.

---

### Erfüllung der Aufgabenstellung

Die Aufgabenstellung wurde vollständig umgesetzt:
1. **RFID-Tag-Lesen und Füllmengenberechnung:** Die Flaschen-ID wird erfolgreich vom RFID-Tag ausgelesen, und die entsprechenden Füllmengen werden korrekt aus der Datenbank abgerufen.
2. **Dokumentation mit Log-File:** Alle relevanten Schritte, einschließlich Erfolg und Fehler, werden in der Datei `station2.log` protokolliert.
3. **QR-Code-Generierung:** Ein QR-Code mit Flaschen-ID, Rezept-ID und Datum wird erfolgreich für korrekt abgefüllte Flaschen erstellt und gespeichert.
4. **State-Machine für Fehlerfälle:** Fehler wie Zeitüberschreitungen oder fehlerhafte RFID-Chips werden erkannt und entsprechend behandelt.

---
### Zusätzliche Python-Skripte und ihre Funktionen

Neben dem Hauptskript  wurden weitere unterstützende Python-Skripte erstellt, die nicht explizit in der Aufgabenstellung verlangt wurden. Diese Skripte erweitern die Funktionalität und erleichtern die Arbeit mit der Datenbank und dem RFID-System. Eine Übersicht:

#### 1. **`inspect_database.py`**
- **Funktion:** Anzeigen des Inhalts der Datenbank-Tabellen.
- **Details:**
  - Greift auf die Tabellen `Flasche` und `Rezept_besteht_aus_Granulat` zu.
  - Zeigt die Inhalte in einer gut formatierten Konsolenausgabe.
  - Bietet eine schnelle Möglichkeit, die aktuelle Datenlage der Flaschen- und Rezeptdatenbank zu inspizieren.

#### 2. **`reset_ID_on_RFID_chip.py`**
- **Funktion:** Zurücksetzen von Daten auf dem RFID-Tag.
- **Details:**
  - Nutzt die PN532-Schnittstelle, um Blöcke eines RFID-Tags zu lesen, zu schreiben und zurückzusetzen.
  - Setzt den Inhalt eines spezifischen Blocks (z. B. Block 2) auf Null.
  - Ermöglicht das vollständige Zurücksetzen eines Tags durch Iteration über alle Blöcke.
  - Bietet nützliche Log-Meldungen für den Fortschritt und mögliche Fehler.

#### 3. **`reset_database.py`**
- **Funktion:** Zurücksetzen der `Flasche`-Tabelle in der Datenbank.
- **Details:**
  - Setzt die Spalte `Tagged_Date` auf `0` und `has_error` auf `0`.
  - Ermöglicht es, die Datenbank für Testzwecke oder den erneuten Gebrauch schnell in den Ausgangszustand zu bringen.
  - Ideal für die Vorbereitung neuer Testszenarien.

---

### Zweck und Nutzen der zusätzlichen Skripte

Die Skripte wurden entwickelt, um typische Anforderungen während der Entwicklung, Fehlersuche und Datenpflege zu unterstützen:
1. **Datenbank-Management:** 
   - `inspect_database.py` erlaubt schnelle Überprüfungen der Datensätze.
   - `reset_database.py` bietet eine einfache Möglichkeit, die Datenbank auf einen sauberen Zustand zurückzusetzen.

2. **RFID-Datenpflege:**
   - Mit `reset_ID_on_RFID_chip.py` können RFID-Tags schnell und effizient zurückgesetzt oder neu beschrieben werden.

3. **Flexibilität:** 
   - Diese Skripte verbessern die Modularität und erleichtern sowohl die Fehlerbehebung als auch die Wiederverwendung von RFID-Chips und Datenbankeinträgen.

---






