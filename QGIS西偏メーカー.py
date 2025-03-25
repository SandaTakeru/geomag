def import_lib():
    import math
    from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsProject, QgsField
    from qgis.PyQt.QtCore import QVariant
    from qgis.utils import iface

def create_lines_from_attributes():
    # ポイントレイヤを取得
    point_layer = iface.activeLayer()
    if point_layer.geometryType() != QgsWkbTypes.PointGeometry:
        print("ポイントレイヤを選択してください。")
        return

    # 新しいラインレイヤを作成
    line_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "西偏", "memory")
    provider = line_layer.dataProvider()

    # 元のポイントレイヤの属性情報を維持するためのフィールドを追加
    fields = point_layer.fields()
    provider.addAttributes(fields)
    line_layer.updateFields()

    # ポイントレイヤの属性情報を基にラインを生成
    for feature in point_layer.getFeatures():
        lat = feature.geometry().asPoint().y()
        lon = feature.geometry().asPoint().x()
        declination = feature["in_decimal"]  # 属性情報から偏角を取得

        # 偏角に基づいてラインの終点を計算
        angle_deg = declination
        angle_rad = math.radians(angle_deg)
        length = 0.05  # ラインの長さ（度）

        str_lat = lat - length * math.cos(angle_rad)
        str_lon = lon - length * math.sin(angle_rad)
        end_lat = lat + length * math.cos(angle_rad)
        end_lon = lon + length * math.sin(angle_rad)

        # ラインの地物を作成
        line_feature = QgsFeature()
        line_feature.setGeometry(QgsGeometry.fromPolylineXY([QgsPointXY(str_lon, str_lat), QgsPointXY(end_lon, end_lat)]))
        line_feature.setAttributes(feature.attributes())
        provider.addFeature(line_feature)

    line_layer.updateExtents()
    QgsProject.instance().addMapLayer(line_layer)
    
# スクリプトを実行してラインを生成
import_lib()
create_lines_from_attributes()

'''
■使い方説明　2025年3月25日　三田武
これは、国土地理院で公開されている偏角の電子データを基に、西偏を表現するラインレイヤを生成するPythonコードです。生成AIを使って作りました。
引用元は右のとおりです。[国土地理院ウェブサイト]https://www.gsi.go.jp/buturisokuchi/menu03_magnetic_chart.html#menu02
これらのデータの利用には、右の利用規約に従ってください。[国土地理院コンテンツ利用規約]https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html

1;データソースマネージャーから、CSVファイルを読み込んでください。

2;予め、CSVファイルの度分秒を10進数に変換してください。(ex; 10°30' → 10.5)
  フィールド計算機で、to_decimalを使い、マイナスをかけるとよいです。[ - to_decimal(  "field_3" ) ]

3;QGISのPython consoleを使います。
  def 部分をそれぞれコピペして実行。（関数定義）
  スクリプトをそれぞれコピペして実行。

プラグイン化することも考えたのですが、元のデータサイズが小さいのでジオパッケージそのものを配ってしまえば済むと判断しました。
データは、2010年（平成22年）以降は５年ごとに公開されています。最新版の「磁気図2020.0年値」を使いました。

'''