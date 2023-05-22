from django.conf.urls import url, include
from it_assets import views


urlpatterns = [
    url(r'^get-assets-maps$', views.get_assets_maps),
    url(r'^get-consumable-maps', views.get_consumable_maps),
    url(r'^fixed-assets$', views.FixedAssetsList.as_view()),
    url(r'^fixed-assets/(?P<pk>[0-9]+)$', views.FixedAssetsDetail.as_view()),
    url(r'^consumable-material$', views.ConsumableMaterialList.as_view()),
    url(r'^consumable-material/(?P<pk>[0-9]+)$', views.ConsumableMaterialDetail.as_view()),
    url(r'^fa-status-record$', views.AssetStatusRecordList.as_view()),
    url(r'^export-asset-template$', views.get_export_asset_template),
    url(r'^upload-fixed-asset$', views.upload_fixed_assets),
    url(r'^export-fixed-asset$', views.export_fixed_assets),
    url(r'^upload-consumable-material$', views.upload_consumable_material),
    url(r'^export-consumable-material$', views.export_consumable_material),
    url(r'^batch-delete-asset$', views.batch_delete_asset),
    url(r'^batch-delete-material$', views.batch_delete_material),
]
