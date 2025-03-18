from copy import deepcopy
from typing import Final

from build123d import *
from ocp_vscode import (  # noqa: F401
    get_defaults,
    reset_show,
    set_defaults,
    set_port,
    show,
    show_all,
    show_object,
)

set_port(3939)

PHONE_X: Final[float] = 75
PHONE_Y: Final[float] = 8
PHONE_Z: Final[float] = 115

HEADBOARD_THICKNESS: Final[float] = 30
WALL_THICKNESS: Final[float] = 2
OPPOSING_WALLS: Final[float] = 2 * WALL_THICKNESS
FILLET: Final[float] = 2


def phone_caddy():
    _hook = hook()
    _phone_caddy = Part() + _hook

    plane = deepcopy(Plane.XZ)
    plane.origin = _hook.faces().sort_by(Axis.Z)[0].edges().sort_by(Axis.Y)[0] @ 0.5

    return _phone_caddy + body(plane, (Align.CENTER, Align.MIN))


def hook():
    hook_z = 10
    hook_thickness = 2
    hook_fillet = 1.25

    l1 = Line((0, hook_z + hook_thickness), (0, 0))
    l2 = Line(l1 @ 1, (-HEADBOARD_THICKNESS, 0))
    l3 = Line(l2 @ 1, (-HEADBOARD_THICKNESS, hook_thickness + hook_fillet))
    l4 = RadiusArc(l3 @ 1, (-HEADBOARD_THICKNESS + hook_fillet, hook_thickness), -hook_fillet)
    l5 = Line(l4 @ 1, (-HEADBOARD_THICKNESS, hook_thickness))
    l6 = Line(l5 @ 1, (-hook_thickness, hook_thickness))
    l7 = Line(l6 @ 1, (-hook_thickness, hook_z + hook_thickness))
    l8 = Line(l7 @ 1, l1 @ 0)

    hook_2d = make_face([l1, l2, l3, l4, l5, l6, l7, l8])
    hook_2d = fillet(hook_2d.vertices()[5], hook_fillet)

    return Plane.YZ * extrude(hook_2d, PHONE_X)


def body(plane: Plane, align: tuple[Align, Align]):
    plane_y_axis = Axis(plane.origin, plane.y_dir)

    body_2d = plane * Rectangle(PHONE_X + OPPOSING_WALLS, PHONE_Z + WALL_THICKNESS, align=align)
    body_2d = fillet(body_2d.vertices().sort_by(plane_y_axis)[2:], FILLET)

    body_3d = extrude(body_2d, amount=PHONE_Y + OPPOSING_WALLS)
    body_3d = fillet(
        body_3d.edges().filter_by(plane_y_axis),
        FILLET,
    )

    body_3d -= phone_cutout(body_3d.faces().sort_by(Axis.Z).first)
    body_3d -= port_cutout(body_3d.faces().sort_by(Axis.Z)[-1])

    return body_3d


def port_cutout(face: Face):
    plane = Plane(origin=face.center())

    return extrude(
        plane * RectangleRounded(PHONE_X - 24, PHONE_Y, radius=1.5),
        amount=-2 * WALL_THICKNESS,
    )


def phone_cutout(face: Face):
    plane = Plane(origin=face.center())

    plane_x_axis = Axis(plane.origin, plane.x_dir)
    plane_y_axis = Axis(plane.origin, plane.y_dir)
    plane_z_axis = Axis(plane.origin, plane.z_dir)

    phone_cutout_2d = Rectangle(PHONE_X, PHONE_Y)
    phone_cutout_2d = fillet(phone_cutout_2d.vertices().group_by(plane_y_axis)[-1], radius=4)
    phone_cutout_2d = fillet(phone_cutout_2d.vertices().group_by(plane_y_axis)[0], radius=1)
    phone_cutout_3d = plane * extrude(phone_cutout_2d, amount=PHONE_Z)
    phone_cutout_3d = fillet(
        phone_cutout_3d.edges()
        .filter_by(plane_x_axis)
        .group_by(plane_z_axis)[-1]
        .sort_by(plane_y_axis)[-1],
        radius=1,
    )

    return phone_cutout_3d


def main():
    _phone_caddy = phone_caddy()
    # h = hook()
    show_all()


if __name__ == "__main__":
    main()
