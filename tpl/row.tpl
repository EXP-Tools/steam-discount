      <tr data-search="%(search)s" data-discount="%(discount_rate)i">
        <td class="position">%(position)s</td>
        <td class="game-cell"><a class="game-link" href="%(shop_url)s" target="_blank" rel="noopener noreferrer"><img src="%(img_url)s" loading="lazy" decoding="async" width="116" height="44" alt=""><span><strong>%(game_name)s</strong><small>APP / %(game_id)i</small></span></a></td>
        <td class="price-cell"><strong>%(discount_price)s</strong><del>%(original_price)s</del></td>
        <td class="discount-cell"><span class="discount-badge" data-rate="%(discount_rate)i">%(discount_label)s</span></td>
        <td class="lowest-cell"><span>%(lowest_price)s</span>%(new_flag)s</td>
        <td class="review-cell"><span class="review-score score-%(evaluation_id)s" title="%(evaluation_info)s">%(evaluation)s</span><small title="%(evaluation_info)s">%(review_summary)s</small></td>
        <td class="region-cell"><span>%(region_label)s</span><details><summary>区域说明</summary><p>%(region_notice)s</p></details></td>
        <td class="players-cell"><span>%(cur_player_num)s</span><small>峰值 %(today_max_player_num)s</small></td>
        <td class="action-cell"><a class="store-link" href="%(shop_url)s" target="_blank" rel="noopener noreferrer" aria-label="前往 %(game_name)s 的 Steam 商店">商店 <span aria-hidden="true">↗</span></a></td>
      </tr>
