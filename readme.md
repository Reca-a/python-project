# Terraria from Temu 0.2.0 - Dokumentacja

## Przegląd

"Terraria from Temu" to 2D gra typu sandbox inspirowana Terrarią, napisana w Pythonie z wykorzystaniem biblioteki Pygame. Gra oferuje proste systemy eksploracji, budowania, kopania oraz zarządzania ekwipunkiem w proceduralnie generowanym świecie.

## Główne Komponenty

### 1. System Gry (main.py)

Główna klasa `Game` zarządza:
- Inicjalizacją Pygame
- Pętlą główną gry
- Obsługą wydarzeń systemowych
- Zarządzaniem stanami gry

### 2. Scene i System Chunków (scene.py)

#### Klasa Scene
Zarządza całym światem gry:
- **Generacja świata**: Wykorzystuje noise OpenSimplex do tworzenia terenu
- **System chunków**: Dynamiczne ładowanie/rozładowywanie obszarów świata
- **Zarządzanie grupami sprite'ów**: Organizacja obiektów gry
- **Automatyczne zapisywanie**: Co 30 sekund

**Parametry konfiguracyjne:**
- `chunk_render_distance = 3` - Zasięg renderowania chunków
- `max_chunks_per_frame = 2` - Limit ładowania chunków na klatkę
- `auto_save_interval = 30` - Interwał automatycznego zapisu

#### Klasa Chunk
Reprezentuje fragment świata (30x30 bloków):
- **Generacja terenu powierzchniowego**: Dla chunków na poziomie y=0
- **Generacja jaskiń**: Cellular automata dla chunków podziemnych
- **System rud**: Generacja surowców na różnych głębokościach
- **Generacja drzew**: Losowe rozmieszczenie drzew

### 3. System Gracza (player.py)

#### Klasa Player
Główny charakter kontrolowany przez gracza:

**Fizyka:**
- Grawitacja: 1000 jednostek/s²
- Maksymalna prędkość pozioma: 4 jednostki
- Maksymalna prędkość pionowa: 300 jednostek
- Siła skoku: -420 jednostek

**Animacje:**
- `idle` - Stanie w miejscu
- `run` - Bieganie
- `jump` - Skok

**Sterowanie:**
- `A/D` - Ruch w lewo/prawo
- `Spacja` - Skok
- `LPM` - Niszczenie bloków
- `PPM` - Stawianie bloków
- `Strzałki lewo/prawo` - Nawigacja w ekwipunku

### 4. System Ekwipunku (inventory/)

#### Klasa Inventory
Zarządza przedmiotami gracza:
- **Rozmiar**: 5 slotów
- **Aktywny slot**: Obecnie wybrany przedmiot
- **Auto-stackowanie**: Automatyczne łączenie identycznych przedmiotów

#### System Przedmiotów
**Hierarchia klas:**
- `Item` - Bazowa klasa przedmiotu
- `BlockItem` - Przedmioty do stawiania bloków
- `EmptyItem` - Pusty slot

**Rejestr przedmiotów** (`ItemRegistry`):
- Materiały budowlane: grass, dirt, stone, wood, leaves
- Rudy: coal_ore, iron_ore, gold_ore, diamond_ore

### 5. System Sprite'ów (sprites/)

#### Klasa Entity
Bazowa klasa dla wszystkich obiektów w grze:
- Pozycja i tekstura
- Przynależność do grup
- Podstawowa logika aktualizacji

#### Klasa Mob
Rozszerza Entity o:
- **Fizyka**: Grawitacja i kolizje
- **AI**: Śledzenie gracza w zasięgu 10 bloków
- **Ruch**: Automatyczne skakanie przez przeszkody

### 6. System Zarządzania Światem (world_manager.py)

#### Klasa WorldManager
Obsługuje persistencję danych:
- **Format zapisu**: .dat
- **Backup**: Automatyczne tworzenie kopii zapasowych
- **Cache**: Optymalizacja wczytywania chunków
- **Metadane**: Informacje o świecie (seed, wersja, czas utworzenia)

## Konfiguracja (settings.py)

### Parametry Ekranu
```python
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
FPS = 60
TILE_SIZE = 16
```

### Parametry Chunków
```python
CHUNK_SIZE = 30  # Rozmiar chunka w blokach
CHUNK_PIXEL_SIZE = 480  # Rozmiar chunka w pikselach
```

### Parametry Fizyki
```python
GRAVITY = 1000
MAX_Y_VELOCITY = 300
MAX_X_VELOCITY = 4
```

### Parametry Generacji Świata
```python
# Cellular Automata (jaskinie)
CELLAUT_CHANCE_TO_STAY_ALIVE = 0.7
CELLAUT_DEATH_LIMIT = 5
CELLAUT_BIRTH_LIMIT = 6
CELLAUT_NUMBER_OF_STEPS = 4

# Generacja rud (progi prawdopodobieństwa)
COAL_GENERATION_THRESHOLD = 0.7
IRON_GENERATION_THRESHOLD = 0.8
GOLD_GENERATION_THRESHOLD = 0.85
DIAMOND_GENERATION_THRESHOLD = 0.9
```

## System Tekstur (texture_data.py)

### Atlas Tekstur
Tekstury są przechowywane w atlasie 16x16 bloków:
- **Rozmiar bloku**: 16x16 pikseli
- **Pozycjonowanie**: Współrzędne (x,y) w atlasie
- **Skalowalność**: Automatyczne skalowanie według TILE_SIZE

## Algorytmy Generacji

### 1. Generacja Terenu Powierzchniowego
Wykorzystuje noise OpenSimplex:
```python
noise_value = noise_generator.noise2(x * 0.05, y * 0.1)
height = int((noise_value + 1) * 10 + 5)
```

### 2. Generacja Jaskiń (Cellular Automata)
Proces 4-etapowy:
1. Losowa inicjalizacja (70% szans na kamień)
2. Iteracyjne zastosowanie reguł życia/śmierci
3. Wygładzenie struktury
4. Finalizacja kształtu jaskiń

### 3. Generacja Drzew
Oparta na szumie i czynnikach losowych:
- Próg generacji: noise + random > 0.5
- Wysokość pnia: 4-8 bloków
- Korona: Okrągła, promień 2-3 bloki

### 4. Generacja Rud
Zależna od głębokości (poziom = chunk):
- **Węgiel**: Od poziomu 0
- **Żelazo**: Od poziomu 2
- **Złoto**: Od poziomu 4
- **Diamenty**: Od poziomu 6

## Optymalizacje Wydajności

### System Chunków
- **Lazy Loading**: Chunki ładowane tylko gdy potrzebne
- **Limit ładowania**: Maksymalnie 2 chunki na klatkę
- **Priorytetowanie**: Chunki bliższe graczowi ładowane pierwsze
- **Kolejka ładowania**: Asynchroniczne przetwarzanie

### Zarządzanie Pamięcią
- **Cache chunków**: Limit 50 chunków w pamięci
- **Rozładowywanie**: Automatyczne usuwanie odległych chunków

### Renderowanie
- **Culling**: Renderowanie tylko widocznych obiektów
- **Group Management**: Efektywne zarządzanie sprite'ami
- **Camera Offset**: Optymalizacja pozycjonowania

## Mechaniki Gry

### Eksploracja
- Nieskończony świat
- System jaskiń i podziemi

### Budowanie
- Stawianie i niszczenie bloków
- System siatki (grid-based)
- Kolizje z otoczeniem

## Rozszerzalność

* Dodawanie Nowych Bloków
* Dodawanie Nowych Mobów
* Modyfikacja Generacji
* Rozszerzenie ekwipunku
* Dodanie craftingu
* Dodanie przedmiotów
* Zdrowie gracza i obrażenia
* Dodanie przeciwników
* Dodanie systemu oświetlenia

## Znane Ograniczenia

- Brak przedmiotów
- Brak celu gry
- Prymitywna grafika
- Podstawowy system fizyki
- Prymitywna mechanika
- prymitywny ekwipunek

## Wymagania Systemowe

### Minimalne
- Python 3.8+
- Pygame 2.0+
- NumPy
- OpenSimplex
- Komputer (laptop też się nada)

### Zalecane
- Python 3.10+
- Procesor (opcjonalnie)
- RAM (do trzymania chunków)
- Karta graficzna z serii RTX
- Dysk tysiąc

## Instrukcja Uruchomienia

1. Zainstaluj wymagane biblioteki:
```bash
pip install pygame numpy opensimplex
```

2. Uruchom grę:
```bash
python main.py
```

3. Użyj klawiszy A/D do poruszania, Spacji do skakania
4. LPM/PPM do interakcji z blokami
5. Strzałki lewo/prawo do nawigacji w ekwipunku
