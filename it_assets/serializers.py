from rest_framework import serializers, validators
from it_assets.models import FixedAssets, ConsumableMaterial, FixedAssetStatusRecord
from django.db import transaction

import datetime
import logging

logger = logging.getLogger('django')


class FixedAssetsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FixedAssets
        fields = ('id', 'asset_number', 'category', 'inner_number', 'name', 'brand', 'model_code', 'unit',
                  'deposit_position', 'entry_date', 'custodian', 'supplier', 'status', 'is_self_develop',
                  'outsource_project', 'network', 'intranet_ip', 'key_lock_number', 'receive_date', 'user_name',
                  'user_work_id', 'department', 'subsector', 'total_amount', 'remarks', 'expect_periods', 'used_periods',
                  'total_depreciated', 'current_year_depreciated')

    def create(self, validated_data):
        fixed_asset = FixedAssets.objects.create(**validated_data)
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                FixedAssetStatusRecord.objects.create(fixed_asset_id=fixed_asset.id, status=fixed_asset.status,
                                                      receive_date=fixed_asset.receive_date,
                                                      user_name=fixed_asset.user_name,
                                                      user_work_id=fixed_asset.user_work_id,
                                                      department=fixed_asset.department,
                                                      subsector=fixed_asset.subsector)
                fixed_asset.save()
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                logger.error('状态记录存储失败,error:{}'.format(str(e)))
                raise serializers.ValidationError('状态记录存储失败')
        return fixed_asset


class ConsumableMaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsumableMaterial
        fields = ('id', 'name', 'brand', 'model_code', 'serial_number', 'supplier', 'receive_date', 'user_name',
                  'user_work_id', 'department', 'subsector', 'remarks')


class AssetStatusRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = FixedAssetStatusRecord
        fields = ('id', 'fixed_asset', 'status', 'receive_date', 'user_name', 'user_work_id', 'department', 'subsector',
                  'create_time', 'remarks')

    def create(self, validated_data):
        status_record = FixedAssetStatusRecord.objects.create(**validated_data)
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                qs = FixedAssets.objects.filter(id=status_record.fixed_asset_id)
                qs.update(status=status_record.status, receive_date=status_record.receive_date,
                          user_name=status_record.user_name, user_work_id=status_record.user_work_id,
                          department=status_record.department, subsector=status_record.subsector)
                status_record.save()
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                logger.error('状态记录存储失败,error:{}'.format(str(e)))
                raise serializers.ValidationError('状态记录存储失败')
        return status_record
