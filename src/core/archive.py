"""Keep every observed low in diff-friendly CSV, and only page records in the catalog.

SQLite is a disposable local working database; it is never committed by the crawler.
"""
import csv
import json
import sqlite3
from pathlib import Path

from src.config import settings
from src.utils.num import byte_to_str


def save(page_ids=None):
    base = Path(settings.database['dbpath']).parent
    with sqlite3.connect(settings.database['dbpath']) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM t_steam_game ORDER BY i_game_id').fetchall()
        ids = set(page_ids or ())
        for where, order in [
            ('i_discount_rate > 0 AND i_discount_rate < 100 AND i_evaluation_id > 6', 'i_discount_rate DESC'),
            ("i_discount_rate >= 100 AND CAST(s_original_price AS TEXT) != '0'", 'i_evaluation_id DESC'),
            ('i_evaluation_id IS NOT NULL', 'i_evaluation_id DESC'),
            ('i_rank_id IS NOT NULL', 'i_rank_id ASC'),
        ]:
            if page_ids is None:
                ids.update(r[0] for r in conn.execute('SELECT i_game_id FROM t_steam_game WHERE '
                                                    + where + ' ORDER BY ' + order + ', i_game_id LIMIT 100'))
    conn.close()
    history_tmp = base / 'lowest-prices.csv.tmp'
    with history_tmp.open('w', encoding='utf-8', newline='') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['game_id', 'lowest_price'])
        writer.writerows((r['i_game_id'], byte_to_str(r['s_lowest_price'])) for r in rows)
    history_tmp.replace(base / 'lowest-prices.csv')
    catalog = [{k: byte_to_str(r[k]) for k in r.keys() if k != 'i_id'}
               for r in rows if r['i_game_id'] in ids]
    catalog_tmp = base / 'catalog.json.tmp'
    catalog_tmp.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    catalog_tmp.replace(base / 'catalog.json')


def restore():
    base = Path(settings.database['dbpath']).parent
    history = base / 'lowest-prices.csv'
    if not history.exists():
        return
    with sqlite3.connect(settings.database['dbpath']) as conn:
        with history.open(encoding='utf-8', newline='') as source:
            conn.executemany('INSERT INTO t_steam_game (i_game_id,s_lowest_price) VALUES (?,?)',
                             ((int(r['game_id']), r['lowest_price'] or None) for r in csv.DictReader(source)))
        catalog = base / 'catalog.json'
        if catalog.exists():
            for row in json.loads(catalog.read_text(encoding='utf-8')):
                columns = list(row)
                conn.execute('UPDATE t_steam_game SET ' + ','.join(k + '=?' for k in columns)
                             + ' WHERE i_game_id=?', [row[k] for k in columns] + [row['i_game_id']])
    conn.close()
