import numpy as np
import os
from dataclasses import dataclass
from shapely.geometry import Polygon
from panoptes_aggregation.reducers.shape_metric_IoU import IoU_metric
from panoptes_aggregation.reducers.point_process_data import temporal_metric
import yaml
from .meta_file_handler import SubjectMetadata
from .image_handler import solar_conversion
import datetime
from dateutil.parser import parse


with open(os.path.join(os.path.split(__file__)[0], '..',
                       'configs/Reducer_config_workflow_21225_V50.59_shapeExtractor_temporalRotateRectangle.yaml'), 'r') as infile:
    EPS_T = yaml.safe_load(infile)['reducer_config']['shape_reducer_dbscan']['eps_t']


@dataclass
class BasePoint:
    x: float
    y: float
    displayTime: float
    subject_id: int
    probability: float = 0

    def to_dict(self):
        data = {}
        data['subject_id'] = self.subject_id
        data['x'] = self.x
        data['y'] = self.y
        data['displayTime'] = self.displayTime
        data['probability'] = self.probability

        if hasattr(self, 'var_x'):
            data['var_x'] = self.var_x
        if hasattr(self, 'var_y'):
            data['var_y'] = self.var_y

        if hasattr(self, 'extracts'):
            data['extracts'] = [ext.to_dict() for ext in self.extracts]

        return data

    @classmethod
    def from_dict(cls, data):
        obj = cls(x=data['x'], y=data['y'], displayTime=data['displayTime'], subject_id=data['subject_id'], probability=data['probability'])

        if 'var_x' in data:
            obj.var_x = data['var_x']
        if 'var_y' in data:
            obj.var_y = data['var_y']

        if 'extracts' in data:
            obj.extracts = []
            for extract in data['extracts']:
                ext = cls(x=extract['x'], y=extract['y'], displayTime=extract['displayTime'], subject_id=extract['subject_id'], probability=extract['probability'])
                obj.extracts.append(ext)

        return obj

    @property
    def coordinate(self):
        return np.asarray([self.x, self.y])

    @property
    def extract_dists(self):
        if not hasattr(self, '_extract_dists'):
            if not hasattr(self, 'extracts'):
                raise ValueError('Point does not have extracts!')
            dists = []
            for extract in self.extracts:
                dists.append(get_point_distance(self, extract))
            self._extract_dists = np.mean(dists)

        return self._extract_dists

    def get_hpc_coordinates_values(self, metafile):
        '''
        Transform pixel coordinates into solar helioprojective cartesian coordinates
        using the metadata provided as a SubjectMetadata object
        '''
        metadata = metafile.get_subjectdata_by_id(self.subject_id)
        hpc_x, hpc_y = solar_conversion(self.subject_id, self.x, self.y, metadata)

        return [hpc_x, hpc_y]

# The following was an idea to get some stddev but should not be used as it is not weighted. I'm working on having the variance calculated during aggregation being part of the data in jets 

#    def get_position_stddev(self):
#        extracts_x = [extract.x for extract in self.extracts]
#        extracts_y = [extract.y for extract in self.extracts]
#        x_stddev = np.std(extracts_x)
#        y_stddev = np.std(extracts_y)
#        return [x_stddev, y_stddev]

@dataclass
class SolarPoint:
    x: float
    y: float
    var_x: float
    var_y: float
    unit: str
    coordinate_system: str
    time: datetime.datetime

    def to_dict(self):
        data = {}
        data['x'] = self.x
        data['y'] = self.y
        data['var_x'] = self.var_x
        data['var_y'] = self.var_y
        data['unit'] = self.unit
        data['coord_syst'] = self.coordinate_system
        data['time'] = self.time
        return data

    @classmethod
    def from_dict(cls, data):
        obj = cls(x=data['x'], y=data['y'], var_x=data['var_x'], var_y=data['var_y'], unit=data['unit'], coordinate_system=data['coord_syst'], time=parse(data['time']))
        return obj

@dataclass
class Box:
    xcenter: float
    ycenter: float
    width: float
    height: float
    angle: float
    displayTime: float
    subject_id: int
    probability: float = 0

    def to_dict(self):
        data = {}
        data['subject_id'] = self.subject_id
        data['xcenter'] = self.xcenter
        data['ycenter'] = self.ycenter
        data['width'] = self.width
        data['height'] = self.height
        data['angle'] = self.angle
        data['displayTime'] = self.displayTime
        data['probability'] = self.probability

        if hasattr(self, 'sigma'):
            data['sigma'] = self.sigma

        if hasattr(self, 'extracts'):
            data['extracts'] = [ext.to_dict() for ext in self.extracts]

        return data

    @classmethod
    def from_dict(cls, data):
        obj = cls(xcenter=data['xcenter'], ycenter=data['ycenter'], width=data['width'], height=data['height'],
                  angle=data['angle'], displayTime=data['displayTime'], subject_id=data['subject_id'], probability=data['probability'])

        if 'sigma' in data:
            obj.sigma = data['sigma']

        if 'extracts' in data:
            obj.extracts = []
            for extract in data['extracts']:
                ext = cls(xcenter=extract['xcenter'], ycenter=extract['ycenter'], width=extract['width'], height=extract['height'],
                          angle=extract['angle'], displayTime=extract['displayTime'], subject_id=extract['subject_id'], probability=extract['probability'])
                obj.extracts.append(ext)

        return obj

    def get_box_edges(self):
        '''
            Return the corners of the box given one corner, width, height
            and angle

            Outputs
            --------
            corners : numpy.ndarray
                Length 4 array with coordinates of the box edges
        '''
        centre = np.array([self.xcenter, self.ycenter])
        original_points = np.array(
            [
                [self.xcenter - 0.5 * self.width, self.ycenter - 0.5 * self.height],  # This would be the box if theta = 0
                [self.xcenter + 0.5 * self.width, self.ycenter - 0.5 * self.height],
                [self.xcenter + 0.5 * self.width, self.ycenter + 0.5 * self.height],
                [self.xcenter - 0.5 * self.width, self.ycenter + 0.5 * self.height],
                # repeat the first point to close the loop
                [self.xcenter - 0.5 * self.width, self.ycenter - 0.5 * self.height]
            ]
        )
        rotation = np.array([[np.cos(self.angle), np.sin(self.angle)], [-np.sin(self.angle), np.cos(self.angle)]])
        corners = np.matmul(original_points - centre, rotation) + centre
        return corners
    
    def get_hpc_box_corners(self, metafile):
        metadata = metafile.get_subjectdata_by_id(self.subject_id)
        corners = self.get_box_edges()
        hpc_corners = np.array(
            [
                solar_conversion(self.subject_id, corners[0][0], corners[0][1], metadata),
                solar_conversion(self.subject_id, corners[1][0], corners[1][1], metadata),
                solar_conversion(self.subject_id, corners[2][0], corners[2][1], metadata),
                solar_conversion(self.subject_id, corners[3][0], corners[3][1], metadata),
                solar_conversion(self.subject_id, corners[4][0], corners[4][1], metadata),
            ]
        )
        return hpc_corners
    
    def get_hpc_box_center(self, metafile):
        metadata = metafile.get_subjectdata_by_id(self.subject_id)
        hpc_box_center = solar_conversion(self.subject_id, self.xcenter, self.ycenter, metadata)
        return hpc_box_center

# The following were a fix, but now it is better to just get the pix to arcsec conversion factor to calculate any distance in arcsec

#    def get_hpc_width(self, metafile):
#        hpc_corners = self.get_hpc_box_corners(metafile)
#        length1 = np.sqrt((hpc_corners[0][0]-hpc_corners[1][0])**2 + (hpc_corners[0][1]-hpc_corners[1][1])**2)
#        length2 = np.sqrt((hpc_corners[1][0]-hpc_corners[2][0])**2 + (hpc_corners[1][1]-hpc_corners[2][1])**2)
#        return np.min([length1,length2])
#    
#    def get_hpc_height(self, metafile):
#        hpc_corners = self.get_hpc_box_corners(metafile)
#        length1 = np.sqrt((hpc_corners[0][0]-hpc_corners[1][0])**2 + (hpc_corners[0][1]-hpc_corners[1][1])**2)
#        length2 = np.sqrt((hpc_corners[1][0]-hpc_corners[2][0])**2 + (hpc_corners[1][1]-hpc_corners[2][1])**2)
#        return np.max([length1,length2])

    def get_shapely_polygon(self):
        return Polygon(self.get_box_edges())

#    def get_plus_minus_sigma(self, sigma):
    def get_plus_minus_sigma(self):
        # calculate the bounding box for the cluster confidence
        plus_box, minus_box = self.get_plus_minus_boxes()
        return plus_box.get_box_edges(), minus_box.get_box_edges()
    
    def get_plus_minus_boxes(self):
        # calculate the bounding box for the cluster confidence
        plus_sigma, minus_sigma = sigma_shape(
            [self.xcenter, self.ycenter, self.width, self.height, self.angle], self.sigma)

        plus_box = Box(*plus_sigma, self.displayTime, self.subject_id)
        minus_box = Box(*minus_sigma, self.displayTime, self.subject_id)

        return plus_box, minus_box

    @property
    def params(self):
        return [self.xcenter, self.ycenter, self.width, self.height, self.angle, self.displayTime]

    @property
    def extract_IoU(self):
        if not hasattr(self, '_extract_IoU'):
            if not hasattr(self, 'extracts'):
                raise ValueError('Box does not have extracts!')
            IoUs = []
            for extract in self.extracts:
                IoUs.append(1. - IoU_metric([self.xcenter, self.ycenter, self.width, self.height, self.angle, self.displayTime],
                                            [extract.xcenter, extract.ycenter, extract.width, extract.height, extract.angle, extract.displayTime],
                                            'temporalRotateRectangle', EPS_T))
            self._extract_IoU = np.mean(IoUs)

        return self._extract_IoU


def get_point_distance(p1: BasePoint, p2: BasePoint) -> float:
    '''
        Get Euclidiean distance between two points p1 and p2

        Inputs
        ------
        p1: BasePoint
            BasePoint object for the first point
        p2: BasePoint
            BasePoint object for the second point

        Outputs
        --------
        dist : float
            Euclidian distance between (x0, y0) and (x1, y1)
    '''
    return temporal_metric([p1.x, p1.y, p1.displayTime], [p2.x, p2.y, p2.displayTime])


def get_box_distance(box1: Box, box2: Box) -> float:
    '''
        Get point-wise distance betweeen 2 boxes.
        Calculates and find the average distance between each edge
        for each box

        Inputs
        ------
        box1 : Box
            parameters corresponding to the first box (see `get_box_edges`)
        box2 : Box
            parameters corresponding to the second box (see `get_box_edges`)

        Outputs
        -------
        dist : float
            Average point-wise distance between the two box edges
    '''
    b1_edges = box1.get_box_edges()[:4]
    b2_edges = box2.get_box_edges()[:4]

    # build a distance matrix between the 4 edges
    # since the order of edges may not be the same
    # for the two boxes
    dists = np.zeros((4, 4))
    for c1 in range(4):
        for c2 in range(4):
            dists[c1, c2] = get_point_distance(*b1_edges[c1], *b2_edges[c2])

    # then collapse the matrix into the minimum distance for each point
    # does not matter which axis, since we get the least distance anyway
    mindist = dists.min(axis=0)

    return np.average(mindist)


def get_box_iou(box1: Box, box2: Box) -> float:
    return 1 - IoU_metric(box1.params, box2.params, 'temporalRotateRectangle', EPS_T)


def scale_shape(params, gamma):
    '''
        scale the box by a factor of gamma
        about the center

        Inputs
        ------
        params : list
            Parameter list corresponding to the box (x, y, w, h, a).
            See `get_box_edges`
        gamma : float
            Scaling parameter. Equal to sqrt(1 - sigma), where sigma
            is the box confidence from the SHGO box-averaging step

        Outputs
        -------
        scaled_params : list
            Parameter corresponding to the box scaled by the factor gamma
    '''
    return [
        # first two params are box center so these lines do not apply anymore:
        ## upper left corner moves
        #params[0] + (params[2] * (1 - gamma) / 2),
        #params[1] + (params[3] * (1 - gamma) / 2),
        
        # box center does not change
        params[0],
        params[1],
        # width and height scale
        gamma * params[2],
        gamma * params[3],
        # angle does not change
        params[4]
    ]


def sigma_shape(params, sigma):
    '''
        calculate the upper and lower bounding box
        based on the sigma of the cluster

        Inputs
        ------
        params : list
            Parameter list corresponding to the box (x, y, w, h, a).
            See `get_box_edges`
        sigma : float
            Confidence of the box, given by the minimum distance of the
            SHGO box averaging step. See the `panoptes_aggregation` module.

        Outputs
        -------
        plus_sigma : list
            Parameters corresponding to the box scaled to the upper sigma bound
        minus_sigma : list
            Parameters corresponding to the box scaled to the lower sigma bound
    '''
    gamma = np.sqrt(1 - sigma)
    plus_sigma = scale_shape(params, 1 / gamma)
    minus_sigma = scale_shape(params, gamma)
    return plus_sigma, minus_sigma

@dataclass 
class SolarBox:
    center: SolarPoint
    corners: list[SolarPoint]
    width: float
    height: float
    length_unit: str
    angle: float
    angle_unit: str

    def to_dict(self):
        data = {}
        data['center'] = self.center.to_dict()
        data['corners'] = [corner.to_dict() for corner in self.corners]
        data['width'] = self.width
        data['height'] = self.height
        data['angle'] = self.angle
        data['length_unit'] = self.length_unit
        data['angle_unit'] = self.angle_unit

        return data

    @classmethod
    def from_dict(cls, data):
        center = SolarPoint.from_dict(data['center'])
        
        corners = []
        for corner in data['corners']:
            ext = SolarPoint.from_dict(corner)
            corners.append(ext)
        
        obj = cls(center=center, corners=corners, width=data['width'], height=data['height'], angle=data['angle'], length_unit=data['length_unit'], angle_unit=data['angle_unit'])

        return obj
