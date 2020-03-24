import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from bin import Container
from geometry import Cuboid, Point, Space

box_color = 'blue'
product_color = 'red'
empty_color = 'yellow'


def create_graphics():
    g = plt.axes(projection='3d')
    g.set_xlabel('X')
    g.set_ylabel('Y')
    g.set_zlabel('Z')
    return g


def scale_axis_for_container(g, container_bin):
    g.set_xlim3d(0, container_bin.specification.dimensions[0] + 10)
    g.set_ylim3d(0, container_bin.specification.dimensions[1] + 10)
    g.set_zlim3d(0, container_bin.specification.dimensions[2] + 10)


def plot_container(container_bin):
    g = create_graphics()
    draw_container(g, container_bin)
    scale_axis_for_container(g, container_bin)
    return g


def draw_container(g, container_bin):
    draw_cube(g, container_bin.specification, box_color)


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


def draw_space(g, space, col):
    verts = create_vertices_from_points(space.bottom_left.coords, space.upper_right.coords)
    g.add_collection3d(Poly3DCollection(verts, facecolors=col, linewidths=0.2, edgecolors='r', alpha=.10))


def draw_placement(g, product_placement, color):
    draw_space(g, product_placement.space, color)


def plot_placements(container_bin, placements, plot_spaces=False):
    g = plot_container(container_bin)
    for i, product_placement in enumerate(placements):
        if product_placement:
            draw_placement(g, product_placement, ((float(i+1)/len(placements)),0,0,0))
    if plot_spaces:
        for empty_space in container_bin.empty_space_list:
            if empty_space:
                draw_space(g, empty_space, empty_color)
    plt.show()


if __name__ == '__main__':
    spec = Cuboid(Point.from_scalars(30, 30, 30))
    container_ = Container(spec)
    g = plot_container(container_)
    b = Point(np.array([5, 5, 5]))
    d = Point(np.array([3, 2, 3]))
    s = Space(d, b)
    draw_space(g, s, product_color)
    plt.show()
