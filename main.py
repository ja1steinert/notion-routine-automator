import logging
from config import notion, PAGE_URL
from notion_api import NotionAPI
from metrics import (
    calculate_average, format_average,
    count_emojis, format_emojis,
    calculate_time_average, format_time_average,
    calculate_hour_average, format_hour_average,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ROW_OPERATIONS = {
    "💧": (calculate_average, format_average),
    "🧘‍♂️": (count_emojis, format_emojis),
    "🏋️‍♂️": (count_emojis, format_emojis),
    "⏱️": (calculate_time_average, format_time_average),
    "💤": (calculate_hour_average, format_hour_average),
}

def main():
    if not PAGE_URL:
        logging.error("A variável PAGE_URL não está definida no arquivo .env")
        return

    api = NotionAPI(notion)
    page_id = api.extract_page_id_from_url(PAGE_URL)
    if not page_id:
        return

    logging.info(f"Processando página com ID: {page_id}")
    all_blocks = api.get_all_blocks_recursively(page_id)

    unchecked = api.get_unchecked_checkboxes(all_blocks)
    if unchecked:
        logging.info(f"Encontradas {len(unchecked)} atividades restantes. Copiando...")
        api.copy_blocks_to_page(page_id, unchecked)
    else:
        logging.info("Nenhuma atividade restante encontrada.")

    logging.info("Atualizando tabela de hábitos...")
    table = api.find_first_table(all_blocks)
    if not table:
        logging.warning("Nenhuma tabela encontrada na página.")
        return

    rows = [b for b in all_blocks if b.get('type') == 'table_row' and b.get('parent', {}).get('block_id') == table['id']]

    if not rows:
        logging.warning(f"Nenhuma linha encontrada para a tabela com ID: {table['id']}")
        return

    for row in rows:
        title, cells = api.get_row_title_and_cells(row)

        # DEBUG
        logging.info(f"[DEBUG] Verificando linha. Título extraído: '{title}'")

        if title in ROW_OPERATIONS:
            values = [api.get_plain_text_from_cell(cell) for cell in cells[1:-1]]

            calc_func, format_func = ROW_OPERATIONS[title]
            result = calc_func(values)
            formatted_result = format_func(result)

            api.update_row_with_new_value(row['id'], formatted_result)
            logging.info(f"Linha '{title}' atualizada: {formatted_result}")

    logging.info("Processo finalizado com sucesso.")

if __name__ == "__main__":
    main()