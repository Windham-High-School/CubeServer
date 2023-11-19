"""Handles the reference data
This is the data that is used to score team data"""

import statistics
from datetime import datetime
import logging
from typing import Mapping, List, Optional

from cubeserver_common.models.team import Team
from cubeserver_common.models.datapoint import DataClass, DataPoint
from cubeserver_common.models.utils.modelutils import PyMongoModel
from pymongo import DESCENDING
from bson import ObjectId


class ReferencePoint(PyMongoModel):
    """Holds a set of reference measurements from a point in time"""

    def __init__(
        self, temp: DataPoint, pressure: DataPoint, moment: Optional[datetime] = None
    ):
        if (
            temp.category != DataClass.TEMPERATURE
            or pressure.category != DataClass.PRESSURE
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
        return super().find_one({}, {"sort": {"control.max.timestamp": -1}})

    def of(self, data_type: DataClass) -> DataPoint:
        """Returns a reference datapoint with the specified dataclass
        if available"""
        if data_type == DataClass.TEMPERATURE:
            return self.temp
        elif data_type == DataClass.PRESSURE:
            return self.pressure
        else:
            raise ValueError(f"No reference of type {data_type}")


class Reference:
    """Manages the reference stations"""

    @classmethod
    def collect(cls, team: Team) -> ReferencePoint:
        """Collects a reference point and stores it to the database.
        This should be run periodically."""

        # temps = []
        # pressures = []
        # for reference_cube in Team.find_references():
        #    data =
        # temp_request = ref_protocol.ReferenceRequest(
        #     id = b'\x00',
        #     signal=ref_protocol.ReferenceSignal.ENQ,
        #     command=ref_protocol.ReferenceCommand.MEAS,
        #     param=ref_protocol.MeasurementType.TEMP.value
        # )
        # pres_request = ref_protocol.ReferenceRequest(
        #     id = b'\x00',
        #     signal=ref_protocol.ReferenceSignal.ENQ,
        #     command=ref_protocol.ReferenceCommand.MEAS,
        #     param=ref_protocol.MeasurementType.PRES.value
        # )
        # with DispatcherClient() as client:
        #     response_temp = client.request(temp_request)
        #     response_pres = client.request(pres_request)

        ref_pt = ReferencePoint(
            DataPoint(category=DataClass.TEMPERATURE, value=32),  # TODO: Use real data
            DataPoint(category=DataClass.PRESSURE, value=0),  # TODO: Use real data
        )
        ref_pt.save()
        return ref_pt

    @classmethod
    def trimmed_mean(cls, values: List[int | float]) -> float:
        """Calculates a trimmed mean (of sorts) of a set of values.
        The furthest from the median is trimmed, and the average of remaining values is returned.
        """
        median = statistics.median(values)
        return sum(values) - max(value - median for value in values) + median

    @classmethod
    def collect_avg(cls) -> ReferencePoint:
        """Collects the trimmed mean reference point as discussed earlier"""
        raise NotImplementedError("Not implemented yet")
        for station in Team.find_references():
            ref = cls.collect(station)
        # return ReferencePoint(
        #    cls.trimmed_mean(),
        #    cls.trimmed_mean()
        # )

    # @classmethod
    # def get_window_point(cls, window: int) -> ReferencePoint:
    #     """Returns the most recent reference point in the db if it falls within the time window of now in seconds"""
    #     logging.debug("Getting a reference point within " + str(window) + " seconds...")
    #     #most_recent = ReferencePoint.find_most_recent()
    #     #logging.debug(most_recent)
    #     #elapsed = datetime.now() - most_recent.moment
    #     #if elapsed.total_seconds() <= window:
    #     #    return most_recent
    #     return cls.collect(Team.find_references()[0])  # If it's too old, grab a new point
