# Programmmieraufgabe: Angewandtes programmieren

Dieses repository enthält die Programmieraufgabe des Moduls Angewandtes Programmieren im Sommersemester 2025. 

Die Aufgabenstellung ist in zwei Teile aufgeteilt. Im ersten Teil sollte die zur verfügung gestellte Sample Library vervollständigt werden. Dies erfolgte mit Hilfe der Skripte im *tools*-Ordner.
Im zweiten Teil sollte ein Sample Browser erstellt werden, der Filterung, Plotten, Audiowiedergabe und Ähnlichkeitsberechnung der Samples ermöglichen soll.

## Nutzung des Datenbrowsers

Der Datenbrowser kann über die **main.py**-Funktion aufgerufen werden. Die Daten werden über einen großen DataFrame verarbeitet. Sollte dieser nicht automatisch geladen werden muss die *samples_data.csv* manuell ausgewählt werden. Anschließend muss der Samples-Ordner ausgeählt werden. Um den Browser richtig ausführen zu können muss der Samples-Ordner vollständig sein. Es müssen also alle .wav Dateien vorhanden sein, die in der *samples_data.csv* enthalten sind, damit alle Samples abgespielt werden können.

### Übersicht der Funktionen

#### Audioplayer

Der Audioplayer bietet Start, Stop und Loop Funktionen. Es muss ein Sample in der Tabelle oder im Plot ausgewählt werden um ein Sample abzuspielen.

#### Suchfunktion

Mit Hilfe eines Eingabefelds können alle Samples nach Namen durchsucht werden (z.B. Kick, Synth, ...). Die Tabellenübersicht passt automatisch die Auswahl an die Suche an. Es besteht außerdem die Möglichkeit ein zufälliges Sample aus der Auswahl auszuwählen.

#### Tabellenübersicht

In der Tabellenübersicht werden alle Samples besierend auf der Suchauswahl angezeigt. Über eine Checkbox können alle Features angezeigt werden und durch Klicken auf die Header auf- oder absteigend sortiert werden.

#### Scatter Plot

Der Scatter Plot zeigt die Features der Samples aufeinder aufgetragen an. Dabei können über ein Dropdown-Menü Features für die x- und y-Achse gewählt werden. Hierbei ist es nur möglich Features mit numerischen Werten auszuwählen. Desweiteren kann ein drittes Feature ausgewählt werden und farblich dargestellt werden. Dabei ist Blau ein niedriger Wert und Orange ein hoher Wert.

Der Plot lässt sich beliebig vergößern und verschieben, was hilfreich sein kann, wenn sehr viele Smaples angezeigt werden. Durch klicken auf einen einzelnen Punkt kann außerdem direkt ein Sample ausgewählt werden. Das aktuell ausgewählte Sample wird immer durch einen roten Kreis markiert.

#### Ähnlichkeit der Samples

Wenn ein Sample über die Tabelle oder den Plot ausgewählt wird kann über das untere Menü die Ähnlichkeit zu anderen Samples berechnet werden. Dazu muss in der Liste ein oder mehrere Features ausgewählt werden. Es können auch direkt alle Features ausgewählt werden. Daneben kann die Methode der Distanzberechnung (Euclidean oder Kosinus) ausgewählt werden. Durch Klicken auf den *Similarity Search*-Button werde die Distanzen berechnet und in einer extra Tabelle rechts daneben angezeigt. So kann direkt nach der Distanz sortiert werden - kleinere Distanz bedeutet also ähnlicheres Sample, basierend auf den ausgewählten Features. Die Ähnlichkeit zu anderen Samples kann ebenfalls farblich im Scatter Plot dargestellt werden. Dabei wird die Ähnlichkeit geringer, je roter der Punkt.

## Limitationen und Verbesserung

Bei der Distanzberechnung kann es vorkommen, dass einzelne Samples für bestimmte Features keine Werte haben. In diesem Fall wird der fehlende Wert durch 0 ersetzt um trotzdem eine Berechnung zu ermöglichen. Diese Problem sollte in einer späteren Version eleganter gelöst werden.

Zudem fehlt die in der Aufgabenstellung geforderte Funktion, Start- und Endsektoren bei der Audiowiedergabe anpassen zu können. Hier hatte ich keine schöne und intuitive Einbindung in die GUI finden können. Ein provisorischer Versuch mit Slidern war nicht zufriedenstellend, daher fehlt diese Funktion bisher.

Insgesamt ist der Code in **main.py** sehr lang und dadurch unübersichtlich. Die Auslagerung einiger Funktionen wäre daher sinnvoll.