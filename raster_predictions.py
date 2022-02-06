import gdal, osr
import numpy as np
import pandas as pd


def save_raster(input, array, output_file):
    """Short summary.

    Parameters
    ----------
    input : str
        Description of parameter `input`.
    array : np.array
        Description of parameter `array`.
    output_file : str
        Description of parameter `output_file`.

    Returns
    -------
    type
        Description of returned object.

    """

    raster = gdal.Open(input)
    geo = raster.GetGeoTransform()
    wkt = raster.GetProjection()
    band = raster.GetRasterBand(1)
    driver = gdal.GetDriverByName("GTiff")

    dst_ds = driver.Create(output_file,
                           band.XSize,
                           band.YSize,
                           1,
                           gdal.GDT_Float32)

    dst_ds.GetRasterBand(1).WriteArray(array)
    dst_ds.GetRasterBand(1).SetNoDataValue(-999)
    dst_ds.SetGeoTransform(geo)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    dst_ds.SetProjection(srs.ExportToWkt())
    ds = None
    dst_ds = None


def rater_predictions(file_path, output_path, dataframe, inputs, model):
    '''
    Creates and saves raster of predictions
    Inputs:
        file_path: string of inputs path
        file_path: string of output path
        dataframe: pandas dataframe with predictors
        inputs: list of covariate names
        model: trained model
    Outputs:
        saves raster
    '''
    raster = gdal.Open(file_path)
    array = raster.ReadAsArray()[:, :, :]
    mins = dataframe[inputs].min().values
    maxs = dataframe[inputs].max().values
    normalised = ((array - mins.reshape((mins.shape[0], 1, 1)))/(maxs.reshape((maxs.shape[0], 1, 1)) - mins.reshape((mins.shape[0], 1, 1))))
    container = []
    for n in range(array.shape[2]):
        container.append(model.predict(np.swapaxes(normalised[:,:,n], 1, 0))[:, 0].ravel())
    save_raster(file_path,
                np.swapaxes(np.vstack(container), 1, 0),
                output_path)
