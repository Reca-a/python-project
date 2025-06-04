import json
from pathlib import Path
import time
import gzip
from typing import Optional, Dict, Any


class WorldManager:
    """Menedżer świata obsługujący zapisywanie i wczytywanie danych"""

    def __init__(self, world_name: str = "default_world", game_version: str = '0.2.0'):
        self.world_name = world_name
        self.world_seed = 121367
        self.game_version = game_version

        # Ścieżki plików
        self.saves_dir = Path("saves")
        self.saves_dir.mkdir(exist_ok=True)
        self.world_file = self.saves_dir / f"{world_name}.dat"

        self.world_data = self.load_world_data()

        # Cache dla chunków
        self.chunk_cache = {}
        self.cache_size_limit = 50

    def load_world_data(self) -> dict:
        """Wczytuje dane świata"""
        if not self.world_file.exists():
            return self._create_new_world_data()

        try:
            return self._load_data()
        except Exception as e:
            print(f"Błąd wczytywania świata: {e}")
            return self._create_new_world_data()

    def _create_new_world_data(self) -> dict:
        """Tworzy nowe dane świata"""
        return {
            'chunks': {},
            'world_info': {'seed': self.world_seed},
            'metadata': {
                'world_name': self.world_name,
                'created': time.time(),
                'last_modified': time.time(),
                'version': self.game_version
            }
        }

    def _load_data(self) -> dict:
        """Wczytuje skompresowane dane JSON"""
        with gzip.open(self.world_file, 'rt', encoding='utf-8') as f:
            return json.load(f)

    def save_world_data(self, chunks_data: Dict[tuple, Any]):
        """Zapisuje dane świata"""
        try:
            # Aktualizuj dane chunków
            for pos, chunk in chunks_data.items():
                chunk_key = f"{pos[0]}_{pos[1]}"
                self.world_data['chunks'][chunk_key] = chunk.get_save_data()

            # Aktualizuj metadane
            self.world_data['metadata']['last_modified'] = time.time()
            self.world_data['metadata']['chunk_count'] = len(self.world_data['chunks'])

            self._save_data()
            print(f"Świat '{self.world_name}' zapisany ({len(self.world_data['chunks'])} chunków)")

        except Exception as e:
            print(f"Błąd zapisywania świata: {e}")

    def _save_data(self):
        """Zapisuje dane w skompresowanym formacie"""
        backup_file = self.world_file.with_suffix('.dat.backup')

        # Utwórz backup
        if self.world_file.exists():
            import shutil
            shutil.copy2(self.world_file, backup_file)

        # Zapisz skompresowane dane
        with gzip.open(self.world_file, 'wt', encoding='utf-8') as f:
            json.dump(self.world_data, f, separators=(',', ':'))

    def load_chunk_data(self, chunk_pos: tuple[int, int]) -> Optional[dict]:
        """Wczytuje dane chunka"""
        chunk_key = f"{chunk_pos[0]}_{chunk_pos[1]}"

        # Sprawdź cache
        if chunk_key in self.chunk_cache:
            return self.chunk_cache[chunk_key]

        # Sprawdź dane świata
        chunk_data = self.world_data['chunks'].get(chunk_key)
        if chunk_data:
            # Dodaj do cache
            if len(self.chunk_cache) < self.cache_size_limit:
                self.chunk_cache[chunk_key] = chunk_data
            return chunk_data

        return None

    def get_world_info(self) -> dict:
        """Zwraca informacje o świecie"""
        metadata = self.world_data.get('metadata', {})
        world_info = self.world_data.get('world_info', {})

        return {
            'name': metadata.get('world_name', self.world_name),
            'seed': world_info.get('seed', self.world_seed),
            'chunk_count': len(self.world_data.get('chunks', {})),
            'last_modified': metadata.get('last_modified', 0),
            'created': metadata.get('created', 0),
            'version': metadata.get('version', self.game_version)
        }