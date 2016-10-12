# gede
Looks for german declination of given word.

It uses `http://de.wiktionary.org/w/api.php` API to get the information.

## Installation

It requires some third party libs: click, requests, tabulate and bs4. 

To install `gede` and collect the requirements:

```
$ git clone https://github.com/Woraufhin/gede.git
$ cd gede
$ pip install -e .
$ gede Gemüt
           Singular                Plural
---------  ----------------------  ------------
Nominativ  das Gemüt               die Gemüter
Genitiv    des Gemüts des Gemütes  der Gemüter
Dativ      dem Gemüt dem Gemüte    den Gemütern
Akkusativ  das Gemüt               die Gemüter
```

## Usage
```
$ gede --help
Usage: gede [OPTIONS] WORD

  Retrieve declination for given word in german.

Options:
  --table-fmt [fancy_grid|grid|html|latex|latex_booktabs|mediawiki|orgtbl|pipe|plain|psql|rst|simple|tsv]
                                  Visual text formatting for the output table
```
Rules for looking german words are the same as for any dictionary:
* **Substantive**: singular, capital first letter.
* **Adjective**: nominativ, singular, masculine.
* **Verb**: active voice, infinitive.
* **Pronouns** and **articles**: in any morphological accident.

`gede` supports all types of output format offered by `tabulate` lib.

## Examples

* **Substantive**:
```
$ gede Apfel
           Singular    Plural
---------  ----------  ----------
Nominativ  der Apfel   die Äpfel
Genitiv    des Apfels  der Äpfel
Dativ      dem Apfel   den Äpfeln
Akkusativ  den Apfel   die Äpfel
```
* **Pronoun**:
```
$ gede euch
           Singular    Plural
---------  ----------  --------
Nominativ  du          ihr
Genitiv    deiner      euer
Dativ      dir         euch
Akkusativ  dich        euch
```

* **Article**:
```
$ gede der
           Singular                        Plural
---------  ----------  ---------  -------  --------
           Maskulinum  Femininum  Neutrum  —
Nominativ  der         die        das      die
Genitiv    des         der        des      der
Dativ      dem         der        dem      den
Akkusativ  den         die        das      die
```

* **Adjective**:
```
$ gede schnell --table-fmt fancy_grid
╒═══════════╤══════════════╤════════════════╕
│ Positiv   │ Komparativ   │ Superlativ     │
╞═══════════╪══════════════╪════════════════╡
│ schnell   │ schneller    │ am schnellsten │
╘═══════════╧══════════════╧════════════════╛
```

* **Verb**:
```
$ gede können
               Person       Wortform
-------------  -----------  ----------  ---------
Präsens        ich          kann
               du           kannst
               er, sie, es  kann
Präteritum     ich          konnte
Konjunktiv II  ich          könnte
Imperativ      Singular     —
               Plural       —
Perfekt        Partizip II              Hilfsverb
               gekonnt                  haben
```


