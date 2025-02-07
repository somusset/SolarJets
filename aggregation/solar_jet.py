from .shape_utils import SolarPoint, SolarBox
from dataclasses import dataclass, field
import datetime

@dataclass
class SolarJet:
    '''
    Object that contains the jet information after aggregation and clustering.
    Jet information is in solar coordinates - there is no need to go back to the metadata
    '''
    jet_id: str = field(init=False)
    start_time: datetime.datetime
    end_time: datetime.datetime
    base_location: SolarPoint
    box: SolarBox
    box_minus_sigma: SolarBox
    box_plus_sigma: SolarBox
    box_sigma: float
    hek_event: str

    @classmethod
    def from_dict(cls, data):
        obj = cls(start_time=data['start_time'], end_time=data['end_time'],
                    base_location=SolarPoint.from_dict(data['base_location']),
                    box=SolarBox.from_dict(data['box']),
                    box_minus_sigma=SolarBox.from_dict(data['box_minus_sigma']),
                    box_plus_sigma=SolarBox.from_dict(data['box_plus_sigma']),
                    box_sigma=data['box_sigma'],
                    hek_event=data['hek_event'] )
        if 'jet_id' in data:
            obj.add_jet_id(data['jet_id'])
        return obj

    def to_dict(self):
        data = {}
        data['start_time'] = self.start_time
        data['end_time'] = self.end_time
        data['base_location'] = self.base_location.to_dict()
        data['box'] = self.box.to_dict()
        data['box_minus_sigma'] = self.box_minus_sigma.to_dict()
        data['box_plus_sigma'] = self.box_plus_sigma.to_dict()
        data['box_sigma'] = self.box_sigma
        data['hek_event'] = self.hek_event
        if hasattr(self, 'jet_id'):
            data['jet_id'] = self.jet_id

        return data
    
    def add_jet_id(self, id):
        self.jet_id = id