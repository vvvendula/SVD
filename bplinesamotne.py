import numpy as np
import matplotlib.pyplot as plt


# LORENZŮV SYSTÉM 
def lorenz(x, y, z, sigma=10, beta=8/3, rho=28):
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return dx, dy, dz

def simulate_lorenz(pocatek, dt, steps, sigma=10, beta=8/3, rho=28):
    x, y, z = pocatek
    traj = [[x, y, z]]
    
    for _ in range(steps - 1):
        k1x, k1y, k1z = lorenz(x, y, z, sigma, beta, rho)
        k2x, k2y, k2z = lorenz(x + 0.5*dt*k1x, y + 0.5*dt*k1y, z + 0.5*dt*k1z, sigma, beta, rho)
        k3x, k3y, k3z = lorenz(x + 0.5*dt*k2x, y + 0.5*dt*k2y, z + 0.5*dt*k2z, sigma, beta, rho)
        k4x, k4y, k4z = lorenz(x + dt*k3x, y + dt*k3y, z + dt*k3z, sigma, beta, rho)
        
        x += (dt / 6.0) * (k1x + 2*k2x + 2*k3x + k4x)
        y += (dt / 6.0) * (k1y + 2*k2y + 2*k3y + k4y)
        z += (dt / 6.0) * (k1z + 2*k2z + 2*k3z + k4z)
        traj.append([x, y, z])
        
    return np.array(traj)


# bspline implementace(cox-de boor)
def cox_de_boor(i, k, t, knots): #bazopve funkce
    #nulty stupen...1 na intervalu (i,i+1), 0 jinde
    if k == 0:
        if t == knots[-1] and knots[i] <= t <= knots[i+1]:
            return 1.0
        if knots[i] <= t < knots[i+1]:
            return 1.0
        return 0.0
    
    jmenovatel1 = knots[i+k] - knots[i] #t_(i+k)-t_i
    term1 = 0.0
    if jmenovatel1 > 0: #(t-t_i)*(1/jmenovatel)*N_(i,k-1)
        term1 = ((t - knots[i]) / jmenovatel1) * cox_de_boor(i, k-1, t, knots)
        
    jmenovatel2 = knots[i+k+1] - knots[i+1] #t_(i+k+1)-t_(i+1)
    term2 = 0.0
    if jmenovatel2 > 0: #(t_(i+k+1)-t)*(1/jemonvatel2)*N_(i+1,k-1)
        term2 = ((knots[i+k+1] - t) / jmenovatel2) * cox_de_boor(i+1, k-1, t, knots)
        
    return term1 + term2

def vlastni_vyhlad_krivku(traj, k=3, pocet_novych_bodu=300):
    
    n = len(traj) - 1 #body ocislovane od 0 do n
    # uzlovy vektor tak, aby křivka začínala a končila přesně v krajních řídících bodech
    knots = np.concatenate(([0]*k, np.linspace(0, 1, n - k + 2), [1]*k))
    
    t_values = np.linspace(0, 1, pocet_novych_bodu)
    vysledna_krivka = np.zeros((pocet_novych_bodu, 3))
    
    for idx, t in enumerate(t_values):
        bod = np.zeros(3)
        for i in range(n + 1):
            #C(t)=sum(N_(i,k)*P_i)
            bod += cox_de_boor(i, k, t, knots) * traj[i]
        vysledna_krivka[idx] = bod
        
    return vysledna_krivka

# vykresleni
if __name__ == "__main__":
    
    pocatek = [10.0, 10.0, 27.0]

   
    dt = 0.08
    steps = 10

    
    surova_data = simulate_lorenz(pocatek, dt, steps)

    
    hladka_krivka = vlastni_vyhlad_krivku(surova_data, k=3, pocet_novych_bodu=300)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(projection='3d')

    # Vykreslení surových dat
    ax.plot(surova_data[:, 0], surova_data[:, 1], surova_data[:, 2], 
            color='red', linestyle='--', marker='o', markersize=6, 
            label='data z integrace')

    # Vykreslení B-spline křivky
    ax.plot(hladka_krivka[:, 0], hladka_krivka[:, 1], hladka_krivka[:, 2], 
            color='blue', linewidth=2, 
            label='vyhlazení b-spline')

    ax.set_title("numerická data vs. b-spline ", fontsize=14)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    
    
    ax.legend()
    plt.show()