from utils.ext_utils import dictfetchall
import pymssql
import pandas as pd
import logging

logger = logging.getLogger('django')


def get_mssql_conn():
    try:
        conn = pymssql.connect(host='172.21.12.104', user='DBConUser', password='Uniic8253Yw#',
                               database='UNIIC_OA')

        return conn
    except Exception as e:
        logger.error('连接oa数据库失败, error:{}'.format(str(e)))
        return None


def get_oa_users(request):
    from users.models import User
    conn = get_mssql_conn()
    cur = conn.cursor()
    exist_users = User.objects.all().filter(is_delete=False).values('employee_no')
    exist_users = [item['employee_no'] for item in exist_users if item['employee_no']]
    count_sql = '''select count(*) as count
                from UniicUsers where CurrentStatus=1 and not (User_name like '%紫存%') {}
                '''
    sql = '''select User_id, loginid, convert(nvarchar(50), User_name) as User_name,
                convert(nvarchar(50), Department) as Department, Worker_id
                from UniicUsers where CurrentStatus=1 and not (User_name like '%紫存%') {} order by User_name
                offset {} rows
                fetch next {} rows only'''
    filter_sql = ''
    page = 1
    size = 10
    for k, v in request.GET.items():
        if k == 'page':
            page = int(v)
        elif k == 'size':
            size = int(v)
        elif k == 'DepartmentId':
            filter_sql += ' and DepartmentId={}'.format(int(v))
        else:
            if v != None and v != '':
                cell = k + ' like ' + "'%{}%'".format(v)
                filter_sql += ' and ' + cell
    if exist_users:
        if len(exist_users) == 1:
            filter_sql += " and Worker_id <> '{}'".format(exist_users[0])
        else:
            filter_sql += ' and Worker_id not in {}'.format(tuple(exist_users))
    total_sql = count_sql.format(filter_sql)
    cur.execute(total_sql)
    total_qs = dictfetchall(cur)
    total = total_qs[0]['count']
    if total:
        offset = (page - 1) * size
        sql = sql.format(filter_sql, offset, size)
        cur.execute(sql)
        users = dictfetchall(cur)
    else:
        users = []
    cur.close()
    conn.close()
    return total, users


def get_oa_sections():
    conn = get_mssql_conn()
    cur = conn.cursor()
    sql = '''select distinct DepartmentId,convert(nvarchar(50), Department) as Department 
                from UniicUsers where CurrentStatus=1'''
    cur.execute(sql)
    sections = dictfetchall(cur)
    if sections:
        sections = [{'value': item['DepartmentId'], 'label': item['Department']} for item in sections]
    cur.close()
    conn.close()
    return sections


def get_oa_user_sections():
    conn = get_mssql_conn()
    cur = conn.cursor()
    sql = '''select User_id, loginid, convert(nvarchar(50), User_name) as user_name,
                      Worker_id as user_work_id,
                      convert(nvarchar(50), dp3.departmentname) as d3,
                      convert(nvarchar(50), dp2.departmentname) as d2,
                      convert(nvarchar(50), dp.departmentname) as d1
                      from UniicUsers u left join UniicDepartment dp on u.DepartmentId=dp.id
                      left join UniicDepartment dp2 on dp.supdepid=dp2.id
                      left join UniicDepartment dp3 on dp2.supdepid=dp3.id
            where CurrentStatus=1 and not (User_name like '%紫存%')
            order by User_name'''
    cur.execute(sql)
    qs = dictfetchall(cur)
    if qs:
        df = pd.DataFrame(qs)
        ddf = df.copy()
        ddf['d4'] = ddf['d2']

        def check_d2(x):
            if pd.isnull(x['d3']):
                return None
            else:
                return x['d2']
        ddf['d2'] = ddf.apply(lambda x: check_d2(x), axis=1)

        def check_d3(x):
            if pd.isnull(x['d3']):
                if pd.isnull(x['d4']):
                    return x['d1']
                else:
                    return x['d4']
            else:
                return x['d3']
        ddf['d3'] = ddf.apply(lambda x: check_d3(x), axis=1)

        def check_d2_2(x):
            if pd.isnull(x['d4']):
                return x['d2']
            else:
                if pd.isnull(x['d2']):
                    return x['d1']
                else:
                    return x['d2']
        ddf['d2'] = ddf.apply(lambda x: check_d2_2(x), axis=1)
        ddf['department'] = ddf['d3']
        ddf['subsector'] = ddf['d2']
        ddf.drop(['d4', 'd3', 'd2', 'd1'], axis=1, inplace=True)
        qs = ddf.to_dict('records')
    cur.close()
    conn.close()
    return qs
