# n_body_collision

Continuing from my previous post outlining my N-body gravity simulation project I have expanded my exploration into the use of Pygame for simulations and other visualisations of data.

In the below short video is a demonstration of 300 particles and the perfectly elastic collisions between them. All energy and momentum between the particles is entirely conserved and only passed along between collisions. Hence, total momentum and energy of the system is conserved also. This can be most easily demonstrated by assessing the velocities shortly after the primary collision. All particles started the simulation with identical speed towards the centre, shortly after many particles are moving at a slow pace and others significantly faster than their original velocity but maintaining an equal average velocity across the system.

To illustrate the dynamics at play, I've assigned distinct colours to each starting quadrant and collided them at the centre of the scene. Chaos quickly emerges from what was initially an ordered system.

Similarly to my initial post, this simulation was derived entirely using mathematics and without specialized libraries, for this project I have only used Pygame, NumPy and Itertools.

Moving forward, my immediate plans involve integrating the collision and gravitation logic into a unified "engine." This will enable us to explore interesting configurations and address any existing bugs in the current scripts. In addition to this, I plan on implementing a similar model using inelastic collisions and visualising the energy loss over time.
