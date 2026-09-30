# Tools for script generating

def build_ground_station_block(name: str, params: dict) -> str:

    # Generates the "Create GroundStation" for a single GS
    return (
        f"Create GroundStation {name};\n"
        f"{name}.CentralBody = Earth;\n"
        f"{name}.StateType = Spherical;\n"
        f"{name}.HorizonReference = Ellipsoid;\n"
        f"{name}.Location1 = {params['lat']};\n"
        f"{name}.Location2 = {params['lon']};\n"
        f"{name}.Location3 = {params['alt']};\n"
        f"{name}.MinimumElevationAngle = {params['min_elevation']};\n"
    )

def build_all_ground_stations(ground_stations: dict) -> tuple[str, str]:

    # Generates the sequence of GS and the list that is required for the ContactLocator
    
    blocks = [build_ground_station_block(name, p) for name, p in ground_stations.items()]
    definitions = "\n".join(blocks)
    observers_list = "{" + ", ".join(ground_stations.keys()) + "}"
    return definitions, observers_list