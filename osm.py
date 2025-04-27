import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, Polygon, box
import folium
import math

def download_osm_data_by_address(address, distance=1000, tags=None):
    """
    下载指定地址周边的OSM数据
    :param address: 地址字符串
    :param distance: 搜索半径（米）
    :param tags: 需要下载的特定标签
    :return: 下载的地理数据
    """
    # 获取地址的地理编码
    geolocator = ox.geocode(address)
    if not geolocator:
        raise ValueError("无法找到该地址")
    
    # 获取坐标
    lat, lon = geolocator[0], geolocator[1]
    
    # 使用place参数下载数据
    if tags is None:
        # 默认下载道路网络
        G = ox.graph_from_point((lat, lon), dist=distance, network_type='drive')
    else:
        # 使用点和距离下载数据
        gdf = ox.features_from_point((lat, lon), tags=tags, dist=distance)
        return gdf
    return G

def save_osm_data(data, filename):
    """
    保存OSM数据
    :param data: OSM数据（NetworkX图或GeoDataFrame）
    :param filename: 保存文件名
    """
    if isinstance(data, gpd.GeoDataFrame):
        data.to_file(filename)
    else:
        ox.save_graph_shapefile(data, filename)

def visualize_osm_data(data, center_point=None, save_path=None):
    """
    可视化OSM数据
    :param data: OSM数据
    :param center_point: 中心点坐标 (lat, lon)
    :param save_path: 保存路径
    """
    if center_point:
        m = folium.Map(location=center_point, zoom_start=15)
        # 添加中心点标记
        folium.Marker(
            center_point,
            popup='目标位置',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    else:
        if isinstance(data, gpd.GeoDataFrame):
            m = folium.Map(location=[data.geometry.centroid.y.mean(), 
                                   data.geometry.centroid.x.mean()],
                          zoom_start=15)
        else:
            m = folium.Map(location=[data.nodes[list(data.nodes)[0]]['y'],
                                   data.nodes[list(data.nodes)[0]]['x']],
                          zoom_start=15)

    if isinstance(data, gpd.GeoDataFrame):
        folium.GeoJson(data).add_to(m)
    else:
        ox.plot_graph_folium(data, graph_map=m)
    
    if save_path:
        m.save(save_path)
    return m

def main():
    # 目标地址
    address = "10912 Yukon Ave S, Inglewood, CA 90303"
    
    # 下载建筑数据
    tags = {
        'building': True,
        'amenity': True,
        'highway': True,
        'landuse': True
    }
    
    try:
        # 获取地理编码（更新为新的方法调用）
        geolocator = ox.geocode(address)
        center_point = (geolocator[0], geolocator[1])
        
        # 下载周边1000米范围的数据
        area_data = download_osm_data_by_address(address, distance=1000, tags=tags)
        
        # 保存数据
        save_osm_data(area_data, 'inglewood_area.geojson')
        
        # 可视化数据
        visualize_osm_data(area_data, center_point=center_point, 
                         save_path='inglewood_area_map.html')
        
        print("数据处理完成！请查看生成的地图文件：inglewood_area_map.html")
        
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == '__main__':
    main()