from porovnani_spline import vykresli_trajektorii, vykresleni_porovnani, animate


#vykresli_trajektorii([1,1,1], 40, 10000, 10, 28, 8/3)

# run "winget install ffmpeg" before using the animation function
animate([1,1,1], .1, 10000, 10, 28, 8/3)

# nebo:
#vykresleni_porovnani([1,1,1], 40, 400, 10, 28, 8/3, s=1.0)