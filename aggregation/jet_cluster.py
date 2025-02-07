import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from .zoo_utils import get_subject_image
from .jet import Jet
from .shape_utils import BasePoint, Box
import tqdm
from dataclasses import dataclass, field
import datetime


@dataclass
class JetCluster:
    jets: list[Jet]
    start_time: datetime.datetime = field(init=False)
    end_time: datetime.datetime = field(init=False)
    base_location: BasePoint = field(init=False)
    base_time: datetime.datetime = field(init=False)
    hek_event: str = field(init=False)

    def __post_init__(self):
        '''
            Initiate the JetCluster with a list of jet objects that are contained by that cluster.
        '''
        self.start_time = self.jets[0].time_info['start']
        self.end_time = self.jets[-1].time_info['end']
        self.base_location = self.jets[0].start
        self.base_time = self.jets[0].time_info['start']
        self.hek_event = self.jets[0].sol_standard

    @classmethod
    def from_dict(cls, data):
        jets = []
        #for jet_dict in data:
        for jet_dict in data['jets']:
            jets.append(Jet.from_dict(jet_dict))

        #obj = cls(jets=jets, start_time=data['start_time'], end_time=data['end_time'])
        obj = cls(jets=jets)
        return obj

    def to_dict(self):
        data = {}
        data['start_time'] = self.start_time
        data['end_time'] = self.end_time
        data['base_location'] = self.base_location.to_dict()
        data['base_time'] = self.base_time
        data['hek_event'] = self.hek_event
        data['jets'] = [jet.to_dict() for jet in self.jets]

        return data
#        return {
#            'start_time': self.start_time,
#            'end_time': self.end_time,
#            'base_location': self.base_location.to_dict(),
#            'hek_event': self.hek_event,
#            'jets': [jet.to_dict() for jet in self.jets]
#        }

    def get_average_box(self):
        '''
        Using the boxes for the jets composing the cluster, calculate the average box:
        average width, height, angle
        average box center position
        '''
        heights = np.array([jet.box.height for jet in self.jets])
        widths = np.array([jet.box.width for jet in self.jets])
        angles = np.array([jet.box.angle for jet in self.jets])
        xcs = np.array([jet.box.xcenter for jet in self.jets])
        ycs = np.array([jet.box.ycenter for jet in self.jets])
        times = np.array([jet.time_info.box for jet in self.jets])
        ## need to add the uncertainties!
        result = Box(xcenter = np.mean(xcs), 
                     ycenter = np.mean(ycs), 
                     width = np.mean(widths),
                     height = np.mean(heights),
                     angle = np.mean(angles),
                     displayTime = 0,
                     subject_id = 0,
                     probability = 0)
        #result.time = np.median(times)
        return 0
    
    def get_jet_with_longer_box(self):
        '''
        Among the boxes of the jets composing the cluster, return the box with the biggest height
        '''
        heights = np.array([jet.box.height for jet in self.jets])
        result = self.jets[np.argmax(heights)]
        return result
    
    ## Another option to consider is to calculate the average box in the same way the average box has been calculated during aggregation, for one subject?


    def create_gif(self, output):
        '''
            Create a gif of the jet objects showing the
            image and the plots from the `Jet.plot()` method
        Inputs
        ------
            output: str
                name of the exported gif
        '''
        fig, ax = plt.subplots(1, 1, dpi=150)

        # create a temp plot so that we can get a size estimate
        subject0 = self.jets[0].subject

        im1 = ax.imshow(get_subject_image(subject0, 0))
        ax.axis('off')
        fig.tight_layout(pad=0)

        # loop through the frames and plot
        ims = []
        for jet in tqdm.tqdm(self.jets):
            subject = jet.subject
            for i in range(15):
                img = get_subject_image(subject, i)

                # first, plot the image
                im1 = ax.imshow(img)

                # for each jet, plot all the details
                # and add each plot artist to the list
                jetims = jet.plot(ax, plot_sigma=False)

                # combine all the plot artists together
                ims.append([im1, *jetims])

        # save the animation as a gif
        ani = animation.ArtistAnimation(fig, ims)
        ani.save(output, writer='ffmpeg')
        plt.close('all')
