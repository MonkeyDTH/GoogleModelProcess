import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, Polygon, box
import folium
import math
import googlemaps
from datetime import datetime

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
    
    # 只获取建筑物轮廓
    tags = {'building': True}
    
    # 使用点和距离下载数据
    gdf = ox.features_from_point((lat, lon), tags=tags, dist=distance)
    
    # 过滤出最近的建筑物
    if not gdf.empty:
        # 创建中心点
        center = Point(lon, lat)
        
        # 将数据转换为UTM投影坐标系
        utm_zone = int(math.floor((lon + 180) / 6) + 1)
        utm_crs = f'EPSG:326{utm_zone:02d}' if lat >= 0 else f'EPSG:327{utm_zone:02d}'
        
        # 转换坐标系
        gdf_proj = gdf.to_crs(utm_crs)
        center_proj = gpd.GeoSeries([center], crs=gdf.crs).to_crs(utm_crs)[0]
        
        # 在投影坐标系中计算距离
        gdf_proj['distance'] = gdf_proj.geometry.distance(center_proj)
        
        # 获取最近的建筑物
        nearest_building = gdf_proj.sort_values('distance').iloc[0]
        
        # 返回单个建筑物的GeoDataFrame，转回原始坐标系
        return gpd.GeoDataFrame([nearest_building], geometry='geometry', crs=utm_crs).to_crs(gdf.crs)
    
    return gdf

def get_coordinates_from_google(address, api_key):
    """
    使用Google Maps API获取地址的经纬度
    :param address: 地址字符串
    :param api_key: Google Maps API密钥
    :return: (纬度, 经度)元组
    """
    # 创建Google Maps客户端
    gmaps = googlemaps.Client(key=api_key)
    
    # 地理编码
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError("无法找到该地址")
    except Exception as e:
        raise Exception(f"Google Maps API错误: {str(e)}")

def main(api_key, clear_cache=False):
    """
    主函数
    :param api_key: Google Maps API密钥
    :param clear_cache: 是否在处理完成后清理缓存
    """
    # 目标地址
    address = "10912 S Yukon Ave, Inglewood, CA 90303"
    
    try:
        # 创建osm目录（如果不存在）
        import os
        os.makedirs('osm', exist_ok=True)
        
        # 使用Google Maps API获取精确坐标
        lat, lon = get_coordinates_from_google(address, api_key)
        center_point = (lat, lon)
        print(f"Google Maps 坐标: ({lon}, {lat})")
        
        # 下载建筑物数据（搜索范围设置为50米，以确保获取目标建筑）
        tags = {'building': True}
        gdf = ox.features_from_point((lat, lon), tags=tags, dist=50)
        
        if not gdf.empty:
            # 创建中心点
            center = Point(lon, lat)
            
            # 将数据转换为UTM投影坐标系
            utm_zone = int(math.floor((lon + 180) / 6) + 1)
            utm_crs = f'EPSG:326{utm_zone:02d}' if lat >= 0 else f'EPSG:327{utm_zone:02d}'
            
            # 转换坐标系
            gdf_proj = gdf.to_crs(utm_crs)
            center_proj = gpd.GeoSeries([center], crs=gdf.crs).to_crs(utm_crs)[0]
            
            # 在投影坐标系中计算距离
            gdf_proj['distance'] = gdf_proj.geometry.distance(center_proj)
            
            # 获取最近的建筑物
            nearest_building = gdf_proj.sort_values('distance').iloc[0]
            building_data = gpd.GeoDataFrame([nearest_building], geometry='geometry', crs=utm_crs).to_crs(gdf.crs)
            
            # 保存数据到osm目录
            save_osm_data(building_data, 'osm/target_building.geojson')
            
            # 可视化数据并保存到osm目录
            visualize_osm_data(building_data, center_point=center_point, 
                             save_path='osm/target_building_map.html')
            
            print("数据处理完成！")
            print("建筑物轮廓已保存到：osm/target_building.geojson")
            print("可视化地图已保存到：osm/target_building_map.html")
        else:
            print("未找到目标建筑物")
        
        # 根据设置决定是否清理缓存
        if clear_cache:
            ox.settings.cache_folder = ''  # 禁用缓存
            if os.path.exists(os.path.expanduser('~/.cache/osmnx')):
                import shutil
                shutil.rmtree(os.path.expanduser('~/.cache/osmnx'))
                print("缓存已清理")
        
    except Exception as e:
        print(f"发生错误：{str(e)}")

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

if __name__ == '__main__':
    # 设置Google Maps API密钥
    API_KEY = 'AIzaSyDLgBT4f31Oo509m9jAdm9Nlx-OOufXg7E'  # 替换为您的API密钥
    
    # 运行主程序
    main(API_KEY, clear_cache=False)