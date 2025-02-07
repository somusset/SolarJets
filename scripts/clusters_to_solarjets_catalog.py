import sys
import json
sys.path.append('.')

try:
    from aggregation.jet_cluster import JetCluster
    from aggregation.solar_jet import SolarJet
    from aggregation.meta_file_handler import SubjectMetadata
    from aggregation.shape_utils import get_point_distance, get_box_iou, SolarPoint, SolarBox
    from aggregation.io import NpEncoder
except ModuleNotFoundError:
    raise

metafile = SubjectMetadata('solar_jet_hunter_metadata.json')

with open('reductions/jet_cluster.json', 'r') as infile:
    clusters = [JetCluster.from_dict(data) for data in json.load(infile)]

solarjets = []

# loop over events
for cluster in clusters:
    # read the start and end times in the cluster, as well as the hek event
    start_time = cluster.start_time
    end_time = cluster.end_time
    # get conversion factor from metadata
    conv = metafile.get_pix2arcsec_conv_by_id(cluster.jets[0].subject_id)
    # get the hpc coordinates
    hpc_coordinates = cluster.base_location.get_hpc_coordinates_values(metafile)
    # get the variance on x and y and convert in arcsec using conversion factor
    var_x = cluster.base_location.var_x*conv
    var_y = cluster.base_location.var_y*conv
    # get the time corresponding to the coordinates
    base_time = cluster.base_time
    # create the base coordinate object with the information above
    base_location = SolarPoint(x=hpc_coordinates[0], y=hpc_coordinates[1], var_x=var_x, var_y=var_y, 
                               unit='arcsec', coordinate_system='HPC', time=base_time)

    # get the bigger box from the jets in the cluster and the associated time
    bbox_jet = cluster.get_jet_with_longer_box()
    # get the minus and plus boxes
    plus, minus = bbox_jet.box.get_plus_minus_boxes()

    # for each of the three boxes:
        # get the hpc coordinates for the center, pick the time of the biggest box, create the center coordinates object
        # get the corners coordinates, transform to hpc, and to object
        # transform height and width with conversion factor
        # assign all these to a SolarBox object

    # main box
    box_center_hpc = bbox_jet.box.get_hpc_box_center(metafile)
    box_center = SolarPoint(x=box_center_hpc[0], y=box_center_hpc[1], var_x=0, var_y=0, unit='arcsec', coordinate_system='HPC', time=bbox_jet.time_info['box'])
    box_corners_hpc = bbox_jet.box.get_hpc_box_corners(metafile)
    box_corners = []
    for i in range(5):
        corner_coords = box_corners_hpc[0]
        obj = SolarPoint(x=corner_coords[0], y=corner_coords[1], var_x=0, var_y=0, unit='arcsec', coordinate_system='HPC', time=bbox_jet.time_info['box'])
        box_corners.append(obj)
    box_width = bbox_jet.box.width*conv
    box_heigth = bbox_jet.box.height*conv

    box = SolarBox(center=box_center, corners=box_corners, width=box_width, height=box_heigth, angle=bbox_jet.box.angle, length_unit='arcsec', angle_unit='rad')

    # plus box
    plus_center_hpc = plus.get_hpc_box_center(metafile)
    plus_center = SolarPoint(x=box_center_hpc[0], y=box_center_hpc[1], var_x=0, var_y=0, unit='arcsec', coordinate_system='HPC', time=bbox_jet.time_info['box'])
    plus_corners_hpc = plus.get_hpc_box_corners(metafile)
    plus_corners = []
    for i in range(5):
        corner_coords = plus_corners_hpc[0]
        obj = SolarPoint(x=corner_coords[0], y=corner_coords[1], var_x=0, var_y=0, unit='arcsec', coordinate_system='HPC', time=bbox_jet.time_info['box'])
        plus_corners.append(obj)
    plus_width = bbox_jet.box.width*conv
    plus_heigth = bbox_jet.box.height*conv

    plus_box = SolarBox(center=plus_center, corners=plus_corners, width=plus_width, height=plus_heigth, angle=plus.angle, length_unit='arcsec', angle_unit='rad')

    # minus box
    minus_center_hpc = minus.get_hpc_box_center(metafile)
    minus_center = SolarPoint(x=box_center_hpc[0], y=box_center_hpc[1], var_x=0, var_y=0, unit='arcsec', coordinate_system='HPC', time=bbox_jet.time_info['box'])
    minus_corners_hpc = minus.get_hpc_box_corners(metafile)
    minus_corners = []
    for i in range(5):
        corner_coords = minus_corners_hpc[0]
        obj = SolarPoint(x=corner_coords[0], y=corner_coords[1], var_x=0, var_y=0, unit='arcsec', coordinate_system='HPC', time=bbox_jet.time_info['box'])
        minus_corners.append(obj)
    minus_width = bbox_jet.box.width*conv
    minus_heigth = bbox_jet.box.height*conv

    minus_box = SolarBox(center=minus_center, corners=minus_corners, width=minus_width, height=minus_heigth, angle=minus.angle, length_unit='arcsec', angle_unit='rad')

    # get everything together in a SolarJet object
    object = SolarJet(start_time=start_time, end_time=end_time, base_location=base_location, box=box, box_minus_sigma=minus_box, box_plus_sigma=plus_box, box_sigma=bbox_jet.box.sigma, hek_event=cluster.hek_event)

    solarjets.append(object)

with open('reductions/solar_jets.json', 'w') as outfile:
    json.dump([jet.to_dict() for jet in solarjets], outfile, cls=NpEncoder, indent=4)
