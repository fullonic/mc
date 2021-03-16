"""Database schema overview.

Defines some of the application models(all BaseModel subclasses), their possible
relationships and some necessary method.
Eventually will grow up while developing and implementing all the features currently
defined here.

NOTE: This document should be see as a database layout of what is foreseen necessary
to be implemented.
"""

import datetime
from typing import Hashable, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, EmailStr, FilePath

from django.contrib.gis.geos import LineString, Point, Polygon


class User(BaseModel):
    id: int
    email: EmailStr
    password: Hashable
    hunter: bool


class Region(BaseModel):
    name: str
    geom: Polygon


class Address(BaseModel):
    street: str
    city: str
    region: Region
    country: str = "Catalunya"
    postalcode: int
    geom: Point


class Club(BaseModel):
    """Hunting club or Association."""

    created_by: User  # Must be a hunter
    name: str
    region: Region
    location: Address
    phone: int
    email: EmailStr
    website: AnyHttpUrl


class HunterProfile(BaseModel):
    user: User
    name: str
    license_id: str
    confirmed: bool
    club: Club
    region: Region

    def confirm_profile(self):
        list_ids = []
        if self.license_id in list_ids:
            return True
        return False


class HuntingLand(BaseModel):
    """Catalonia permitted hunting land areas."""

    plate_id: str
    region: Region
    managed_by: Optional[Club]
    geom: Polygon


class HuntingZone(BaseModel):
    """Area of hunting activity during a specific period of time."""

    submitted_by: User  # Must be a hunter user or a club
    date: datetime.datetime
    duration: int  # In hours
    visible: bool = True
    geom: Polygon

    @property
    def ends_on(self):
        return self.date + datetime.timedelta(hours=self.duration)

    def hide_geometry(self):
        """Change hunting zone geometry visibility.

        If the hunting event is already expired, we turn off the visibility which will
        remove it from the hunting zone map.
        """
        if self.ends_on > datetime.datetime.now():
            self.visible = False


class GPXTrack(BaseModel):
    user: User
    track: FilePath
    geom: LineString


class GeomType:
    line: str
    polygon: str


class Alert(BaseModel):
    """Alert system to notify public in general.

    If a person is planning a new outdoor activity and wants to be notified in case of a new
    hunting event in a particular area.
    User can submit the interested zone by:
        1. Draw a the area of interest (AOI) which will be treated as a polygon
        2. Submit the route (.gpx file) which will be treated as a LineString
    Once a new hunting zone is submitted, we will check if there is any entry on the alert
    system that meets one of the follow possibilities:
    1. The user routes is inside or intersects with the new created hunting area
    2. The AIO is inside or intersects
    3. Finally, even the previous scenarios are false, we check if the user security buffer
    will be respected all the time
    """

    user: User  # A regular user
    track: Optional[GPXTrack]
    date: datetime.datetime
    # TODO: Search for a default security value
    security_buffer: int  # Meters
    geom_type: GeomType  # Helper flag to provide
    geom: Union[Polygon, LineString]

    def is_activity_secure(self, hunting_zone: HuntingZone) -> bool:
        """
        Proxy to do all geographic operations checks to ensure that user activity doesn't
        overlap with a hunting activity."""

        ...

    def notify_user(self, hunting_zone: HuntingZone):
        if not self.is_activity_secure(hunting_zone):
            # alert user about the occurrence of a hunting activity
            return
        # alert user about the absence of a hunting activity
        return
