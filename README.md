# Programmmieraufgabe 1: Angewandtes programmieren

Als Datengrundlage nutzen wir die Samples der Webseite musicradar

https://www.musicradar.com/news/tech/free-music-samples-royalty-free-loops-hits-and-multis-to-download-sampleradar


(Sie müssen diese nicht runterladen, aber ich gebe Ihnen ein Skript, dass das könnte, da ich Ihnen die Daten eigentlich nicht direkt geben darf)
zusätzlich bekommen Sie eine zip Datei mit vielen Analysedaten dieser Datenbank (Audiocommons, pytimbre und Chroma).
(Die Daten sind in beide Richtungen nicht vollständig, Es gibt also wavedateien ohne analyse und Analysedaten ohne wavefiles)

## Aufgaben

### Daten vervollständigen

Vervollständigen Sie den Datensatz zumindest in die Richtung Audio. Also laden Sie die Datensätze herunter zu denen Sie Analysedaten vorliegen haben. Zusatzaufgabe (echte Kür): Nutzen Sie die Werkzeuge zur Berechnung der Feature-Files und vervollständigen die Datenbank auch in die andere Richtung.

### Aufbau Datenbrowser 

Programmieren Sie einen Datenbrowser für den Datensatz: Dieser sollte die folgenden Dinge können:

1. Auswahl / Reduktion von Dateien nach einem gegebenen Reg-Ex Schema (Editierfeld)
2. 2 dimensionale Visualisierung von 2 beliebigen Merkmalen auf der x bzw. y Achse (Automatische kluge Skalierung in beide Richtungen). Zusatz: 3dim mit 3 Merkmalen. Jeder Datenpunkt entspricht einer Datei. Evtl das 3. bzw. 4 Merkmal als Farbe kodieren.
3. Audio-Player, der eine angewählte (Auswahl in der Visualisierung oder in der Dateiliste) Datei abspielt (mit Anfangs und Endselektoren und Loop Funktion)


Empfehlung: Nutzen Sie intern ein großes Pandas Dataframe für alles. 
Wie Sie Teil 2 lösen bleibt Ihnen überlassen, aber hier gibt es viel Optimierungsmöglichkeiten. Wichtig ist, dass immer die aktuelle Liste genutzt wird, also zB nach der Regex Auswahl.


# Programmieraufgabe 2

Erweitern Sie das Programm um die folgende Funktion:

1. Liste (Auswahl-buttons) aller vorhandenen Merkmalen, die einzeln angewählt werden können
2. Berechnung eines Abstandsmaß zu einem vorher ausgewählten File
3. Ausgabe einer sortierten Liste (Absteigend nach Distanz), so dass man mit der Play Funktion schnell überprüfen kann, ob Werte mit einem kleinen Abstand tatsächlich ähnlich klingen.
4. Optional: Kodierung der Distanz als Farbe in der 2d/3d Darstellung von Aufgabe 1