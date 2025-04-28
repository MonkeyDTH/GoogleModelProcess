import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point, Polygon, box
import folium
import math
import googlemaps
from datetime import datetime
import numpy as np
import json
import os
import time
import logging
from logging.handlers import RotatingFileHandler

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

def create_building_obj(building_data, output_file):
    """
    从建筑物轮廓创建OBJ文件
    :param building_data: 包含建筑物数据的GeoDataFrame
    :param output_file: 输出的OBJ文件路径
    """
    # 获取建筑物高度（如果没有高度信息，使用默认值10米）
    height = float(building_data.get('height', building_data.get('building:height', 10.0)))
    
    # 获取建筑物轮廓坐标
    if isinstance(building_data.geometry, Polygon):
        coords = list(building_data.geometry.exterior.coords)
    else:
        raise ValueError("建筑物轮廓必须是多边形")
    
    # 创建顶点列表
    vertices = []
    # 底面顶点
    for x, y in coords[:-1]:  # 去掉最后一个重复点
        vertices.append((x, y, 0))
    # 顶面顶点
    for x, y in coords[:-1]:
        vertices.append((x, y, height))
    
    # 创建面列表
    faces = []
    n = len(coords) - 1  # 多边形顶点数
    
    # 底面
    bottom = list(range(1, n+1))
    faces.append(bottom)
    
    # 顶面
    top = list(range(n+1, 2*n+1))
    faces.append(top[::-1])  # 反向以确保法向朝上
    
    # 侧面
    for i in range(n):
        v1 = i + 1
        v2 = (i + 1) % n + 1
        v3 = v2 + n
        v4 = v1 + n
        faces.append([v1, v2, v3, v4])
    
    # 写入OBJ文件
    with open(output_file, 'w') as f:
        # 写入顶点
        for x, y, z in vertices:
            f.write(f'v {x} {y} {z}\n')
        
        # 写入面
        for face in faces:
            f.write('f ' + ' '.join(str(i) for i in face) + '\n')

def setup_logger(timestamp):
    """
    配置日志记录器
    """
    # 创建日志文件名
    log_file = f'osm/log/process_log_{timestamp}.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger('BuildingProcessor')
    logger.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_file

def process_single_address(address, api_key, logger):
    """
    处理单个地址
    """
    try:
        logger.info(f"开始处理地址: {address}")
        
        # 使用Google Maps API获取精确坐标
        lat, lon = get_coordinates_from_google(address, api_key)
        center_point = (lat, lon)
        logger.info(f"获取到坐标: ({lon}, {lat})")
        
        # 下载建筑物数据
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
            
            # 生成文件名（使用地址作为文件名）
            file_name = ''.join(c if c.isalnum() else '_' for c in address)
            file_name = file_name[:50]  # 限制文件名长度
            
            # 保存数据到对应目录
            save_osm_data(building_data, os.path.join('osm/result/geojson', f'{file_name}.geojson'))
            create_building_obj(nearest_building, os.path.join('osm/result/obj', f'{file_name}.obj'))
            visualize_osm_data(building_data, center_point=center_point, 
                             save_path=os.path.join('osm/result/html', f'{file_name}.html'))
            
            logger.info(f"地址 {address} 处理成功")
            return True, "处理成功"
        else:
            logger.warning(f"地址 {address} 未找到目标建筑物")
            return False, "未找到目标建筑物"
            
    except Exception as e:
        logger.error(f"处理地址 {address} 时发生错误: {str(e)}", exc_info=True)
        return False, str(e)

def main(api_key, input_file, clear_cache=False):
    """
    主函数 - 批量处理版本
    """
    try:
        # 设置时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        start_time = time.time()
        
        # 确保主输出目录和分类目录存在
        os.makedirs('osm/result/obj', exist_ok=True)
        os.makedirs('osm/result/html', exist_ok=True)
        os.makedirs('osm/result/geojson', exist_ok=True)
        
        # 设置日志记录器
        logger, log_file = setup_logger(timestamp)
        
        logger.info("开始执行程序")
        
        # 确保osm目录存在
        os.makedirs('osm', exist_ok=True)
        
        # 读取输入的JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            addresses = json.load(f)
        
        if not isinstance(addresses, list):
            raise ValueError("JSON文件必须包含地址列表")
        
        # 初始化统计数据
        total_count = len(addresses)
        success_count = 0
        failed_count = 0
        
        logger.info(f"开始批量处理，共有 {total_count} 个地址待处理")
        
        # 处理每个地址
        for index, address in enumerate(addresses, 1):
            logger.info(f"正在处理第 {index}/{total_count} 个地址")
            
            # 处理单个地址（移除了base_dir参数）
            success, message = process_single_address(address, api_key, logger)
            
            # 更新统计数据
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        # 记录最终统计结果
        logger.info("处理完成！统计结果：")
        logger.info(f"总地址数: {total_count}")
        logger.info(f"成功处理: {success_count}")
        logger.info(f"处理失败: {failed_count}")
        logger.info(f"成功率: {(success_count/total_count*100):.2f}%")
        
        # 计算并记录运行时间
        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"程序运行时间：{total_time:.1f}秒")
        
        # 根据设置决定是否清理缓存
        if clear_cache:
            ox.settings.cache_folder = ''
            if os.path.exists(os.path.expanduser('~/.cache/osmnx')):
                import shutil
                shutil.rmtree(os.path.expanduser('~/.cache/osmnx'))
                logger.info("缓存已清理")
        
        print(f"处理完成！详细日志已保存到：{log_file}")
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"发生错误：{str(e)}", exc_info=True)
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
    
    # 输入文件路径
    INPUT_FILE = 'addresses.json'  # JSON文件，包含地址列表
    
    # 运行主程序
    main(API_KEY, INPUT_FILE, clear_cache=False)