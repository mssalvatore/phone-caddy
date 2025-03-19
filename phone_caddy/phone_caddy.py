import argparse
from copy import deepcopy
from pathlib import Path
from typing import Final

from build123d import *  # noqa: F403
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
PHONE_Y: Final[float] = 9.75
PHONE_Z: Final[float] = 115


HOOK_Z: Final[float] = 30
HOOK_THICKNESS: Final[float] = 2.5

HEADBOARD_THICKNESS: Final[float] = 40.75
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
    hook_fillet = 1.25

    l1 = Line((0, HOOK_Z + HOOK_THICKNESS), (0, 0))
    l2 = Line(l1 @ 1, (-(HEADBOARD_THICKNESS + HOOK_THICKNESS), 0))
    l3 = Line(l2 @ 1, (-(HEADBOARD_THICKNESS + HOOK_THICKNESS), HOOK_THICKNESS + hook_fillet))
    l4 = RadiusArc(
        l3 @ 1,
        (-(HEADBOARD_THICKNESS + HOOK_THICKNESS - hook_fillet), HOOK_THICKNESS),
        -hook_fillet,
    )
    l5 = Line(l4 @ 1, (-(HEADBOARD_THICKNESS + HOOK_THICKNESS), HOOK_THICKNESS))
    l6 = Line(l5 @ 1, (-HOOK_THICKNESS, HOOK_THICKNESS))
    l7 = Line(l6 @ 1, (-HOOK_THICKNESS, HOOK_Z + HOOK_THICKNESS))
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


def export_model_to_stl(model: Part):
    src_file_path = Path(__file__)
    renders_dir = src_file_path.parent.parent / "renders"

    if not renders_dir.exists():
        renders_dir.mkdir()
    elif not renders_dir.is_dir():
        raise RuntimeError(f"{renders_dir} is not a directory.")

    stl_file_name = src_file_path.stem + ".stl"

    export_stl(model, renders_dir / stl_file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A phone caddy that hooks over a headboard.")
    parser.add_argument("--stl", action="store_true", help="Export STL")
    args = parser.parse_args()

    model = phone_caddy()

    if args.stl:
        export_model_to_stl(Part() + model)
    else:
        show_all()
