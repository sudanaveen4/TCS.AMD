import json
import os
from typing import Type, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class JSONDatabase:
    def __init__(self, db_dir: str):
        self.db_dir = db_dir
        os.makedirs(db_dir, exist_ok=True)

    def _get_file_path(self, table_name: str) -> str:
        return os.path.join(self.db_dir, f"{table_name}.json")

    def read_table(self, table_name: str, model_class: Type[T]) -> List[T]:
        file_path = self._get_file_path(table_name)
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return [model_class(**item) for item in data]
            except json.JSONDecodeError:
                return []

    def write_table(self, table_name: str, items: List[T]):
        file_path = self._get_file_path(table_name)
        data = [item.dict() for item in items]
        
        # Datetime objects need to be converted to strings for JSON
        def default_serializer(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=default_serializer, indent=4)

    def insert(self, table_name: str, item: T):
        items = self.read_table(table_name, type(item))
        items.append(item)
        self.write_table(table_name, items)

    def update(self, table_name: str, item_id_field: str, item_id: str, new_item: T):
        items = self.read_table(table_name, type(new_item))
        for i, existing in enumerate(items):
            if getattr(existing, item_id_field) == item_id:
                items[i] = new_item
                self.write_table(table_name, items)
                return True
        return False
