from utils.ext_utils import dictfetchall
import pymssql
import pandas as pd
import numpy as np
import logging
import re

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


def get_oa_user_sections(user_work_id=None):
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
            where CurrentStatus=1 and not (User_name like '%紫存%') {}
            order by User_name'''
    filter_sql = ''
    if user_work_id:
        filter_sql += " and Worker_id='{}'".format(user_work_id)
    cur.execute(sql.format(filter_sql))
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
        ddf['user_work_id'] = pd.to_numeric(ddf['user_work_id'], errors='coerce')
        ddf.dropna(axis=0, subset=['user_work_id'], inplace=True)
        ddf['user_work_id'] = ddf['user_work_id'].astype(int).astype(str)

        def trans_name(x):
            user_name = re.sub(r'\d+', '', x['user_name'])
            no_ = re.findall(r'\d+', x['loginid'])
            if no_:
                user_name = user_name + no_[0]
            return user_name
        ddf['user_name'] = ddf.apply(lambda x: trans_name(x), axis=1)
        qs = ddf.to_dict('records')
    cur.close()
    conn.close()
    return qs


def trans_section_tree(data):
    df = pd.DataFrame(data)
    df.drop(['User_id', 'loginid', 'user_name', 'user_work_id'], axis=1, inplace=True)
    df = df.where(df.notnull(), '')
    ndf = df.groupby(['department', 'department_id', 'subsector', 'subsector_id']).sum()
    nndf = ndf.reset_index()
    nndf.loc[nndf['subsector'] == '', 'subsector'] = '无'
    sort_ls = [{'department': '董事会', 'no': 1}, {'department': '总经理办公室', 'no': 2},
               {'department': '产品业务一部(PB1)', 'no': 3},
               {'department': '产品业务二部(PB2)', 'no': 4}, {'department': '产品业务三部(PB3)', 'no': 5},
               {'department': '设计服务部(DS)', 'no': 6},
               {'department': '产品工程部(PE)', 'no': 7}, {'department': '供应链管理部(SCM)', 'no': 8},
               {'department': '人力资源与行政部(HRA)', 'no': 9},
               {'department': '信息与设计自动化部(ITDA)', 'no': 10}, {'department': '财务部(FA)', 'no': 11},
               {'department': '战略与项目合作部(SP)', 'no': 12},
               {'department': '法务部(LG)', 'no': 13}, {'department': '技术与项目合作部(TPC)', 'no': 15},
               {'department': '采购部(PUR)', 'no': 15}]
    sort_df = pd.DataFrame(sort_ls)
    mdf = pd.merge(nndf, sort_df, how='left', on='department')
    mdf = mdf.sort_values(by='no', ascending=True)
    department_ls = mdf[['department_id', 'department']].drop_duplicates().to_dict('records')
    for dp_dic in department_ls:
        department_id = dp_dic['department_id']
        subsector_ls = mdf[mdf['department_id'] == department_id][['subsector_id', 'subsector']].sort_index().to_dict(
            'records')
        for sb_dic in subsector_ls:
            sb_dic['department_id'] = department_id
            sb_dic['department'] = dp_dic['department']
        dp_dic['children'] = subsector_ls
    return department_ls


def get_sections_tree():
    conn = get_mssql_conn()
    cur = conn.cursor()
    sql = '''select User_id, loginid, convert(nvarchar(50), User_name) as user_name,
                      Worker_id as user_work_id, dp3.id as d3_id, convert(nvarchar(50), dp3.departmentname) as d3,
                  dp2.id as d2_id, convert(nvarchar(50), dp2.departmentname) as d2,
                  dp.id as d1_id, convert(nvarchar(50), dp.departmentname) as d1
                  from UniicUsers u left join UniicDepartment dp on u.DepartmentId=dp.id
                  left join UniicDepartment dp2 on dp.supdepid=dp2.id
                  left join UniicDepartment dp3 on dp2.supdepid=dp3.id
                  where CurrentStatus=1 and not (User_name like '%紫存%')'''
    cur.execute(sql)
    qs = dictfetchall(cur)
    if qs:
        df = pd.DataFrame(qs)
        ddf = df.copy()
        ddf['d4'] = ddf['d2']
        ddf['d4_id'] = ddf['d2_id']

        def check_d2(x):
            if pd.isnull(x['d3']):
                return None
            else:
                return x['d2']

        def check_d2_id(x):
            if pd.isnull(x['d3_id']):
                return None
            else:
                return x['d2_id']

        ddf['d2'] = ddf.apply(lambda x: check_d2(x), axis=1)
        ddf['d2_id'] = ddf.apply(lambda x: check_d2_id(x), axis=1)

        def check_d3(x):
            if pd.isnull(x['d3']):
                if pd.isnull(x['d4']):
                    return x['d1']
                else:
                    return x['d4']
            else:
                return x['d3']

        def check_d3_id(x):
            if pd.isnull(x['d3_id']):
                if pd.isnull(x['d4_id']):
                    return x['d1_id']
                else:
                    return x['d4_id']
            else:
                return x['d3_id']

        ddf['d3'] = ddf.apply(lambda x: check_d3(x), axis=1)
        ddf['d3_id'] = ddf.apply(lambda x: check_d3_id(x), axis=1)

        def check_d2_2(x):
            if pd.isnull(x['d4']):
                return x['d2']
            else:
                if pd.isnull(x['d2']):
                    return x['d1']
                else:
                    return x['d2']

        def check_d2_2_id(x):
            if pd.isnull(x['d4_id']):
                return x['d2_id']
            else:
                if pd.isnull(x['d2_id']):
                    return x['d1_id']
                else:
                    return x['d2_id']

        ddf['d2'] = ddf.apply(lambda x: check_d2_2(x), axis=1)
        ddf['d2_id'] = ddf.apply(lambda x: check_d2_2_id(x), axis=1)
        ddf['department'] = ddf['d3']
        ddf['department_id'] = ddf['d3_id']
        ddf['subsector'] = ddf['d2']
        ddf['subsector_id'] = ddf['d2_id']
        ddf['user_work_id'] = pd.to_numeric(ddf['user_work_id'], errors='coerce')
        ddf.dropna(axis=0, subset=['user_work_id'], inplace=True)
        ddf['user_work_id'] = ddf['user_work_id'].astype(int).astype(str)
        ddf.drop(['d4', 'd3', 'd2', 'd1', 'd4_id', 'd3_id', 'd2_id', 'd1_id'], axis=1, inplace=True)
        ddf = ddf.replace({np.nan: None})
        ddf['department_id'] = ddf['department_id'].map(lambda x: str(int(x)) if x else '')
        ddf['subsector_id'] = ddf['subsector_id'].map(lambda x: str(int(x)) if x else '')
        qs = ddf.to_dict('records')
    cur.close()
    conn.close()
    return qs


# 查询指定部门下面的人员
def query_section_user(department_id, subsector_id):
    datas = get_sections_tree()
    udf = pd.DataFrame(datas)
    if subsector_id is None:
        qdf = udf[udf['department_id'] == department_id]
    else:
        qdf = udf[(udf['department_id'] == department_id) & (udf['subsector_id'] == subsector_id)]
    return qdf['user_work_id'].tolist()
