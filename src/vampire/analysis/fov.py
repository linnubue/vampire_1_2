
def fov(H, theta, phi):
    import numpy as np
    """Calculates field of view of radiometer 
    input:
        H: height of antenna/radiometer in m
        theta: incidence angle in degrees
        phi: opening angle (full width) in degrees
    output: 
        a: minor axis
        b: major axis 
        area: area of ellipse
    """
    #distance origin to beam at incidence angle theta (CO)
    BO = np.tan(theta*np.pi/180)*H
     #distance origin to first vertex of the ellipse
    AO = np.tan((theta-phi/2)*np.pi/180)*H
     #distance origin to second vertex of the ellipse
    DO = np.tan((theta+phi/2)*np.pi/180)*H
    
        
   # print("BO ", BO, " AO:", AO, " DO: ", DO)
    b = (DO-AO)/2 #major axis, note that A and D do not have the same distance to C 
    CO = AO + b
    HC = (H**2 + CO**2)**0.5 #length of beam at incidence angle theta
    print("HC ", HC)
    a = HC * np.tan((phi/2)*np.pi/180) #minor axis
    area = np.pi * a * b #area of the ellipse
    if  theta+phi/2 > 90:   
        print("second vortex above horizon, distance origin to first vortex: ", AO, " as estimation of footprint center one might take BO: ", BO)
    return a, b, area, CO

