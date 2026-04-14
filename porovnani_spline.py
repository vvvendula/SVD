import matplotlib.pyplot as plt
from bspline import vyhlad_krivku
from simulace import simulace
import numpy as np
import matplotlib.animation as animation

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
    beta,):

    traj = simulace(pocatecni_stav, t_max, pocet_bodu, sigma, rho, beta)
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.plot(traj[:,0], traj[:,1], traj[:,2])
    ax.legend([f"t={t_max}"])
    ax.set_title("numericka")
    plt.show()

def animate(pocatecni_stav,
    t_max,
    pocet_bodu,
    sigma,
    rho,
    beta,
    retain_points=500,
    frame_count=500,
    fps=15):
    traj0 = np.empty((0, 3))  # Inicializace prázdného pole pro trajektorii

    def update(frame):
        nonlocal traj0
        nonlocal pocatecni_stav
        nonlocal frame_count
        traj = simulace(pocatecni_stav, t_max/frame_count*(frame+1), int(pocet_bodu/frame_count), sigma, rho, beta)
        traj0 = np.append(traj0[:-1], traj, axis=0)
        ax.cla()
        ax.plot(traj0[-retain_points:,0], traj0[-retain_points:,1], traj0[-retain_points:,2])
        ax.legend([f"t={t_max/frame_count*(frame+1):.2f}"])
        ax.set_title("numericka")
        ax.set(xlim=(-20, 20), ylim=(-30, 30), zlim=(0, 50))
        pocatecni_stav = traj[-1]

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ani = animation.FuncAnimation(fig=fig, func=update, frames=frame_count, interval=1000/fps, repeat=False)
    ani.save(filename="video.mp4", writer="ffmpeg", fps=fps)