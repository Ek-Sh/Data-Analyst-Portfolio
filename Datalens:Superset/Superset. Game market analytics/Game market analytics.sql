with games_base as (
  SELECT game_id,
          release_date,
          title,
          platform,
          developers,
          publishers,
          genres,
          supported_languages
      from games gam   
   WHERE
          release_date >= date('2023-01-01')
      AND
          release_date < date('2025-01-01') -- aильтруемм дату выхода игр
)

  SELECT gam.game_id,
          gam.release_date,
          gam.title,
          gam.platform,
          gam.developers,
          gam.publishers,
          gam.genres,
          gam.supported_languages,
          pri.date_acquired, -- дата приобретения игры
          coalesce(pri.rub, 0) as rub_clean,
          pg.player_id,
          concat(pg.game_id, pg.player_id) as install_id,
          ach.achievement_id,
          ach.title as achievement_title,
          ach.description,
          ach.rarity,
          ply.nickname,
          ply.country
    from games_base gam
left join prices pri 
         on gam.game_id = pri.game_id
left join players_games pg
         on gam.game_id = pg.game_id
left join players ply          
         on ply.player_id = pg.player_id
left join achievements ach
          on ach.game_id = gam.game_id

         
          
          
          
          
          
          
          