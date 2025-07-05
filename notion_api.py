import re
import logging
from typing import List, Dict, Any, Optional, Tuple

class NotionAPI:
    """Uma classe para encapsular interações genéricas com a API do Notion."""
    
    def __init__(self, client):
        self.notion = client

    def extract_page_id_from_url(self, url: str) -> Optional[str]:
        # Regex para extrair a última parte de 32 caracteres hexadecimais da URL
        match = re.search(r'([a-f0-9]{32})$', url.split('?')[0])
        if match:
            page_id = match.group(1)
            # Formatação para UUID padrão
            return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
        logging.error("URL inválida ou page_id não encontrado.")
        return None

    def get_all_blocks_recursively(self, block_id: str) -> List[Dict[str, Any]]:
        all_blocks = []
        next_cursor = None
        while True:
            response = self.notion.blocks.children.list(block_id=block_id, start_cursor=next_cursor)
            all_blocks.extend(response['results'])
            if not response['has_more']: break
            next_cursor = response['next_cursor']
        
        # Recursão para blocos filhos
        child_blocks = []
        for block in all_blocks:
            if block.get('has_children'):
                child_blocks.extend(self.get_all_blocks_recursively(block['id']))
        return all_blocks + child_blocks

    def get_unchecked_checkboxes(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [b for b in blocks if b['type'] == 'to_do' and not b['to_do']['checked'] and b['to_do']['rich_text']]

    def copy_blocks_to_page(self, page_id: str, checkboxes: List[Dict[str, Any]]):
        children_to_append = [
            {"type": "divider", "divider": {}},
            {"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Atividades Restantes"}}]}},
        ]
        for cb in checkboxes:
            children_to_append.append({
                "type": "to_do",
                "to_do": {"rich_text": cb['to_do']['rich_text'], "checked": False}
            })
        
        # A API permite adicionar até 100 blocos por chamada
        self.notion.blocks.children.append(block_id=page_id, children=children_to_append)

    def find_first_table(self, blocks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return next((b for b in blocks if b['type'] == 'table'), None)

    def get_plain_text_from_cell(self, cell: List[Dict[str, Any]]) -> str:
        return "".join(part.get('plain_text', '') for part in cell)

    def get_row_title_and_cells(self, row: Dict[str, Any]) -> Tuple[str, List]:
        cells = row.get('table_row', {}).get('cells', [])
        title = self.get_plain_text_from_cell(cells[0]).strip() if cells else ""
        return title, cells

    def update_row_with_new_value(self, row_id: str, value: str):
        row_block = self.notion.blocks.retrieve(block_id=row_id)
        cells = row_block.get('table_row', {}).get('cells', [])
        if cells:
            cells[-1] = [{"type": "text", "text": {"content": value}}]
            self.notion.blocks.update(row_id, table_row={"cells": cells})