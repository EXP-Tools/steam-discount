"""Small reusable WebP covers and explicitly sourced regional store notices."""
import io
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
from color_log.clog import log

from src.config import PRJ_DIR
from src.utils.num import byte_to_str

ROOT = Path(PRJ_DIR)
REGIONS = ROOT / 'data/region-info.json'
_regions = None
_used_covers = set()
_region_budget = 20
_proxy = {}
_zone = 'CN'


def configure(zone, proxy):
    global _zone, _proxy, _region_budget
    _zone, _proxy, _region_budget = zone.upper(), proxy, 20


def regions():
    global _regions
    if _regions is None:
        _regions = json.loads(REGIONS.read_text(encoding='utf-8')) if REGIONS.exists() else {}
    return _regions


def key(game):
    url = byte_to_str(game.shop_url) or ''
    match = re.search(r'/(app|sub|bundle)/(\d+)', url)
    return '-'.join(match.groups()) if match else 'app-%s' % game.game_id


def record_availability(games, zone):
    # A public price on this country's storefront proves purchasing availability,
    # but says nothing about gifting or activation in another country.
    for game in games.values():
        region_key = zone.upper() + ':' + key(game)
        entry = regions().setdefault(region_key, {})
        entry.update(available=True, observed=int(time.time()))


def _cover(game):
    name = key(game) + '.webp'
    target = ROOT / 'docs/imgs/covers' / name
    _used_covers.add(name)
    if target.exists():
        return
    url = byte_to_str(game.img_url) or ''
    urls = [url.replace('http://', 'https://', 1)] if url else []
    if key(game).startswith('app-'):
        urls.append('https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/'
                    '%s/capsule_231x87.jpg' % game.game_id)
    for url in urls:
        if not url.startswith('https://'):
            continue
        try:
            response = requests.get(url, proxies=_proxy, timeout=(5, 15))
            response.raise_for_status()
            if len(response.content) > 2_000_000:
                raise ValueError('封面超过 2 MB')
            with Image.open(io.BytesIO(response.content)) as image:
                thumb = ImageOps.fit(image.convert('RGB'), (176, 66), method=Image.Resampling.LANCZOS)
                target.parent.mkdir(parents=True, exist_ok=True)
                thumb.save(target, 'WEBP', quality=65, method=6)
            return
        except (requests.RequestException, OSError, ValueError) as exc:
            log.warn('封面读取失败 [%s]: %s' % (game.game_id, exc))


def _region(game):
    region_key = _zone + ':' + key(game)
    entry = regions().setdefault(region_key, {})
    try:
        response = requests.get(byte_to_str(game.shop_url), params={'cc': _zone, 'l': 'schinese'},
                                proxies=_proxy, timeout=(5, 15))
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(' ', strip=True)
        notices = [node.get_text(' ', strip=True) for node in soup.select(
            '.notice_box_content, .game_area_purchase_restricted, .game_area_purchase_not_available')]
        notices = [s for s in notices if re.search(r'地区|国家|区域|激活|region|countr|activat', s, re.I)]
        unavailable = any(s in text for s in ['该物品在您所在的地区不可用',
            '您所在的地区目前不提供此物品', 'This item is currently unavailable in your region'])
        if unavailable:
            entry['available'] = False
        elif soup.select_one('.game_area_purchase_game .game_purchase_price, '
                             '.game_area_purchase_game .discount_final_price, '
                             '.game_area_purchase_game .btn_addtocart'):
            entry['available'] = True
        else:
            return  # Age gates or login pages cannot establish a restriction.
        entry.update(notice=' '.join(notices), checked=int(time.time()), source=response.url)
    except requests.RequestException as exc:
        log.warn('购买区域核验失败 [%s]: %s' % (game.game_id, exc))


def prepare(games):
    global _region_budget
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(_cover, games))
    pending = [g for g in games if time.time() - regions().get(_zone + ':' + key(g), {}).get('checked', 0) > 7 * 86400]
    pending = pending[:_region_budget]
    _region_budget -= len(pending)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(_region, pending))


def cover_url(game):
    name = key(game) + '.webp'
    return 'imgs/covers/' + name if (ROOT / 'docs/imgs/covers' / name).exists() else 'imgs/favicon.svg'


def region_label(game):
    entry = regions().get(_zone + ':' + key(game), {})
    zone = '国区' if _zone == 'CN' else _zone
    if entry.get('available') is True:
        label = zone + '可购'
    elif entry.get('available') is False:
        label = zone + '不可购'
    else:
        label = zone + ' · 待核验'
    notice = entry.get('notice') or '商店未披露跨区激活或赠送限制，购买前请确认商品页。'
    if entry.get('notice'):
        label += ' · 有限制'
    return label, notice


def save(clean=True):
    REGIONS.parent.mkdir(parents=True, exist_ok=True)
    REGIONS.write_text(json.dumps(regions(), ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    # Keep only the covers referenced by the generated pages.
    for path in (ROOT / 'docs/imgs/covers').glob('*.webp'):
        if clean and path.name not in _used_covers:
            path.unlink()
