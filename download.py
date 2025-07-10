import ee
import geemap
import geopandas as gpd
from datetime import datetime
import os
from shapely.geometry import Polygon, MultiPolygon

# Initialize Earth Engine
ee.Initialize()

# Load GeoJSON
gdf = gpd.read_file("train.geojson")

# Create output folder
os.makedirs("monthly_composites", exist_ok=True)

def geometry_to_ee(geom):
    """Convert Shapely geometry to Earth Engine geometry"""
    if isinstance(geom, Polygon):
        return ee.Geometry.Polygon(list(geom.exterior.coords))
    elif isinstance(geom, MultiPolygon):
        # Get the largest polygon in the MultiPolygon
        largest = max(geom.geoms, key=lambda g: g.area)
        return ee.Geometry.Polygon(list(largest.exterior.coords))
    else:
        raise ValueError(f"Unsupported geometry type: {type(geom)}")

def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_mask = 1 << 10
    cirrus_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_mask).eq(0).And(qa.bitwiseAnd(cirrus_mask).eq(0))
    return image.updateMask(mask).divide(10000)

for index, row in gdf.iterrows():
    geom = row.geometry
    crop_id = row['ID']
    
    # Convert to EE geometry (handles both Polygon/MultiPolygon)
    try:
        roi = geometry_to_ee(geom)
        point = roi.centroid()  # Get centroid for filtering
    except Exception as e:
        print(f"⚠️ Skipping {crop_id}: {str(e)}")
        continue

    for month in range(2, 13):  # Feb to Dec
        start = datetime(2024, month, 1)
        end = datetime(2024, month + 1, 1) if month != 12 else datetime(2024, 12, 31)
        
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(point)
            .filterDate(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))  # Increased cloud threshold
            .map(mask_s2_clouds)
        )
        
        if collection.size().getInfo() == 0:
            print(f"⚠️ No images for {crop_id} in {start.strftime('%b')} 2024")
            continue
        
        median_image = collection.median()
        clipped = median_image.clip(roi)
        
        filename = f"s2_{crop_id}_2024_{start.strftime('%b')}.tif"
        path = os.path.join("monthly_composites", filename)
        
        try:
            geemap.ee_export_image(
                clipped,
                filename=path,
                scale=20,  # Reduced resolution for faster downloads
                region=roi,
                file_per_band=False,
            )
            print(f"✅ Saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to export {filename}: {str(e)}")