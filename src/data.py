from .models.waypoint import Waypoint
from .models.vehicle import Vehicle

_waypoints = [
    Waypoint(
        id="OFFICE",
        name="Office",
        latitude=8.5241,
        longitude=76.9366,
        demand=0,
    ),

    Waypoint(
        id="WP001",
        name="Waypoint 1",
        latitude=8.5588,
        longitude=76.8812,
    ),

    Waypoint(
        id="WP002",
        name="Waypoint 2",
        latitude=8.5104,
        longitude=76.8987,
    ),

    Waypoint(
        id="WP003",
        name="Waypoint 3",
        latitude=8.6050,
        longitude=76.9500,
    ),

    Waypoint(
        id="WP004",
        name="Waypoint 4",
        latitude=8.5400,
        longitude=76.9100,
    ),

    Waypoint(
        id="WP005",
        name="Waypoint 5",
        latitude=8.5480,
        longitude=76.9200,
    ),

    Waypoint(
        id="WP006",
        name="Waypoint 6",
        latitude=8.5560,
        longitude=76.9300,
    ),

    Waypoint(
        id="WP007",
        name="Waypoint 7",
        latitude=8.5650,
        longitude=76.9400,
    ),

    Waypoint(
        id="WP008",
        name="Waypoint 8",
        latitude=8.5750,
        longitude=76.9500,
    ),

    Waypoint(
        id="WP009",
        name="Waypoint 9",
        latitude=8.5850,
        longitude=76.9600,
    ),

    Waypoint(
        id="WP010",
        name="Waypoint 10",
        latitude=8.4950,
        longitude=76.8850,
    ),

    Waypoint(
        id="WP011",
        name="Waypoint 11",
        latitude=8.5050,
        longitude=76.8950,
    ),

    Waypoint(
        id="WP012",
        name="Waypoint 12",
        latitude=8.5150,
        longitude=76.9050,
    ),

    Waypoint(
        id="WP013",
        name="Waypoint 13",
        latitude=8.5250,
        longitude=76.9150,
    ),

    Waypoint(
        id="WP014",
        name="Waypoint 14",
        latitude=8.5350,
        longitude=76.9250,
    ),
]

_vehicles = [
    Vehicle(
        id="VH001",
        number="KL01TS1001",
        operator="James",
        capacity=4,
    ),

    Vehicle(
        id="VH002",
        number="KL01TS2002",
        operator="Thomas",
        capacity=4,
    ),

    Vehicle(
        id="VH003",
        number="KL01TS3003",
        operator="Joseph",
        capacity=3,
    ),

    Vehicle(
        id="VH004",
        number="KL01TS4004",
        operator="David",
        capacity=3,
    ),
]

def get_waypoints():
    return _waypoints

def get_vehicles():
    return _vehicles

def get_depot():
    return 0
