#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sep 24, 2025

@author: bill


Append features from one GeoPackage layer to another.
If schemas differ, only copy matching fields.

Optional tool: requires the QGIS Python bindings (qgis.core), which the rest of
OWI does not use. On the dbx-qgis distrobox, run it as:
    distrobox enter dbx-qgis -- ~/Projects-qbox/OWI/.venv-dbx/bin/python src/gpkg_tools.py
"""

from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsFeature,
    QgsProject
)
import sys
import os

# ---------------- CONFIG ----------------
source_gpkg = "/path/to/source.gpkg"
source_layer_name = "source_layer"

target_gpkg = "/path/to/target.gpkg"
target_layer_name = "target_layer"
# ----------------------------------------

def append_layer(source_gpkg, source_layer_name, target_gpkg, target_layer_name):
    """
    Append features from one GeoPackage layer to another.
    If schemas differ, only copy matching fields.
    """

    # Load source layer
    src = QgsVectorLayer(f"{source_gpkg}|layername={source_layer_name}", source_layer_name, "ogr")
    if not src.isValid():
        raise RuntimeError("Source layer failed to load")

    # Load target layer
    tgt = QgsVectorLayer(f"{target_gpkg}|layername={target_layer_name}", target_layer_name, "ogr")
    if not tgt.isValid():
        raise RuntimeError("Target layer failed to load")

    # Determine common fields
    src_fields = set([f.name() for f in src.fields()])
    tgt_fields = set([f.name() for f in tgt.fields()])
    common_fields = src_fields.intersection(tgt_fields)

    print(f"Source fields: {src_fields}")
    print(f"Target fields: {tgt_fields}")
    print(f"Common fields: {common_fields}")

    # Prepare editing
    if not tgt.isEditable():
        tgt.startEditing()

    # Iterate through source features
    for feat in src.getFeatures():
        new_feat = QgsFeature(tgt.fields())
        # copy only matching attributes
        for f in common_fields:
            new_feat.setAttribute(f, feat[f])
        # copy geometry
        new_feat.setGeometry(feat.geometry())
        tgt.addFeature(new_feat)

    # Commit changes
    if not tgt.commitChanges():
        raise RuntimeError("Failed to commit changes to target layer")

    print("Append complete")

def append_unlocs_to_locs():
    from OWI_config import OWIfiles
    owif = OWIfiles()
    dir = owif.OWI_DOWNLOAD_WELLSSHP_DIR, 
    locs = owif.CWI_LOCS, 
    unlocs = owif.CWI_UNLOCS
    
    # ---------------- CONFIG ----------------
    source_gpkg = "/path/to/source.gpkg"
    source_layer_name = "source_layer"
    
    target_gpkg = "/path/to/target.gpkg"
    target_layer_name = "target_layer"
    # ----------------------------------------

    QgsApplication.setPrefixPath("/usr", True)  # may need adjusting
    qgs = QgsApplication([], False)
    qgs.initQgis()


    try:
        append_layer(source_gpkg, source_layer_name, target_gpkg, target_layer_name)
    finally:
        qgs.exitQgis()

# ---------------- RUN ----------------
if __name__ == "__main__":
    append_unlocs_to_locs()
    print (r'\\\\\\\\\\\\\\\\\\ DONE ///////////////////')
