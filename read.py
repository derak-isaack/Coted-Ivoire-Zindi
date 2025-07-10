import rasterio
from rasterio.mask import mask
import train as gpd
import json

# 1. Load GeoJSON file
geojson_path = "train.geojson"  # Replace with your file
gdf = gpd.read_file(geojson_path)

# Ensure CRS matches DEM (EPSG:4326 for SRTM/COP30)
gdf = gdf.to_crs("EPSG:4326")

# Extract geometry in GeoJSON-like dict format
geometry = gdf.geometry.values[0]  # Single polygon
# For MultiPolygon or complex shapes:
# geometry = [geom.__geo_interface__ for geom in gdf.geometry]

# 2. Open the DEM
dem_path = "cotedivoire_cop30.tif"
with rasterio.open(dem_path) as src:
    # 3. Mask the DEM
    out_image, out_transform = mask(
        src, 
        [geometry],  # Must be a list of shapes
        crop=True,
        all_touched=True  # Optional: include pixels touching geometry
    )
    out_meta = src.meta.copy()

# 4. Update metadata
out_meta.update({
    "driver": "GTiff",
    "height": out_image.shape[1],
    "width": out_image.shape[2],
    "transform": out_transform
})

# 5. Save clipped DEM
with rasterio.open("clipped_dem.tif", "w", **out_meta) as dest:
    dest.write(out_image)

print("✅ DEM clipped and saved as 'clipped_dem.tif'")