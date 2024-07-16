import requests
from bs4 import BeautifulSoup
from psycopg2 import pool
import time as td
from collections import namedtuple
from multiprocessing import Pool,Manager
import threading
import copy
import codecs
import signal
import sys
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)
conn_pool = pool.SimpleConnectionPool(1,7,host='db',dbname='tse',
                                    user='root',password='root')
                                    
#---------------init db------------------------
try:
	conn = conn_pool.getconn()
	cur = conn.cursor()
	cur.execute("""select exists (select from information_schema.tables 
	where table_schema='public' and table_name='company')""")
	if not cur.fetchone()[0]:
		sql=''
		logger.info('Creating tables started')
		with open('db.sql') as o:
			sql = ''.join(o.readlines())
		cur.execute(sql)
		logger.info('Creating tables finished successfully')
		
	logger.info('Inserting data started')
	cur.execute("""select count(*) from public.group limit 1""")
	if cur.fetchone()[0]==0:
		with codecs.open('group.txt', 'r',encoding='utf-8') as f:
			cur.copy_from(f, 'public.group(id,code,name)', sep=',')
			
	cur.execute("""select count(*) from public.company limit 1""")
	if cur.fetchone()[0]==0:	
		with codecs.open('company.txt', 'r',encoding='utf-8') as f:
			cur.copy_from(f, 'public.company', sep=',')

	logger.info('Inserting data finished successfully')
	conn.commit()

	logger.info('Database initializition finished successfully')
except:
	logger.exception('Database initializition failed. Rolling back',exc_info=True)
	conn.rollback()
	conn_pool.closeall()
	exit()
finally:
	cur.close()
	conn_pool.putconn(conn)

#---------------fetch data------------------------

Row=namedtuple('Row','id tse_id code')

url = 'http://www.tsetmc.com/tsev2/data/instinfofast.aspx?i={cid}&c={gcode}+'
tse_url='http://www.tsetmc.com/loader.aspx?ParTree=151311&i={cid}'



price_columns = ['last_trade', 'A', 'last', 'close', 'first', 'yesterday',
                 'max', 'min', 'count', 'volume', 'cost', '0', 'date', 'time']

trade_columns = ['kharid_haghighi', 'kharid_hoghoghi', '0',
                 'forosh_haghighi', 'forosh_hoghoghi', 'tedad_kharid_haghighi',
                 'tedad_kharid_hoghoghi', '0', 'tedad_forosh_haghighi',
                 'tedad_forosh_hoghoghi']
queues_columns = ['tedad_kharid','hajm_kharid','gheimat_kharid',
                  'tedad_forosh','hajm_forosh','gheimat_forosh']

db_columns = ['last', 'close', 'first', 'yesterday','max', 'min','count',
            'volume', 'cost','kharid_haghighi', 'kharid_hoghoghi',
            'forosh_haghighi', 'forosh_hoghoghi', 'tedad_kharid_haghighi',
            'tedad_kharid_hoghoghi', 'tedad_forosh_haghighi',
            'tedad_forosh_hoghoghi', 'date', 'time']

middle_columns = ['MinWeek','MaxWeek','BaseVol','QTotTran5JAvg','EstimatedEPS','MinYear','MaxYear',
                  'ZTitad','PSGelStaMin','PSGelStaMax','SectorPE','KAjCapValCpsIdx']

middle_db_columns = ['min_week','max_week','min_year','max_year','min_gheimat_mojaz',
                     'max_gheimat_mojaz','tedad_saham','hajm_mabna','miangin_hajm_mah',
                     'saham_shenavar','pe_goroh','eps','pe']
middle_columns_map = {'min_week':'MinWeek','max_week':'MaxWeek','min_year':'MinYear',
                      'max_year':'MaxYear','hajm_mabna':'BaseVol','min_gheimat_mojaz':'PSGelStaMin',
                      'max_gheimat_mojaz':'PSGelStaMax','tedad_saham':'ZTitad',
                      'saham_shenavar':'KAjCapValCpsIdx','miangin_hajm_mah':'QTotTran5JAvg',
                      'pe_goroh':'SectorPE','eps':'EstimatedEPS'}

session = requests.Session()
manager = Manager()
data_dict = manager.dict()
MAX_TRIES = 5
conn=conn_pool.getconn()
cur = conn.cursor()

cur.execute('''
select c.id,c.tse_id,g.code from
public.company c left join public.group g on c.group_id=g.id
where c.id!=612
 ''')

rows = [Row(row[0],row[1].strip(),row[2].strip()) for row in cur.fetchall()]
cur.close()
conn_pool.putconn(conn)


def get_data(row):
#    tries = 0
#    while True and tries < MAX_TRIES:
#      tries += 1
  res = session.get(url.format(cid=row.tse_id, gcode=row.code))
  tse_res = session.get(tse_url.format(cid=row.tse_id))
  soup = BeautifulSoup(tse_res.content,'html.parser')
  scripts=soup.find_all('script')
  if scripts is not None and len(scripts)>=3:
      middle_part_text = scripts[2].text
      s = set(middle_part_text[middle_part_text.find('var')+5:middle_part_text.find(';')].split(','))
      middle_part=eval('dict(%s)'%(','.join(s)))
      middle_part_data = {k:middle_part.get(k) for k in middle_columns}
  else:
      middle_part_data={k:None for k in middle_columns}
  if res.status_code == 200:
      content = res.content.decode('utf-8')
      content_list = content.split(';')
#      all_loaded = True
#      for c in content_list:
#          all_loaded &= (c == '')
#      if not all_loaded:
#          continue

      if content_list[0] == '':
          return
      else:
          price_data_list = content_list[0].split(',')

      if content_list[4] == '':
          trade_data_list = [None for x in trade_columns]
      else:
          trade_data_list = content_list[4].split(',')
      if content_list[2] == '':
          queues_data = None
      else:
          queues = content_list[2].split(',')
          queues_data = []
          for q in queues:
              if q != '':
                  queues_data.append(dict(zip(queues_columns,q.split('@'))))

      all_data = dict(zip(price_columns,price_data_list))
      all_data.update(dict(zip(trade_columns,trade_data_list)))
      all_data.update({'queues': queues_data})
      all_data.update(middle_part_data)
      if all_data['max'] != '0':
          date = '{}-{}-{}'.format(
              price_data_list[12][:4],
              price_data_list[12][4:6],
              price_data_list[12][6:8])
          time = '{}:{}:{}'.format(
              price_data_list[13][:-4],
              price_data_list[13][-4:-2],
              price_data_list[13][-2:])
          all_data['date']=date
          all_data['time']=time
          data_dict[row] = all_data
          return


def insert_data(datas):
    conn = conn_pool.getconn()
    cur = conn.cursor()
    for row,data in datas.items():
        data_id = None
        try:
            d=[row.tse_id]
            for k in db_columns:
              d.append(data[k])
            for c in middle_db_columns[:-1]:
              t=data[middle_columns_map[c]]
              if t is not None:
                d.append(float(t))
              else:
                d.append(None)
            try:
            	pe=round(int(data['close'])/float(data[middle_columns_map['eps']])*10)/10
            except:
            	pe=None
            d.append(pe)
            cur.execute(
                '''
                insert into public.daily_data ({cols})
                values ({vals})
                returning id
                '''.format(cols=','.join(['company_id']+db_columns+middle_db_columns),
                           vals=','.join(['%s']*33)),
                tuple(d)
            )
            data_id = cur.fetchone()

            if data['queues'] is not None:
                if data_id is not None:
                    for q in data['queues']:
                        d = tuple([q[k] for k in queues_columns]+[data_id])
                        cur.execute(
                            '''
                            insert into public.queues ({cols})
                            values (%s,%s,%s,%s,%s,%s,%s)
                            returning id
                            '''.format(cols=','.join(queues_columns)+','+'price_id'),
                            d
                        )
        except Exception as e:
            logger.exception(data,exc_info=True)
            pass

    conn.commit()
    cur.close()
    conn_pool.putconn(conn)



def periodic_runner():
    logger.info('Start collecting new data')
    t1 = td.time()
    pool = Pool(10)
    pool.map(get_data,rows)
    pool.close()
#    for row in rows:
#    get_data(rows[0])
#    with Pool(1) as pool:
#        pool.map(get_data,rows)
    logger.info('Done in {}'.format(td.time()-t1))
    datas = copy.deepcopy(data_dict)
    data_dict.clear()
    logger.info('Inserting data')
    t = threading.Thread(target=insert_data,args=(datas,))
    t.start()
    t.join()


def exit_signal_handler(signal,frame):
    print('Closing connections')
    # conn_pool.‌close()
    sys.exit()


if __name__=='__main__':
    interval = 300
    try:
        while True:
            t1 = td.time()
            periodic_runner()
            t2 = td.time()
            if (t2-t1)<interval:
                print('sleeping %s secs'%(interval-(t2-t1)))
                td.sleep(interval-(t2-t1))

    except KeyboardInterrupt:
        conn_pool.closeall()
        exit()
