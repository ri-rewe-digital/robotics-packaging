import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from bin import Container
from geometry import Cuboid, Point

box_color = 'blue'
product_color = 'red'
space_color = 'yellow'


def plot(container):
    g = plt.axes(projection='3d')
    draw_cube(g, container.specification, box_color)
    g.set_xlabel('X')
    g.set_ylabel('Y')
    g.set_zlabel('Z')
    g.set_xlim3d(0, container.specification.dimensions[0] + 10)
    g.set_ylim3d(0, container.specification.dimensions[1] + 10)
    g.set_zlim3d(0, container.specification.dimensions[2] + 10)

    plt.show()


def create_vertices_from_points(o0, u0):
    o1 = np.array((o0[0], u0[1], o0[2]))
    o2 = np.array((o0[0], u0[1], u0[2]))
    o3 = np.array((o0[0], o0[1], u0[2]))
    u1 = np.array((u0[0], u0[1], o0[2]))
    u2 = np.array((u0[0], o0[1], o0[2]))
    u3 = np.array((u0[0], o0[1], u0[2]))
    return [
        [o0, o1, o2, o3],  # left
        [o0, u2, u1, o1],  # bottom
        [o1, u1, u0, o2],  # back
        [u0, o2, o3, u3],  # top
        [o0, u2, u3, o3],  # front
        [u0, u1, u2, u3]  # right
    ]


def create_vertices(cuboid):
    o = Point.new_origin().coords
    u = cuboid.dimensions.coords
    return create_vertices_from_points(o, u)


def draw_cube(g, cuboid, col):
    verts = create_vertices(cuboid)
    g.add_collection3d(Poly3DCollection(verts, facecolors=col, linewidths=0.2, edgecolors='r', alpha=.10))


if __name__ == '__main__':
    spec = Cuboid(Point.from_scalars(30, 30, 30))
    container = Container(spec)
    plot(container)
