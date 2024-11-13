import numpy as np

rocket = {
    "payload": {
        "mass": 200,
        "height": 180
    },
    "fuel tank": {
        "mass": 500,
        "height": 100
    },
    "engine": {
        "mass": 300,
        "height": 20
    }
}


def calculate_cp():
    body_height = 30
    body_diameter = 2

    fins_number = 4
    fins_base_rect = 1
    fins_height_rect = 3

    body_reference_area = np.pi*(body_diameter/2)**2
    body_normal_fc = 1.1
    body_distance_from_cg = body_height/2

    fins_reference_area = fins_number * ((fins_base_rect * fins_height_rect)/2)
    fins_normal_fc = 2.0
    fins_distance_from_cg = 28

    body_contribution = body_reference_area * body_normal_fc * body_distance_from_cg
    fins_contribution = fins_reference_area * fins_normal_fc * fins_distance_from_cg

    total_moment = body_contribution + fins_contribution
    total_effective_aerodynamic_force = (body_reference_area*body_normal_fc) + (fins_reference_area*fins_normal_fc)

    cp = total_moment/total_effective_aerodynamic_force

    return cp 

def calculate_cg():
    # find total mass rocket
    total_mass_rocket = 0
    for component in rocket.keys():
        total_mass_rocket += rocket[component]["mass"]

    calculation_each_component = 0
    for component in rocket.keys():
        calculation_each_component += rocket[component]["mass"] * (rocket[component]["height"]/2)

    cg_position = calculation_each_component / total_mass_rocket

    return cg_position

cg = calculate_cg()
cp = calculate_cp()

length_rocket = 0
for component in rocket.keys(): length_rocket += rocket[component]["height"]
print(f"Rocket length: {length_rocket}m, location CP: {cp}m, location CG: {cg}")
