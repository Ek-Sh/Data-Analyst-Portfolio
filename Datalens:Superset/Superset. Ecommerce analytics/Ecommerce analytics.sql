with SessionOrders as (
  select sess.session_id
    , sess.user_id
    , ord.order_datetime
    , sess.session_start
    , sess.session_end
    , sess.os
    , sess.device
    , sess.channel
    , usr.country
    , usr.city
    , usr.coordinates
    , ord.order_id
    , prd.name
    , prd.category
    , prd.price_usd
    , prd.rating
    , prd.date_added
    , prd.in_stock
    , itm.product_id
    , itm.quantity
  from ec_store.sessions sess
  /* Не существует таких сессий, у которых нет юзера и наоборот */
  join ec_store.users usr
    on sess.user_id = usr.user_id
  /* Заказы только в онлайн коммерции и поэтому тут не может быть заказов без сессии
  , но могут быть сессии без заказов */
  left join ec_store.orders ord 
    on ord.user_id = sess.user_id
    and ord.order_datetime between sess.session_start and sess.session_end
    /* Связка заказа и продукта */
  left join ec_store.order_items itm 
    on ord.order_id = itm.order_id
    /* Заказ без продукта не существует */
  left join ec_store.products prd 
    on itm.product_id = prd.id 
  )
  , FirstOrder as (
    select
        user_id
        , min(order_datetime) as first_order_date -- дата первого заказа пользователя
        , min(session_start) as first_session_date -- дата первой сессии
        , coalesce(extract(day from (min(order_datetime) - min(session_start))), -1) as days_to_first_order
      from SessionOrders
    group by user_id
    having extract(day from (min(order_datetime) - min(session_start))) > 0
  )
  
    select
      date(date_trunc('month', session_start)) AS value_day
      , category
      , os 
      , channel
      , name
      , country
      , count(distinct order_id) as total_orders
      , sum(quantity) as total_products
      , sum(price_usd * quantity) as total_order_price
      , avg(price_usd * quantity) as avg_order_price
      , count(distinct sso.user_id) as unique_users
      , count(distinct case when order_id is not null then sso.user_id end) as active_users
      , count(distinct session_id) as total_sessions
      , avg(extract(epoch from (session_end - session_start))) / 60 as avg_session_duration_minutes
      , round(avg(days_to_first_order)) as days_to_first_order
    from SessionOrders sso
    left join FirstOrder fo 
      on sso.user_id = fo.user_id
    
    group by 
        date(date_trunc('month', session_start))
      , category
      , os 
      , channel
      , name
      , country