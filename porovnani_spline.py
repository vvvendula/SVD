import matplotlib as plt
from bspline import vyhlad_krivku
from simulace import simulce


def vykresleni_porovnani( pocatecni_stav, t_max, pocet_bodu, sigma, rho, beta, s=1):
    #1.numericky trajektorie
    traj=simulace(pocatecni_stav, t_max, pocet_bodu, sigma, rho, beta)

    #spline
    traj_spline=vyhlad_krivku(traj, s=s, pocet_novych_bodu=5000)

    #graf
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    # 4. původní trajektorie
    ax.plot(
        traj[:, 0], traj[:, 1], traj[:, 2],
        label="numericka trajektorie",
        linewidth=1,
        alpha=0.5
    )

    # 5. spline
    ax.plot(
        traj_spline[:, 0], traj_spline[:, 1], traj_spline[:, 2],
        label="B-spline",
        linewidth=1
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()

    plt.show()

def vykresli_trajektorii(pocatecni_stav,
    t_max,
    pocet_bodu,
    sigma,
    rho,
    beta):

    traj = simulace(pocatecni_stav, t_max, pocet_bodu, sigma, rho, beta)

    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.plot(traj[:,0], traj[:,1], traj[:,2])

    ax.set_title("numericka")
    plt.show()


