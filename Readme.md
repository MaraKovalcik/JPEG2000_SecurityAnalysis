#Analýza zabezpčení formátu JPEG 2000 proti poškození

Tento framework testuje různá nastavení komprese pomocí knihovny Kakadu nebo OpenJPEG
a srovnává jejich výsledky. Pro použití je nutné mít připravenou datovou sadu, nad kterou bude
analýza probíhat. Tato sada musí být připravena v adresáři a obsahovat soubory ve formátu
PPM. Pro správnou funkčnost je třeba mít naistalován python verze 3.6 a balíčky vypsané
v souboru requirements.txt. Pro vytváření grafů je dále třeba mít nainstalován nástroj gnuplot 
a knihovnu Kakadu nebo OpenJPEG, jejíž kompresní a dekompresní nástroj musí být přidán do
cesty v prostředí. Testy probíhaly na operačním systému Ubuntu 16.04 LTS.

## Spuštění analýzy

$ python3 Analyzator.py --directory DIR [--library LIB]

 1) DIR - cesta ke složce s datasetem
 2) LIB - volitelný parametr použité knihovny [kakadu|openjpeg], výchozí je kakadu
 
## Vytvoření grafů 

Po skončení analýzy se budou všechna nasbíraná data nacházet ve šložce output. Dalším krokem
krokem je spuštění skriptu PlotGraphs.py, který agreguje hodnoty pro všechna nasbíraná data
pro každou analyzovanou fotografii a vytvoří grafy.

## Demonstrace vytvoření grafů

Jelikož samotná analýza může trvat i několik dní, lze ve složce demo_graphs nalézt data,
která byla sesbíraná během analýzy, která je popsána v technické zprávě k této práci. Tato
data byla získána při zpracování celého datasetu čítajícího 111 fotografíí v malých i větších
rozlišeních. Celkově tato analýza trvala na mém laptopu něco přes týden.

Prvním krokem je nakopírování obsahu složky output do nadřazené složky Analyzator, což lze 
provést níže přiloženým příkazem.

$ cp -a demo_graphs/output/ .

Při spuštění skriptu PlotGraphs_demo.py se použijí tato data k vytvoření grafů, které lze
nalézt v technické zprávě k této studii.

## CCSDS 122.0

V se složce CCSDS lze najít zdrojové soubory a makefile k použité knihovně BPE pro 
zpracování obrazů ve formátu CCSDS. Provádění této anýlyzy je poněkud těžkopádnější, 
protože tato knihovna pracuje se surovými obrazovými daty bez hlavičky. Po úspěšném přeložení 
zdrojových souborů vznikne spustitelný program bpe, o jehož použití se lze dočíst na 
http://hyperspectral.unl.edu/ nebo v nápovědě programu použitím parametru -h.

$ ./bpe -h

Níže je ukázáno spuštění skriptu pro test formátu JPEG 2000 pro tuto část analýzy, kde FILE 
je jméno testovaného souboru ve formátu PPM. Tento soubor by měl být převeden na stupně šedi,
jelikož pro analýzu pomocí BPE byli použity také pouze obrazy ve stupních šedi kvůli CCSDS 122.0.

$ python3 Analyze_JPEG2000.py FILE

Analýza CCSDS 122.0 se skládala z komprese a poškození vstupního souboru viz použití skriptu 
Analyze_CCSDS122.0.py, dekomprese a následný převod zpět do formátu PPM například pomocí
grafického edtioru GIMP. Poté je možno srovnat kvalitu výsledných obrazů použitím skriptu 
PSNRCalculator.py, kde ORIGINAL je název původního souboru ve formátu PPM a CONTRAST
je cesta k testovanému souboru.

$ python3 PSNRCalculator.py ORIGINAL CONTRAST


Autor: Marek Kovalčík, 2019