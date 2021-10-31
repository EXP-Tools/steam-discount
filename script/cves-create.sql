CREATE TABLE IF NOT EXISTS `t_steam_game` (
  `i_id`                    INTEGER(32),
  `s_name`                  TEXT(128),
  `s_original_price`        TEXT(16),
  `s_lowest_price`          TEXT(16),
  `i_discount_rate`         INTEGER(32),
  `s_discount_price`        TEXT(16),
  `i_evaluation_id`         INTEGER(32),
  `s_evaluation`            TEXT(64),
  `s_evaluation_info`       TEXT(512),
  `s_shop_url`              TEXT(512), 
  `i_sort_id`               INTEGER(32),
  `i_cur_player_num`        INTEGER(32), 
  `i_today_max_player_num`  INTEGER(32)
);