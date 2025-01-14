u"""
Created on 16/08/16
by fccoelho
license: GPL V3 or Later
"""
import os
from tempfile import NamedTemporaryFile
from io import BytesIO
import pandas as pd
import geopandas as gpd
from dbfread import DBF

try:
    from pysus.utilities._readdbc import ffi, lib
except (ImportError, ModuleNotFoundError):
    from _readdbc import ffi, lib


def read_dbc(filename, encoding='utf-8', raw=False):
    """
    Opens a DATASUS .dbc file and return its contents as a pandas
    Dataframe.
    :param filename: .dbc filename
    :param encoding: encoding of the data
    :param raw: Skip type conversion. Set it to True to avoid type conversion errors
    :return: Pandas Dataframe.
    """
    if isinstance(filename, str):
        filename = filename.encode()
    with NamedTemporaryFile(delete=False) as tf:
        dbc2dbf(filename, tf.name.encode())
        dbf = DBF(tf.name, encoding=encoding, raw=raw)
        df = gpd.GeoDataFrame(list(dbf))
    os.unlink(tf.name)

    return df


def dbc2dbf(infile, outfile):
    """
    Converts a DATASUS dbc file to a DBF database.
    :param infile: .dbc file name
    :param outfile: name of the .dbf file to be created.
    """
    if isinstance(infile, str):
        infile = infile.encode()
    if isinstance(outfile, str):
        outfile = outfile.encode()
    p = ffi.new('char[]', os.path.abspath(infile))
    q = ffi.new('char[]', os.path.abspath(outfile))

    lib.dbc2dbf([p], [q])

    # print(os.path.exists(outfile))


def dbc2csv(filename, tempdir='.', encoding='iso-8859-1', raw=False):
    outputfile = str(filename).replace(".dbc", ".csv")
    if isinstance(filename, str):
        filename = filename.encode()
    with NamedTemporaryFile(delete=True, dir=tempdir) as tf:
        dbc2dbf(filename, tf.name.encode())
        dbf = DBF(tf.name, encoding=encoding, raw=raw)

        with open(outputfile, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(dbf.field_names)
            for record in dbf:
                writer.writerow(list(record.values()))

