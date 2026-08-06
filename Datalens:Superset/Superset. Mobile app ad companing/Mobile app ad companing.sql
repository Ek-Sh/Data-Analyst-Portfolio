with sess_or as (
  select cast (coalesce(ors. event_dt, sess.session_start) AS date) as event_dt, --получаем дату события
  coalesce(ors. user_id, sess.user_id) as user_id,  --выводим id пользователя
  ors.order_id as order_id,  -- выводим id заказа
  coalesce(sess. channel, 'N/A') as channel,  -- gолучаем канал привлечения
  ors.revenue as revenue,  -- сколько выручки получили
  device,  -- какое устройство использовали
  avg(date_part('minute', session_end - session_start)
  + date_part('hour', session_end - session_start) * 60) as session_length -- длина одной сессии
from pa_orders ors 
full join pa_sessions sess 
on ors.event_dt between sess.session_start and sess.session_end and ors.user_id = sess. user_id 
group by cast(coalesce(ors. event_dt, sess. session_start) AS date), 
coalesce(ors.user_id, sess.user_id), 
ors.order_id, 
coalesce(sess. channel, 'N/A'), 
ors.revenue, 
device
)

select raw.event_dt,
avg(raw.session_length) as session_length, 
count (distinct raw.order_id) as orders, 
count (distinct raw.user_id) as users, 
count (distinct case when raw.order_id is not null then raw.user_id end) as users_with_order, 
raw.channel, 
raw.ad_category, 
raw.device, 
max (pa_costs.costs) as costs, 
sum (raw. revenue) as revenue 
from ( 
select coalesce(sess_or.event_dt, pa_costs.dt) as event_dt, 
session_length, 
order_id, 
user_id, 
coalesce(sess_or.channel, pa_costs. channel) as channel, 
coalesce(pa_costs.ad_category, 'N/A') as ad_category, 
device, 
sess_or.revenue 
from sess_or 
full join pa_costs on sess_or. channel = pa_costs.channel and sess_or.event_dt = pa_costs.dt
) raw full join pa_costs
on raw.channel = pa_costs.channel
and raw.event_dt = pa_costs.dt
group by
raw.event_dt,
raw. channel,
raw. ad_category,
raw. device


