#http://192.168.12.9:8090/?src_path=/home/bisag/Desktop/change_detection/2020_GCS.tif&ref_path=/home/bisag/Desktop/change_detection/2014_GCS.tif
import os,sys
import rasterio
from flask import Flask, request
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.exposure import match_histograms
from shapely.geometry import Polygon, MultiPolygon
from typing import List
import traceback
from flask import abort
from shapely.geometry import box
import geopandas as gpd
from rasterio.mask import mask


def check_if_grayscale(img: np.ndarray) -> bool:
    if len(img.shape) < 3:
        return True
    if img.shape[2] == 1:
        return True
    b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    if (b == g).all() and (b == r).all():
        return True
    return False


def image_diff(img1: np.ndarray, img2: np.ndarray):
    img1_f = img1.astype(np.float32)
    img2_f = img2.astype(np.float32)

    diff_image = np.absolute(img1_f - img2_f).astype('uint8')

    return diff_image


def threshold_image(img: np.ndarray, threshes: List):
    if img.ndim == 3:
        assert img.shape[2] == len(threshes)
        channel_outs = [None] * img.shape[2]
        for i in range(img.shape[2]):
            _, channel_outs[i] = cv2.threshold(img[:, :, i], threshes[i], 255, cv2.THRESH_BINARY)
        return cv2.merge(channel_outs)
    else:
        assert len(threshes) == 1
        return cv2.threshold(img, threshes[0], 255, cv2.THRESH_BINARY)[1]


def display_hist_matched(img1: np.ndarray, img2: np.ndarray, img3: np.ndarray):
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(8, 3))
    for aa in (ax1, ax2, ax3):
        aa.set_axis_off()

    ax1.imshow(img1)
    ax1.set_title('Source')
    ax2.imshow(img2)
    ax2.set_title('Reference')
    ax3.imshow(img3)
    ax3.set_title('Matched')
    plt.tight_layout()
    plt.show()


def save_changes(bw_img: np.ndarray, ref_raster_img_path: str):
    try:
        raster = rasterio.open(ref_raster_img_path)
        binary_img = np.copy(bw_img)
        if binary_img.ndim == 3:
            binary_img = np.logical_or.reduce(binary_img > 0, axis=2).astype(np.uint8)
            binary_img[binary_img == 1] = 255
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []
        for contour in contours:
            points = list(map(lambda point: list(raster.xy(point[0][1], point[0][0])), contour))
            polygons.append(Polygon(points))
        geo_collection = MultiPolygon(polygons)
        return geo_collection.wkt
    except Exception as e:
        abort(500, {'message': f'{e}'})


def calculate_threshold(img1: np.ndarray, img2: np.ndarray, is_gray: bool) -> List:
    if is_gray:
        th = [(np.std(img1) + np.std(img2)) / 2]
    else:
        img1_r_std = np.std(img1[:, :, 0])
        img1_g_std = np.std(img1[:, :, 1])
        img1_b_std = np.std(img1[:, :, 2])
        img2_r_std = np.std(img2[:, :, 0])
        img2_g_std = np.std(img2[:, :, 1])
        img2_b_std = np.std(img2[:, :, 2])
        th = [(img1_r_std + img2_r_std) / 2, (img1_g_std + img2_g_std) / 2, (img1_b_std + img2_b_std) / 2]
    th = list(map(lambda val: int(val), th))
    return th


def process(ref_path, src_path, ref_geotiff_path):
    try:
        reference = cv2.imread(ref_path)
        image = cv2.imread(src_path)
        is_gray = False

        if check_if_grayscale(image) or check_if_grayscale(reference):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            reference = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
            is_gray = True
        else:
            reference = cv2.cvtColor(reference, cv2.COLOR_BGR2RGB)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            is_gray = False

        ksize = (25, 25)

        if image.shape != reference.shape:
            image = cv2.resize(image, (reference.shape[1], reference.shape[0]))

        reference = cv2.GaussianBlur(reference, ksize, 0)
        # plt.imshow(reference, cmap='gray')
        # plt.show()
        image = cv2.GaussianBlur(image, ksize, 0)
        # plt.imshow(image, cmap='gray')
        # plt.show()

        matched = match_histograms(image, reference, multichannel=True)
        threshold = calculate_threshold(reference, image, is_gray)

        # plt.imshow(matched, cmap='gray')
        # plt.show()
        # display_hist_matched(image, reference, matched)

        diff = image_diff(matched, reference)

        # plt.imshow(diff, cmap='gray')
        # plt.show()
        #
        cv2.imwrite("matched.jpg", matched)
        cv2.imwrite("ref.jpg", reference)
        diff_thresh = threshold_image(diff, threshold)

        # plt.imshow(diff_thresh, cmap='gray')
        # plt.show()

        kernel = np.ones((15, 15), np.uint8)
        thresh_img = cv2.morphologyEx(diff_thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        thresh_img = cv2.cvtColor(thresh_img, cv2.COLOR_RGB2GRAY)
        thresh_img[thresh_img > 50] = 255
        cv2.imwrite("thresh.jpg", thresh_img)

        # plt.imshow(thresh_img, cmap='gray')
        # plt.show()

        # overlaid = cv2.addWeighted(thresh_img, 0.3, reference, 0.7, 0.0)
        # if is_gray:
        #     cv2.imwrite(ref_geotiff_path, overlaid)
        # else:
        #     cv2.imwrite(ref_geotiff_path, cv2.cvtColor(overlaid, cv2.COLOR_RGB2BGR))
        changes_wkt = save_changes(thresh_img, ref_geotiff_path)
        return changes_wkt
    except Exception as e:
        traceback.print_exc()
        abort(500, {'message': f'{e}'})


def convert_to_epsg_4326(fp: str) -> str:
    out_fp = fp.split(".tif")[0] + "_epsg_4326.tif"
    os.system(f"gdalwarp -t_srs EPSG:4326 {fp} {out_fp}")
    if not os.path.isfile(out_fp):
        abort(500, {'message': f'GDAL Warp failed for {fp}'})
    return out_fp


def create_rendered_image(fp: str) -> str:
    pwd = os.getcwd()
    script_path = os.path.join(pwd, "createRendered.py")
    os.system(f"/usr/bin/python3 {script_path} {fp}")
    rendered_fp = fp.split(".tif")[0] + "_rendered.tif"
    if not os.path.isfile(rendered_fp):
        abort(500, {'message': f'QGIS rendered image creation failed for {fp}'})
    return rendered_fp


def get_bbox(img_path: str) -> Polygon:
    raster = rasterio.open(img_path)
    polygon = box(*raster.bounds)
    return polygon


def find_intersection_bb(img_path1: str, img_path2: str):
    try:
        bbox1 = get_bbox(img_path1)
        bbox2 = get_bbox(img_path2)
        intersection = bbox1.intersection(bbox2)
        return intersection
    except Exception as e:
        traceback.print_exc()
        abort(500, {"message": f"Exception encountered while calculating intersection of two rasters: {e}"})


def get_features(gdf):
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def clip_image(img_path: str, polygon: Polygon) -> str:
    try:
        raster = rasterio.open(img_path)

        geom = gpd.GeoDataFrame({'geometry': polygon}, index=[0], crs={'init': 'epsg:4326', 'no_defs': True})
        geom = geom.to_crs(crs=raster.crs.data)
        coords = get_features(geom)

        clipped_raster, clipped_raster_transform = mask(dataset=raster, shapes=coords, crop=True)
        out_meta = raster.meta.copy()

        out_meta.update({"driver": "GTiff",
                         "height": clipped_raster.shape[1],
                         "width": clipped_raster.shape[2],
                         "transform": clipped_raster_transform,
                         })

        print(out_meta["crs"])

        out_img_path = img_path.split(".tif")[0] + "_clipped.tif"
        with rasterio.open(out_img_path, "w", **out_meta) as f:
            f.write(clipped_raster)
        return out_img_path
    except Exception as e:
        traceback.print_exc()
        abort(500, {"message": f"Clipping failed for {img_path}: {e}"})


#app = Flask(__name__)


#@app.route("/", methods=['GET'])
def change_detection2(src_path,ref_path):
    
    if not src_path.endswith(".tif") or not ref_path.endswith(".tif"):
        abort(422, {'message': 'Invalid file format'})
    if not os.path.isfile(src_path) or not os.path.isfile(ref_path):
        abort(404, {'message': 'Provided files not found'})

    temp_filepaths = []

    src_epsg_path = convert_to_epsg_4326(src_path)
    ref_epsg_path = convert_to_epsg_4326(ref_path)
    temp_filepaths.append(src_epsg_path)
    temp_filepaths.append(ref_epsg_path)

    intersection = find_intersection_bb(src_epsg_path, ref_epsg_path)
    src_clipped_path = clip_image(src_epsg_path, intersection)
    ref_clipped_path = clip_image(ref_epsg_path, intersection)
    temp_filepaths.append(src_clipped_path)
    temp_filepaths.append(ref_clipped_path)

    src_rendered_path = create_rendered_image(src_clipped_path)
    ref_rendered_path = create_rendered_image(ref_clipped_path)
    temp_filepaths.append(src_rendered_path)
    temp_filepaths.append(ref_rendered_path)

    src_rendered_jpg_path = src_rendered_path.replace('.tif', '.jpg')
    ref_rendered_jpg_path = ref_rendered_path.replace('.tif', '.jpg')

    cv2.imwrite(src_rendered_jpg_path, cv2.imread(src_rendered_path))
    cv2.imwrite(ref_rendered_jpg_path, cv2.imread(ref_rendered_path))

    changes_wkt = process(src_rendered_path, ref_rendered_path, ref_path)
    #dirname = os.path.dirname(path)

    with open('/home/bisag/.local/share/QGIS/QGIS3/profiles/default/python/plugins/change_detection/wkt.txt','w') as f:
        f.write(str(changes_wkt))
    print(changes_wkt)
    return changes_wkt


if __name__ == "__main__":
    # src_path='/home/bisag/Desktop/change_detection/2020_GCS.tif'
    # ref_path='/home/bisag/Desktop/change_detection/2014_GCS.tif'
    src_path,ref_path =sys.argv[1], sys.argv[2]
    change_detection2(src_path,ref_path)
    #app.run(debug=True, port=8090, host="0.0.0.0")


