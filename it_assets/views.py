from rest_framework import generics, serializers
from rest_framework import filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from it_assets.serializers import FixedAssetsSerializer, ConsumableMaterialSerializer, AssetStatusRecordSerializer
from it_assets.models import FixedAssets, ConsumableMaterial, FixedAssetStatusRecord

from utils.log_utils import set_create_log, set_update_log, set_delete_log
from utils.ext_utils import REST_FAIL, REST_SUCCESS, VIEW_FAIL, VIEW_SUCCESS, get_file_path, execute_batch_sql, create_excel_resp
from it_assets.analy_utils import analysis_asset, analysis_material

import os
import datetime
import pandas as pd
import traceback
import logging

logger = logging.getLogger('django')


@api_view(['GET'])
def get_assets_maps(request):
    category_ls = ['电子设备']
    category_qs = FixedAssets.objects.values('category').distinct()
    if category_qs:
        category_ls.extend([item['category'] for item in list(category_qs) if item['category']])
        category_ls_ = list(set(category_ls))
        category_ls_.sort(key=category_ls.index)
        category_ls = category_ls_
    name_ls = ['笔记本', '台式机', '投影仪', '电视', '广告机', '显示器', '打印机', '摄像头', '交换机', '扫描仪',
               '瘦客户机', '存储设备', 'VPN主机', '服务器及3Par设备一套', '防火墙', '服务器', '会议系统电话',
               '全向麦克风', '扫描枪', '英方一体机']
    name_qs = FixedAssets.objects.values('name').distinct()
    if name_qs:
        name_ls.extend([item['name'] for item in list(name_qs) if item['name']])
        name_ls_ = list(set(name_ls))
        name_ls_.sort(key=name_ls.index)
        name_ls = name_ls_
    brand_ls = []
    brand_qs = FixedAssets.objects.values('brand').distinct()
    if brand_qs:
        brand_ls.extend([item['brand'] for item in list(brand_qs) if item['brand']])
        brand_ls_ = list(set(brand_ls))
        brand_ls_.sort(key=brand_ls.index)
        brand_ls = brand_ls_
    unit_ls = ['台', '个']
    unit_qs = FixedAssets.objects.values('unit').distinct()
    if unit_qs:
        unit_ls.extend([item['unit'] for item in list(unit_qs) if item['unit']])
        unit_ls_ = list(set(unit_ls))
        unit_ls_.sort(key=unit_ls.index)
        unit_ls = unit_ls_
    deposit_position_ls = ['A座实验室', 'B座实验室', '1F产线', '1F办公室', '1F-IT机房', '1F库房', '2F办公室', '201机房',
                           '203机房', '207机房', '209机房', '3F办公室', '3F机房', '4F办公室', '401机房', '402机房',
                           '403机房', 'IT库房', '总经理办公室', '上海办公室', '深圳办公室', '台湾办公室']
    deposit_position_qs = FixedAssets.objects.values('deposit_position').distinct()
    if deposit_position_qs:
        deposit_position_ls.extend([item['deposit_position'] for item in list(deposit_position_qs)
                                    if item['deposit_position']])
        deposit_position_ls_ = list(set(deposit_position_ls))
        deposit_position_ls_.sort(key=deposit_position_ls.index)
        deposit_position_ls = deposit_position_ls_
    custodian_ls = ['张少敏', '魏立', '孙建锁']
    supplier_ls = ['西安轩刚商贸', '京东商城']
    supplier_qs = FixedAssets.objects.values('supplier').distinct()
    if supplier_qs:
        supplier_ls.extend([item['supplier'] for item in list(supplier_qs) if item['supplier']])
        supplier_ls_ = list(set(supplier_ls))
        supplier_ls_.sort(key=supplier_ls.index)
        supplier_ls = supplier_ls_
    status_ls = ['使用中', '空闲', '已坏', '已报废']
    is_self_develop_ls = ['是', '否']
    network_ls = ['内网', '外网']
    outsource_project_ls = ['展锐', '合芯', '清微智能', '仁芯', '同创', 'TMC', 'MTK']
    outsource_project_qs = FixedAssets.objects.values('outsource_project').distinct()
    if outsource_project_qs:
        outsource_project_ls.extend([item['outsource_project'] for item in list(outsource_project_qs)
                                     if item['outsource_project']])
        outsource_project_ls_ = list(set(outsource_project_ls))
        outsource_project_ls_.sort(key=outsource_project_ls.index)
        outsource_project_ls = outsource_project_ls_
    return REST_SUCCESS({
        'category_ls': category_ls,
        'name_ls': name_ls,
        'brand_ls': brand_ls,
        'unit_ls': unit_ls,
        'deposit_position_ls': deposit_position_ls,
        'custodian_ls': custodian_ls,
        'supplier_ls': supplier_ls,
        'status_ls': status_ls,
        'is_self_develop_ls': is_self_develop_ls,
        'network_ls': network_ls,
        'outsource_project_ls': outsource_project_ls
    })


@api_view(['GET'])
def get_consumable_maps(request):
    name_ls = ['鼠标', '键盘', '耳机', '转接头', 'USB扩展', '耳机海绵套', 'USB转网口', '显示器', '麦克风', '硒鼓']
    name_qs = ConsumableMaterial.objects.values('name').distinct()
    if name_qs:
        name_ls.extend([item['name'] for item in list(name_qs) if item['name']])
        name_ls_ = list(set(name_ls))
        name_ls_.sort(key=name_ls.index)
        name_ls = name_ls_
    brand_ls = []
    brand_qs = ConsumableMaterial.objects.values('brand').distinct()
    if brand_qs:
        brand_ls.extend([item['brand'] for item in list(brand_qs) if item['brand']])
        brand_ls_ = list(set(brand_ls))
        brand_ls_.sort(key=brand_ls.index)
        brand_ls = brand_ls_
    supplier_ls = ['西安轩刚商贸', '京东商城']
    supplier_qs = ConsumableMaterial.objects.values('supplier').distinct()
    if supplier_qs:
        supplier_ls.extend([item['supplier'] for item in list(supplier_qs) if item['supplier']])
        supplier_ls_ = list(set(supplier_ls))
        supplier_ls_.sort(key=supplier_ls.index)
        supplier_ls = supplier_ls_
    return REST_SUCCESS({
        'name_ls': name_ls,
        'brand_ls': brand_ls,
        'supplier_ls': supplier_ls
    })


# 新增固定资产
class FixedAssetsList(generics.ListCreateAPIView):
    model = FixedAssets
    queryset = model.objects.all().order_by('-entry_date')
    serializer_class = FixedAssetsSerializer
    table_name = model._meta.db_table
    verbose_name = model._meta.verbose_name

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.GET.get('name', '')
        if name:
            name_ls = name.split(',')
            queryset = queryset.filter(name__in=name_ls)
        deposit_position = request.GET.get('deposit_position', '')
        if deposit_position:
            deposit_position_ls = deposit_position.split(',')
            queryset = queryset.filter(deposit_position__in=deposit_position_ls)
        status = request.GET.get('status', '')
        if status:
            status_ls = status.split(',')
            queryset = queryset.filter(status__in=status_ls)
        network = request.GET.get('network', '')
        if network:
            queryset = queryset.filter(network=network)

        fuzzy_params = {}
        fuzzy_params['asset_number'] = request.GET.get('asset_number', '')
        fuzzy_params['inner_number'] = request.GET.get('inner_number', '')
        fuzzy_params['user_name'] = request.GET.get('user_name', '')

        filter_params = {}
        for k, v in fuzzy_params.items():
            if v != None and v != '':
                k = k + '__contains'
                filter_params[k] = v

        if filter_params:
            queryset = queryset.filter(**filter_params)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @set_create_log
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# 修改资产数据
class FixedAssetsDetail(generics.RetrieveUpdateDestroyAPIView):
    model = FixedAssets
    queryset = model.objects.all()
    serializer_class = FixedAssetsSerializer
    table_name = model._meta.db_table
    verbose_name = model._meta.verbose_name

    @set_update_log
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @set_delete_log
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return REST_SUCCESS({'msg': '删除成功'})


# 新增耗材
class ConsumableMaterialList(generics.ListCreateAPIView):
    model = ConsumableMaterial
    queryset = model.objects.all().order_by('-create_time')
    serializer_class = ConsumableMaterialSerializer
    table_name = model._meta.db_table
    verbose_name = model._meta.verbose_name

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.GET.get('name', '')
        if name:
            name_ls = name.split(',')
            queryset = queryset.filter(name__in=name_ls)

        fuzzy_params = {}
        fuzzy_params['model_code'] = request.GET.get('model_code', '')
        fuzzy_params['serial_number'] = request.GET.get('serial_number', '')
        fuzzy_params['user_name'] = request.GET.get('user_name', '')

        filter_params = {}
        for k, v in fuzzy_params.items():
            if v != None and v != '':
                k = k + '__contains'
                filter_params[k] = v

        if filter_params:
            queryset = queryset.filter(**filter_params)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @set_create_log
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ConsumableMaterialDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ConsumableMaterial
    queryset = model.objects.all()
    serializer_class = ConsumableMaterialSerializer
    table_name = model._meta.db_table
    verbose_name = model._meta.verbose_name

    @set_update_log
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @set_delete_log
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return REST_SUCCESS({'msg': '删除成功'})


class AssetStatusRecordList(generics.ListCreateAPIView):
    model = FixedAssetStatusRecord
    queryset = model.objects.all().order_by('-create_time')
    serializer_class = AssetStatusRecordSerializer
    table_name = model._meta.db_table
    verbose_name = model._meta.verbose_name

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        fixed_asset_id = request.GET.get('fixed_asset_id', '')
        if fixed_asset_id:
            queryset = queryset.filter(fixed_asset_id=fixed_asset_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @set_create_log
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# 下载固定资产导入模板
@api_view(['GET'])
def get_export_asset_template(request):
    current_path = os.path.dirname(__file__)
    file_name = request.GET.get('file_name')
    if not file_name:
        return REST_FAIL({'msg': 'file_name不能为空'})
    filepath = os.path.join(current_path, 'export_template/{}.xlsx'.format(file_name))
    return create_excel_resp(filepath, file_name)


# 批量插入固定资产
def insert_fixed_assets(datas):
    count = 0
    for data in datas:
        now_ts = datetime.datetime.now()
        count += 1
        lineNo = count + 1
        asset_number = data.get('asset_number')
        qs = FixedAssets.objects.filter(asset_number=asset_number)
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                if qs:
                    data['update_time'] = now_ts
                    try:
                        qs.update(**data)
                    except Exception as e:
                        return VIEW_FAIL(msg='固定资产存储失败, 错误所在行：{}, error:{}'.format(lineNo, str(e)))
                else:
                    try:
                        fixed_asset = FixedAssets.objects.create(**data)
                    except Exception as e:
                        return VIEW_FAIL(msg='固定资产存储失败, 错误所在行：{}, error:{}'.format(lineNo, str(e)))
                    FixedAssetStatusRecord.objects.create(fixed_asset_id=fixed_asset.id, status=fixed_asset.status,
                                                          receive_date=fixed_asset.receive_date,
                                                          user_name=fixed_asset.user_name,
                                                          user_work_id=fixed_asset.user_work_id,
                                                          department=fixed_asset.department,
                                                          subsector=fixed_asset.subsector)
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                logger.error('固定资产存储失败,error:{}'.format(str(e)))
                return VIEW_FAIL(msg='固定资产存储失败, error:{}'.format(str(e)))


# 批量导入固定资产
@api_view(['POST'])
def upload_fixed_assets(request):
    try:
        try:
            file = request.FILES.get('file', '')
            if not file:
                return VIEW_FAIL(msg='上传文件不能为空')
            upload_path = get_file_path('asset', 'upload_files')
            with open(upload_path, 'wb') as f:
                for i in file.chunks():
                    f.write(i)
            df = pd.read_excel(upload_path, sheet_name='固定资产')
            datas = df.to_dict('records')
            datas = analysis_asset(datas)
            count = 0
            for data in datas:
                now_ts = datetime.datetime.now()
                count += 1
                lineNo = count + 1
                asset_number = data.get('asset_number')
                qs = FixedAssets.objects.filter(asset_number=asset_number)
                with transaction.atomic():
                    save_id = transaction.savepoint()
                    try:
                        if qs:
                            data['update_time'] = now_ts
                            try:
                                qs.update(**data)
                            except Exception as e:
                                logger.error('固定资产存储失败,error:{}'.format(str(e)))
                                return VIEW_FAIL(msg='固定资产存储失败, 错误所在行：{}, error:{}'.format(lineNo, str(e)))
                        else:
                            try:
                                fixed_asset = FixedAssets.objects.create(**data)
                            except Exception as e:
                                logger.error('固定资产存储失败,error:{}'.format(str(e)))
                                return VIEW_FAIL(msg='固定资产存储失败, 错误所在行：{}, error:{}'.format(lineNo, str(e)))
                            FixedAssetStatusRecord.objects.create(fixed_asset_id=fixed_asset.id,
                                                                  status=fixed_asset.status,
                                                                  receive_date=fixed_asset.receive_date,
                                                                  user_name=fixed_asset.user_name,
                                                                  user_work_id=fixed_asset.user_work_id,
                                                                  department=fixed_asset.department,
                                                                  subsector=fixed_asset.subsector)
                        transaction.savepoint_commit(save_id)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        logger.error('固定资产存储失败,error:{}'.format(str(e)))
                        return VIEW_FAIL(msg='固定资产存储失败, error:{}'.format(str(e)))
            return VIEW_SUCCESS(msg='导入成功')
        except Exception as e:
            logger.error('文件解析出错, error:{}'.format(str(e)))
            return VIEW_FAIL(msg='文件解析出错, error:{}'.format(str(e)))
    except Exception as e:
        logger.error('固定资产导入失败, error:{}'.format(str(e)))
        return VIEW_FAIL(msg='固定资产导入失败', data={'error': str(e)})


# 导出固定资产
@api_view(['GET'])
def export_fixed_assets(request):
    try:
        obj = FixedAssets.objects
        name = request.GET.get('name', '')
        if name:
            name_ls = name.split(',')
            obj = obj.filter(name__in=name_ls)
        deposit_position = request.GET.get('deposit_position', '')
        if deposit_position:
            deposit_position_ls = deposit_position.split(',')
            obj = obj.filter(deposit_position__in=deposit_position_ls)
        status = request.GET.get('status', '')
        if status:
            status_ls = status.split(',')
            obj = obj.filter(status__in=status_ls)
        network = request.GET.get('network', '')
        if network:
            obj = obj.filter(network=network)

        fuzzy_params = {}
        fuzzy_params['asset_number'] = request.GET.get('asset_number', '')
        fuzzy_params['inner_number'] = request.GET.get('inner_number', '')
        fuzzy_params['user_name'] = request.GET.get('user_name', '')
        filter_params = {}
        for k, v in fuzzy_params.items():
            if v != None and v != '':
                k = k + '__contains'
                filter_params[k] = v
        if filter_params:
            obj = obj.filter(**filter_params)
        qs = obj.values('asset_number', 'category', 'inner_number', 'name', 'brand', 'model_code', 'unit',
                        'deposit_position', 'entry_date', 'custodian', 'supplier', 'status', 'is_self_develop',
                        'outsource_project', 'network', 'intranet_ip', 'key_lock_number', 'receive_date', 'user_name',
                        'department', 'subsector', 'remarks')
        blank_path = os.path.dirname(__file__) + '/blank_files/固定资产表.xlsx'
        if not qs:
            return create_excel_resp(blank_path, '固定资产表')
        df = pd.DataFrame(list(qs))
        df.insert(0, 'no', range(1, 1 + len(df)))
        df['entry_date'] = df['entry_date'].map(lambda x: x.strftime('%Y-%m-%d') if x else x)
        df['receive_date'] = df['receive_date'].map(lambda x: x.strftime('%Y-%m-%d') if x else x)
        rename_maps = {
            'no': '序号',
            'category': '资产类别',
            'asset_number': '固定资产编号',
            'inner_number': '内部编号',
            'name': '资产名称',
            'brand': '设备品牌',
            'model_code': '规格型号',
            'unit': '计量单位',
            'deposit_position': '所放地点',
            'entry_date': '入库时间',
            'custodian': '保管人',
            'supplier': '供应商',
            'status': '资产状态',
            'is_self_develop': '是否自研',
            'outsource_project': '外包项目名称',
            'network': '内网或外网',
            'intranet_ip': '内网电脑IP地址',
            'key_lock_number': '钥匙锁编号',
            'receive_date': '领用时间',
            'user_name': '使用人',
            'department': '部门',
            'subsector': '分部门',
            'remarks': '备注'
        }
        df.rename(rename_maps, axis=1, inplace=True)
        file_path = get_file_path('asset', 'export_files')
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = writer.book
        fmt = workbook.add_format({'font_size': 11, 'text_wrap': True, 'valign': 'vcenter', 'font_name': '等线'})
        center_fmt = workbook.add_format({'font_size': 11, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center', 'font_name': '等线'})
        border_format = workbook.add_format({'border': 1})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'font_name': '等线',
                                         'bg_color': '#d9d9d9', 'text_wrap': True, 'valign': 'vcenter'})
        df.to_excel(writer, sheet_name='固定资产', header=False, index=False, startcol=0, startrow=1)
        worksheet = writer.sheets['固定资产']
        l_end = len(df.index) + 1
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, title_fmt)
        worksheet.set_column('A:A', 6, center_fmt)
        worksheet.set_column('B:E', 18, fmt)
        worksheet.set_column('F:N', 13, fmt)
        worksheet.set_column('O:O', 17, fmt)
        worksheet.set_column('P:P', 13, fmt)
        worksheet.set_column('Q:R', 17, fmt)
        worksheet.set_column('S:T', 13, fmt)
        worksheet.set_column('U:W', 26, fmt)
        worksheet.conditional_format('A1:W%d' % l_end, {'type': 'blanks', 'format': border_format})
        worksheet.conditional_format('A1:W%d' % l_end, {'type': 'no_blanks', 'format': border_format})
        writer.save()
        return create_excel_resp(file_path, '固定资产表')
    except Exception as e:
        logger.error('固定资产导出失败, error: {}'.format(traceback.format_exc()))
        return REST_FAIL({'msg': '固定资产导出失败, error: {}'.format(str(e))})


# 批量插入耗材信息
def insert_consumable_material(datas):
    insert_sql = '''insert into it_consumable_material(name, brand, model_code, serial_number, supplier, receive_date, 
                            user_name, user_work_id, department, subsector, create_time, update_time, remarks)
                            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    update_sql = '''update it_consumable_material set receive_date=%s,user_name=%s,user_work_id=%s,department=%s, 
                            subsector=%s,remarks=%s,update_time=%s where serial_number=%s'''
    insert_ls = []
    update_ls = []
    count = 0
    for data in datas:
        now_ts = datetime.datetime.now()
        count += 1
        serial_number = data.get('serial_number')
        qs = ConsumableMaterial.objects.filter(serial_number=serial_number)
        if qs:
            update_args = (data['receive_date'], data['user_name'], data['user_work_id'],
                           data['department'], data['subsector'], data['remarks'], now_ts, serial_number)
            update_ls.append(update_args)
        else:
            insert_args = (data['name'], data['brand'], data['model_code'], data['serial_number'], data['supplier'],
                           data['receive_date'], data['user_name'], data['user_work_id'],
                           data['department'], data['subsector'], now_ts, now_ts, data['remarks'])
            insert_ls.append(insert_args)
        if len(insert_ls) + len(update_ls) >= 30:
            execute_batch_sql(insert_sql, insert_ls)
            execute_batch_sql(update_sql, update_ls)
            insert_ls = []
            update_ls = []

    if len(insert_ls) + len(update_ls) > 0:
        execute_batch_sql(insert_sql, insert_ls)
        execute_batch_sql(update_sql, update_ls)


# 导入耗材
@api_view(['POST'])
def upload_consumable_material(request):
    try:
        try:
            file = request.FILES.get('file', '')
            if not file:
                return VIEW_FAIL(msg='上传文件不能为空')
            upload_path = get_file_path('material', 'upload_files')
            with open(upload_path, 'wb') as f:
                for i in file.chunks():
                    f.write(i)
            df = pd.read_excel(upload_path, sheet_name='耗材')
            datas = df.to_dict('records')
            datas = analysis_material(datas)
            try:
                insert_consumable_material(datas)
            except Exception as e:
                logger.error('耗材信息插入数据库失败, error:{}'.format(str(e)))
                error_code = e.args[0]
                if error_code == 1111:
                    msg = e.args[1]
                    error = e.args[1]
                else:
                    msg = '保存失败'
                    error = str(e)
                return VIEW_FAIL(msg=msg, data={'error': error})
            return VIEW_SUCCESS(msg='导入成功')
        except Exception as e:
            logger.error('文件解析出错, error:{}'.format(str(e)))
            return VIEW_FAIL(msg='文件解析出错, error:{}'.format(str(e)))
    except Exception as e:
        logger.error('耗材信息导入失败, error:{}'.format(str(e)))
        return VIEW_FAIL(msg='耗材信息导入失败', data={'error': str(e)})


# 导出耗材
@api_view(['GET'])
def export_consumable_material(request):
    try:
        obj = ConsumableMaterial.objects
        name = request.GET.get('name', '')
        if name:
            name_ls = name.split(',')
            obj = obj.filter(name__in=name_ls)

        fuzzy_params = {}
        fuzzy_params['model_code'] = request.GET.get('model_code', '')
        fuzzy_params['serial_number'] = request.GET.get('serial_number', '')
        fuzzy_params['user_name'] = request.GET.get('user_name', '')

        filter_params = {}
        for k, v in fuzzy_params.items():
            if v != None and v != '':
                k = k + '__contains'
                filter_params[k] = v

        if filter_params:
            obj = obj.filter(**filter_params)
        qs = obj.values('name', 'brand', 'model_code', 'serial_number', 'user_name', 'department', 'subsector',
                        'supplier', 'receive_date','remarks')
        blank_path = os.path.dirname(__file__) + '/blank_files/耗材表.xlsx'
        if not qs:
            return create_excel_resp(blank_path, '耗材表')
        df = pd.DataFrame(list(qs))
        # df.insert(0, 'no', range(1, 1 + len(df)))
        df['receive_date'] = df['receive_date'].map(lambda x: x.strftime('%Y-%m-%d') if x else x)
        rename_maps = {
            'name': '名称',
            'brand': '品牌',
            'model_code': '规格型号',
            'serial_number': '序列号',
            'user_name': '领用人',
            'department': '部门',
            'subsector': '分部门',
            'supplier': '供应商',
            'receive_date': '领用时间',
            'remarks': '备注'
        }
        df.rename(rename_maps, axis=1, inplace=True)
        file_path = get_file_path('material', 'export_files')
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = writer.book
        fmt = workbook.add_format({'font_size': 11, 'text_wrap': True, 'valign': 'vcenter', 'font_name': '等线'})
        center_fmt = workbook.add_format(
            {'font_size': 11, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center', 'font_name': '等线'})
        border_format = workbook.add_format({'border': 1})
        title_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'font_name': '等线',
                                         'bg_color': '#d9d9d9', 'text_wrap': True, 'valign': 'vcenter'})
        df.to_excel(writer, sheet_name='耗材', header=False, index=False, startcol=0, startrow=1)
        worksheet = writer.sheets['耗材']
        l_end = len(df.index) + 1
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, title_fmt)
        worksheet.set_column('A:B', 13, fmt)
        worksheet.set_column('C:D', 16, fmt)
        worksheet.set_column('E:E', 16, fmt)
        worksheet.set_column('F:G', 25, fmt)
        worksheet.set_column('H:I', 18, fmt)
        worksheet.set_column('J:J', 25, fmt)
        worksheet.conditional_format('A1:J%d' % l_end, {'type': 'blanks', 'format': border_format})
        worksheet.conditional_format('A1:J%d' % l_end, {'type': 'no_blanks', 'format': border_format})
        writer.save()
        return create_excel_resp(file_path, '耗材表')
    except Exception as e:
        logger.error('耗材导出失败, error: {}'.format(traceback.format_exc()))
        return REST_FAIL({'msg': '耗材导出失败, error: {}'.format(str(e))})
