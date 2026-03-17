def lorenz(t,stav, sigma, rho, beta):
    x,y,z=stav

#dx dy dz

    dx=sigma*(y-x)
    dy=x*(rho-z)-y 
    dz=x*y-beta*z


    return [dx, dy,dz]
