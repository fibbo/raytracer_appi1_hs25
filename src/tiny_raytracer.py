import math
import sys

from light import Light
from material import Material
from scene import Scene
from sphere import Sphere
from vector import Vector

float_max = sys.float_info.max


def ray_sphere_intersect(origin, direction, sphere):
    origin_to_center = sphere.center - origin
    projection_distance = origin_to_center.dot(direction)
    perpendicular_dist_squared = (
        origin_to_center.dot(origin_to_center)
        - projection_distance * projection_distance
    )
    if perpendicular_dist_squared > sphere.radius * sphere.radius:
        return (False, 0)
    half_chord = math.sqrt(sphere.radius * sphere.radius - perpendicular_dist_squared)
    near_intersection = projection_distance - half_chord
    far_intersection = projection_distance + half_chord
    if near_intersection < 1e-3:
        near_intersection = far_intersection
    if near_intersection < 1e-3:
        return (False, 0)

    return (True, near_intersection)


def reflect(incoming, normal):
    return incoming - normal * 2.0 * (incoming.dot(normal))


def refract(incoming, normal, eta_transmitted, eta_incident=1.0):
    cos_incident = -max(-1.0, min(1.0, incoming.dot(normal)))
    if cos_incident < 0:
        return refract(incoming, -normal, eta_incident, eta_transmitted)
    eta_ratio = eta_incident / eta_transmitted
    discriminant = 1 - eta_ratio * eta_ratio * (1 - cos_incident * cos_incident)
    if discriminant < 0:
        return Vector(1, 0, 0)
    else:
        return incoming * eta_ratio + normal * (
            eta_ratio * cos_incident - math.sqrt(discriminant)
        )


def scene_intersect(origin, direction, spheres):
    spheres_dist = float_max
    hit = None
    normal = None
    material = None
    for sphere in spheres:
        intersection_result = ray_sphere_intersect(origin, direction, sphere)
        if intersection_result[0] and intersection_result[1] < spheres_dist:
            spheres_dist = intersection_result[1]
            hit = origin + direction * spheres_dist
            normal = (hit - sphere.center).normalize()
            material = sphere.material

    checkerboard_dist = float_max
    if abs(direction.y) > 1e-3:
        floor_distance = -(origin.y + 4) / direction.y
        intersection_point = origin + direction * floor_distance
        if (
            floor_distance > 1e-3
            and abs(intersection_point.x) < 10
            and intersection_point.z < -10
            and intersection_point.z > -30
            and floor_distance < spheres_dist
        ):
            checkerboard_dist = floor_distance
            hit = intersection_point
            normal = Vector(0, 1, 0)
            diffuse_color = (
                Vector(0.3, 0.3, 0.3)
                if (int(0.5 * hit.x + 1000) + int(0.5 * hit.z)) & 1
                else Vector(0.3, 0.2, 0.1)
            )
            material = Material("checkerboard", 1, Vector(1, 0, 0, 0), diffuse_color, 0)

    return (min(spheres_dist, checkerboard_dist) < 1000, hit, normal, material)


def cast_ray(origin, direction, spheres, lights, depth=0):
    if depth > 4:
        return Vector(0.2, 0.7, 0.8)
    has_hit, hit_point, normal, material = scene_intersect(origin, direction, spheres)
    if not has_hit:
        return Vector(0.2, 0.7, 0.8)

    reflect_direction = reflect(direction, normal).normalize()
    refract_direction = refract(
        direction, normal, material.refractive_index
    ).normalize()
    reflect_color = cast_ray(hit_point, reflect_direction, spheres, lights, depth + 1)
    refract_color = cast_ray(hit_point, refract_direction, spheres, lights, depth + 1)

    diffuse_light_intensity = 0
    specular_light_intensity = 0
    for light in lights:
        light_direction = (light.position - hit_point).normalize()

        has_shadow_hit, shadow_point, _, _ = scene_intersect(
            hit_point, light_direction, spheres
        )
        if (
            has_shadow_hit
            and (shadow_point - hit_point).norm() < (light.position - hit_point).norm()
        ):
            continue

        diffuse_light_intensity += light.intensity * max(
            0.0, light_direction.dot(normal)
        )
        specular_light_intensity += (
            math.pow(
                max(0.0, -reflect(-light_direction, normal).dot(direction)),
                material.specular_exponent,
            )
            * light.intensity
        )
    return (
        material.diffuse_color * diffuse_light_intensity * material.albedo[0]
        + Vector(1.0, 1.0, 1.0) * specular_light_intensity * material.albedo[1]
        + reflect_color * material.albedo[2]
        + refract_color * material.albedo[3]
    )


def render(scene):
    width = 400
    height = 200
    field_of_view = math.pi / 3.0
    framebuffer = width * height * [None]
    for pixel_y in range(height):
        for pixel_x in range(width):
            ray_dir_x = (pixel_x + 0.5) - width / 2.0
            ray_dir_y = -(pixel_y + 0.5) + height / 2.0
            ray_dir_z = -height / (2.0 * math.tan(field_of_view / 2.0))
            framebuffer[pixel_x + pixel_y * width] = cast_ray(
                Vector(0, 0, 0),
                Vector(ray_dir_x, ray_dir_y, ray_dir_z).normalize(),
                scene["spheres"],
                scene["lights"],
            )

    with open("out.ppm", "wb") as f:
        f.write(bytearray(f"P6 {width} {height} 255\n", "ascii"))
        counter = 0
        for pixel_color in framebuffer:
            counter += 1
            max_component = max(pixel_color[0], max(pixel_color[1], pixel_color[2]))
            if max_component > 1:
                pixel_color = pixel_color * 1 / max_component
            pixel_bytes = bytes(
                [
                    int(255 * pixel_color[0]),
                    int(255 * pixel_color[1]),
                    int(255 * pixel_color[2]),
                ]
            )
            f.write(pixel_bytes)


def read_scene(url):
    lights = []
    spheres = []
    materials = {}

    # TODO: Get text from url and parse the scene

    return Scene(lights=lights, spheres=spheres)


def write_scene_to_file(scene, file_name):
    with open(file_name, "w") as f:
        scene_string = scene.to_json()
        f.write(scene_string)


def load_scene_from_file(file_name):
    scene = Scene()
    with open(file_name, "r") as f:
        for line in f:
            scene.from_json(line)
            return scene


def main():
    ivory = Material(
        "ivory", 1.0, Vector(0.6, 0.3, 0.1, 0.0), Vector(0.4, 0.4, 0.3), 50
    )
    glass = Material(
        "glass", 1.5, Vector(0.0, 0.5, 0.1, 0.8), Vector(0.6, 0.7, 0.8), 125
    )
    red_rubber = Material(
        "red_rubber", 1.0, Vector(0.9, 0.1, 0.0, 0.0), Vector(0.3, 0.1, 0.1), 10
    )
    mirror = Material(
        "mirror", 1.0, Vector(0.0, 10.0, 0.8, 0.0), Vector(1.0, 1.0, 1.0), 1425
    )

    spheres = [
        Sphere(Vector(-3, 0, -16), 2, ivory),
        Sphere(Vector(-1.0, -1.5, -12), 2, glass),
        Sphere(Vector(1.5, -0.5, -18), 3, red_rubber),
        Sphere(
            Vector(
                7,
                5,
                -18,
            ),
            4,
            mirror,
        ),
    ]

    lights = [
        Light(Vector(-20, 20, 20), 1.5),
        Light(Vector(30, 50, -25), 1.8),
        Light(Vector(30, 20, 30), 1.7),
    ]
    scene = Scene(lights=lights, spheres=spheres)
    print(scene)
    render(scene)


if __name__ == "__main__":
    main()
