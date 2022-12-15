"""Handles the reference data
This is the data that is used to score team data"""

from datetime import datetime
from typing import Mapping, List, Optional

from cubeserver_common.models.datapoint import DataClass, DataPoint
from cubeserver_common.models.utils.modelutils import PyMongoModel


class ReferencePoint(PyMongoModel):
    """Holds a set of reference measurements from a point in time"""

    def __init__(
        self,
        temp: DataPoint,
        pressure: DataPoint,
        moment: Optional[datetime] = None
    ):
        if (
            temp.category != DataClass.TEMPERATURE or \
            pressure.category != DataClass.PRESSURE
        ):
            raise ValueError("Params MUST be of their respective DataClasses")
        super().__init__()

        self.temp = temp
        self.pressure = pressure

        self.temp.is_reference = True
        self.pressure.is_reference = True

        self.moment = moment
        if self.moment is None:
            self.moment = datetime.now()

    def __str__(self) -> str:
        return (
            self.moment.__str__() + " - \n"
            "Temperature: \t" + self.temp.__str__() + "\n"
            "Pressure: \t" + self.pressure.__str__() + "\n"
        )
    
    def find_most_recent(self) -> PyMongoModel:
        """Returns the most recent db entry"""
        return super().find_one(
            {},
            {
                'sort': { 'control.max.timestamp': -1 }
            }
        )

    def of(self, data_type: DataClass) -> DataPoint:
        """Returns a reference datapoint with the specified dataclass
        if available"""
        if data_type == DataClass.TEMPERATURE:
            return self.temp
        elif data_type == DataClass.PRESSURE:
            return self.pressure
        else:
            raise ValueError(f"No reference of type {data_type}")
        

class ReferenceStation:
    """Manages the reference station"""

    @classmethod
    def collect(cls) -> ReferencePoint:
        """Collects a reference point and stores it to the database.
        This should be run periodically."""
        ref_pt = ReferencePoint(
            DataPoint(
                category=DataClass.TEMPERATURE,
                value=32.0  # TODO: Collect actual data!
            ),
            DataPoint(
                category=DataClass.PRESSURE,
                value=30.00
            )
        )
        ref_pt.save()
        return ref_pt

    @classmethod
    def get_window_point(cls, window: int) -> ReferencePoint:
        """Returns the most recent reference point in the db if it falls within the time window of now in seconds"""
        print("Getting a reference point within " + str(window) + " seconds...")
        most_recent = ReferencePoint.find_most_recent()
        print(most_recent)
        elapsed = datetime.now() - most_recent.moment
        if elapsed.total_seconds() <= window:
            return most_recent
        return cls.collect()  # If it's too old, grab a new point

