

def distance(lat1, lon1, lat2, lon2):
    """
    used orthodrome for distance calculation
    NOTE: accurracy is enough for a most applications
            using satellite data

    input:
        lat1, lon1, lat2, lon2 - array with coordinates
            of the same size, might be multi dimensional
    output:
        dist - array of distances of size of the input array
    """
    from numpy import sin, cos, arccos, radians, float64
    lon1=radians(lon1).astype(float64)
    lon2=radians(lon2).astype(float64)
    lat1=radians(lat1).astype(float64)
    lat2=radians(lat2).astype(float64)
    earthrad=6371.

    return arccos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*earthrad

