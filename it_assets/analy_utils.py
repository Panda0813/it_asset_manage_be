from utils.conn_mssql import get_oa_user_sections
from xlrd import xldate_as_tuple
import pandas as pd
import numpy as np
import datetime



def trans_float_ts(ts, infmt, outfmt):
    """
    转换日期格式
    """
    try:
        if not ts:
            return ''
        if isinstance(ts, pd._libs.tslibs.timestamps.Timestamp):
            ts = ts.to_pydatetime()
        if isinstance(ts, str):
            if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}', ts):
                return ts
            try:
                dt = datetime.datetime.strptime(ts, infmt)
            except:
                dt = datetime.datetime(*xldate_as_tuple(ts, 0))
        elif isinstance(ts, datetime.datetime):
            dt = ts
        return dt.strftime(outfmt)
    except:
        return ts

asset_column_map = {
    '资产类别': 'category',
    '固定资产编号': 'asset_number',
    '内部编号': 'inner_number',
    '资产名称': 'name',
    '设备品牌': 'brand',
    '规格型号': 'model_code',
    '计量单位': 'unit',
    '所放地点': 'deposit_position',
    '入库时间': 'entry_date',
    '保管人': 'custodian',
    '供应商': 'supplier',
    '资产状态': 'status',
    '是否自研': 'is_self_develop',
    '外包项目名称': 'outsource_project',
    '内网或外网': 'network',
    '内网电脑IP地址': 'intranet_ip',
    '钥匙锁编号': 'key_lock_number',
    '领用时间': 'receive_date',
    '使用人': 'user_name',
    '备注': 'remarks'
}


def analysis_asset(datas):
    if not datas:
        return []
    df = pd.DataFrame(datas)
    df = df[list(asset_column_map.keys())]
    df.rename(columns=asset_column_map, inplace=True)
    df = df.replace({np.nan: None})
    ndf = df.copy()
    ndf['entry_date'] = ndf['entry_date'].apply(trans_float_ts, args=('%Y-%m-%d', '%Y-%m-%d'))
    ndf['entry_date'] = ndf['entry_date'].map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date() if x else None)
    ndf['receive_date'] = ndf['receive_date'].apply(trans_float_ts, args=('%Y-%m-%d', '%Y-%m-%d'))
    ndf['receive_date'] = ndf['receive_date'].map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date() if x else None)
    oa_user_sections = get_oa_user_sections()
    us_df = pd.DataFrame(oa_user_sections)
    us_df = us_df[['user_work_id', 'user_name', 'department', 'subsector']]
    mdf = pd.merge(ndf, us_df, on='user_name', how='left')
    mdf = mdf.replace({np.nan: None})
    datas = mdf.to_dict('records')
    return datas


material_columns_map = {
    '名称': 'name',
    '品牌': 'brand',
    '规格型号': 'model_code',
    '序列号': 'serial_number',
    '供应商': 'supplier',
    '领用时间': 'receive_date',
    '领用人': 'user_name',
    '备注': 'remarks'
}


def analysis_material(datas):
    if not datas:
        return []
    df = pd.DataFrame(datas)
    df = df[list(material_columns_map.keys())]
    df.rename(columns=material_columns_map, inplace=True)
    df = df.replace({np.nan: None})
    ndf = df.copy()
    ndf['receive_date'] = ndf['receive_date'].apply(trans_float_ts, args=('%Y-%m-%d', '%Y-%m-%d'))
    ndf['receive_date'] = ndf['receive_date'].map(
        lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date() if x else None)
    oa_user_sections = get_oa_user_sections()
    us_df = pd.DataFrame(oa_user_sections)
    us_df = us_df[['user_work_id', 'user_name', 'department', 'subsector']]
    mdf = pd.merge(ndf, us_df, on='user_name', how='left')
    mdf = mdf.replace({np.nan: None})
    datas = mdf.to_dict('records')
    return datas
