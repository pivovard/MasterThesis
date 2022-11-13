# Detekce vybraných aktivit diabetického pacienta 1. typu
Autor: Bc. David Pivovar
Vedoucí práce: doc. Ing. Tomáš Koutný, PH.D.

## Adresářová struktura
- doc
  - zdrojové tex soubory
  - poster
  - posudky
  - prezentace
- cho_detection - python skripty pro zpracovani dat a trenovani neuronove site (vstupní data pacientů není možné přiložit z důvodu autorských práv)
- model - natrénované keras modely GRU sítě
- results - vysledky provedených experimentů
- scgms_cho_module
  - setup - konfigurační soubory
  - src - zdrojové soubory filtrů pro SmartCGMS
  - CMakeLists.txt
  - detection.dll - knihovna filtrů pro SmartCGMS

## Knihovny, kompilace, spuštění
SmartCGMS je dostupný na https://diabetes.zcu.cz/smartcgms. Knihovna je kompilována v C++ 17. Pro kompilaci jsou nutné header soubory SmartCGMS a knihovny [VisualLeakDetector](https://kinddragon.github.io/vld/), [frugally-deep](https://github.com/Dobiasd/frugally-deep), [Eigen](https://gitlab.com/libeigen/eigen), [FunctionalPlus](https://github.com/Dobiasd/FunctionalPlus) a [json](https://github.com/nlohmann/json). K dispozici je CMake skript.
Vytvořená dynamická knihovna `detection.dll` se umístí do složky filters. Grafické rozhraní SmartCGMS se spustí programem `gpredict3.exe`, konzolová verze programem `console3.exe`.

## Nastavení filtrů
### Savitzky-Golay filtr
Filtr pro vyhlazení dat.
- Signal - zdrojový signál pro vyhlazení
- Window size - velikost okna Savitzky-Golay filtru
- Degre - stupeň polynomu

Filtr posílá vyhlazená data v signálu `Savgol signal`. V případě použití více filtrů je nutné výstupní signál přemapovat.

### CHO detection
Filtr detekce příjmu karbohydrátů.
- Signal - detekovaný signál
- Window size - velikost klouzavého okénka
- Detect edges - detekce vzestupných hran
- Detect descending edges - detekce sestupných hran
- Rise threshold - threshold pro určení míry stoupání/klesání v čase
- Use RNN - použití rekurentní neuronové sítě
- RNN model file path - cesta k souboru s natrénovaným keras modelem převedeným do formátu pro frugally-deep
- RNN threshold - threshold detekce neuronovou sítí
- Thresholds
	- Threshold Low - threshold malé změny IST
	- Weight Low - váha malé změny IST
	- Threshold High - threshold velké změny IST
	- Weight High - váha velké změny IST

Filtr posílá aktivační funkce a detekované karohydráty.
Příklad konfigurace detekce hran průběhu intersticiální glukózy je v souboru `setup/setup_th.ini`, příklad neuronové sítě v souboru `setup/setup_gru.ini`.

### PA detection
Filtr detekce fyzické aktivity.
- Heartbeat - detekce podle srdečního tepu
- Steps - detekce podle počtu kroků
- Acceleration - detekce podle hodnoty akcelerace
- Electrodermal activity - detekce podle elektrodermální aktivity
- Mean - použití průměru za časové okno
- Window size - mean - velikost klouzavého okénka pro spočítání průměru (v případě velikosti okna 1 je průměr rovná aktuální hodnotě)
- Detect IST edges - potvrzení detekce sestupnou hranou dat IST
- Signal - detekovaný signal
- Window size - edges - velikost klouzavého okénka pro detekci hran
- Thresholds - threshold ukazatelů pro detekci a thresholdy a váhy pro detekci hran

Filtr posílá detekovanou fyzickou aktivitu.
Příklad konfigurace s měřeným srdečním tepem a počtem kroků je v konfiguračním souboru `setup/setup_bpm.ini`. Příklad konfigurace s akcelerací a potvrzováním pomocí detekce sestupné hrany je v konfiguračním souboru `setup/setup_acc.ini`.

### Evaluation
Filtr pro vyhodnocení výsledků.
- Reference signal - referenční signál
- Detected signál - detekovaný signál
- Max detection delay - maximální zpoždění, které může mít detekovaný signál oproti referenčnímu
- False positive cooldown - cooldown po detekci falešně pozitivního signálu, než je započítán další
- Late detection delay - čas před referenčním signálem, kdy se bude detekce počítat jako pravdivě pozitivní
- Min reference count - minimální počet referenčních signálů za den

Filtr na konci běhu simulace posílá info s naměřenými statistikami počtu referenčních signálů TP, potvrzené TP, FN, FP, zpoždění detekce a zpoždění potvrzení.


## Python skripty

Skripty umožňují transformaci a modifikaci dat BGLP, trénování rekurentní neuronové sítě a analýzu metod detekce karbohydrátů a fyzické aktivity. Pro spuštění skriptů je nutné mít nainstalovaný Python 3.7 nebo 3.8. Python 3.9 není podporovaný z důvodu nepodporované kompatibilitě s knihovnou TensorFlow. Dále je nutné mít nainstalované tyto balíčky:
- numpy
- pandas
- scipy
- sklearn
- tensorflow
- tabulate
- matplotlib
- sweetviz

V souboru `examples.py` jsou příklady práce se skripty:
- lg.load_log()- transformace dat z logu do csv
- ld.load_data() - modifikace dat pro detekci karbohydrátů nebo fyzické aktivity
- cho.rnn() - trénování RNN
- cho.lda() - LDA/GDA
- cho.threshold() - detekce hran IST
- pa.get_feature() - spočtení vlastností (průměr, medián, směrodatná odchylka, rozdíl kvartilů)
- pa.export_features() - export vlastností do csv
- pa.ML() - test metod strojového učení pro detekci fyzické aktivity

### Trénování neuronové sítě

Pro natrénování keras modelu rekurentní neuronové sítě je připraven skript `train_rnn.py`.  Ten se spouští příkazem `python train_rnn.py <type> <options> [values]`, kdy `type` je typ neuronové `-gru` nebo `-lstm` (povinný parametr) a `options` jsou volitelné parametry:
- -f &nbsp; název logu pacienta (* pro natrénování neuronové sítě na všech logách v adresáři)
- -i &nbsp; adresář se vstupními logy (defaultně data/)
- -o &nbsp; adresář pro uložení natrénovaného modelu (defaultně model/)
- -h &nbsp; nápověda

Příklad natrénování GRU pro všechny pacienty: `python train_rnn.py -gru -f * -i data/ -o model/`
Příklad natrénování LSTM pro pacienta 575: `python train_rnn.py -lstm -f 575-ws-training.log -i data/ -o model/`