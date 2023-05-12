from django.db import models


class FixedAssets(models.Model):
    asset_number = models.CharField(verbose_name='资产编号', max_length=60, null=True, blank=True)
    category = models.CharField(verbose_name='资产类别', max_length=60, default='电子设备', null=True, blank=True)
    inner_number = models.CharField(verbose_name='内部编号', max_length=60, null=True, blank=True)
    name = models.CharField(verbose_name='资产名称', max_length=100, null=True, blank=True)
    brand = models.CharField(verbose_name='品牌', max_length=100, null=True, blank=True)
    model_code = models.CharField(verbose_name='规格型号', max_length=100, null=True, blank=True)
    unit = models.CharField(verbose_name='单位', max_length=10, null=True, blank=True)
    deposit_position = models.CharField(verbose_name='存放地点', max_length=100, null=True, blank=True)
    entry_date = models.DateField(verbose_name='入库时间', null=True, blank=True)
    custodian = models.CharField(max_length=60, verbose_name='保管人', null=True, blank=True)
    supplier = models.CharField(verbose_name='供应商', max_length=100, null=True, blank=True)
    status = models.CharField(verbose_name='资产状态', max_length=50, null=True, blank=True)
    is_self_develop = models.CharField(verbose_name='是否自研', max_length=10, null=True, blank=True)
    outsource_project = models.CharField(verbose_name='外包项目名称', max_length=100, null=True, blank=True)
    network = models.CharField(verbose_name='网络环境', max_length=20, null=True, blank=True)
    intranet_ip = models.CharField(verbose_name='内网电脑IP地址', max_length=60, null=True, blank=True)
    key_lock_number = models.CharField(verbose_name='钥匙锁编号', max_length=60, null=True, blank=True)
    receive_date = models.DateField(verbose_name='领用时间', null=True, blank=True)
    user_name = models.CharField(verbose_name='使用人', max_length=50, null=True, blank=True)
    user_work_id = models.CharField(verbose_name='工号', max_length=30, null=True, blank=True)
    department = models.CharField(verbose_name='部门', max_length=100, null=True, blank=True)
    subsector = models.CharField(verbose_name='分部门', max_length=100, null=True, blank=True)
    total_amount = models.DecimalField(verbose_name='资产原值', max_digits=20, decimal_places=2, null=True, blank=True)
    expect_periods = models.IntegerField(verbose_name='预计使用期间数', null=True, blank=True)
    used_periods = models.IntegerField(verbose_name='已经使用期间数', null=True, blank=True)
    total_depreciated = models.DecimalField(verbose_name='累计折旧', max_digits=16, decimal_places=2, null=True, blank=True)
    current_year_depreciated = models.DecimalField(verbose_name='本年累计折旧', max_digits=16, decimal_places=2, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True, auto_now_add=False)
    remarks = models.TextField(verbose_name='备注', null=True, blank=True)
    field_1 = models.CharField(verbose_name='字段1', max_length=100, null=True, blank=True)
    field_2 = models.CharField(verbose_name='字段2', max_length=100, null=True, blank=True)
    field_3 = models.CharField(verbose_name='字段3', max_length=100, null=True, blank=True)
    field_4 = models.CharField(verbose_name='字段4', max_length=100, null=True, blank=True)
    field_5 = models.CharField(verbose_name='字段5', max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'it_fixed_assets'
        verbose_name = '固定资产表'
        verbose_name_plural = verbose_name


class ConsumableMaterial(models.Model):
    name = models.CharField(verbose_name='名称', max_length=100, null=True, blank=True)
    brand = models.CharField(verbose_name='品牌', max_length=100, null=True, blank=True)
    model_code = models.CharField(verbose_name='规格型号', max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=50, verbose_name='序列号', null=True, blank=True)
    supplier = models.CharField(verbose_name='供应商', max_length=100, null=True, blank=True)
    receive_date = models.DateField(verbose_name='领用时间', null=True, blank=True)
    user_name = models.CharField(verbose_name='使用人', max_length=50, null=True, blank=True)
    user_work_id = models.CharField(verbose_name='工号', max_length=30, null=True, blank=True)
    department = models.CharField(verbose_name='部门', max_length=100, null=True, blank=True)
    subsector = models.CharField(verbose_name='分部门', max_length=100, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True, auto_now_add=False)
    remarks = models.TextField(verbose_name='备注', null=True, blank=True)
    field_1 = models.CharField(verbose_name='字段1', max_length=100, null=True, blank=True)
    field_2 = models.CharField(verbose_name='字段2', max_length=100, null=True, blank=True)
    field_3 = models.CharField(verbose_name='字段3', max_length=100, null=True, blank=True)
    field_4 = models.CharField(verbose_name='字段4', max_length=100, null=True, blank=True)
    field_5 = models.CharField(verbose_name='字段5', max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'it_consumable_material'
        verbose_name = '耗材表'
        verbose_name_plural = verbose_name


class FixedAssetStatusRecord(models.Model):
    fixed_asset = models.ForeignKey(FixedAssets, verbose_name='固定资产名称', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='资产状态', max_length=50, null=True, blank=True)
    receive_date = models.DateField(verbose_name='领用时间', null=True, blank=True)
    user_name = models.CharField(verbose_name='使用人', max_length=50, null=True, blank=True)
    user_work_id = models.CharField(verbose_name='工号', max_length=30, null=True, blank=True)
    department = models.CharField(verbose_name='部门', max_length=100, null=True, blank=True)
    subsector = models.CharField(verbose_name='分部门', max_length=100, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    remarks = models.TextField(verbose_name='备注', null=True, blank=True)

    class Meta:
        db_table = 'it_asset_status_record'
        verbose_name = '固定资产状态变更表'
        verbose_name_plural = verbose_name
