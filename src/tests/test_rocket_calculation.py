import unittest
from unittest.mock import patch

import os 
import pygame
import math
os.environ["SDL_VIDEODRIVER"] = "dummy"

from ..helpers.rocket import RocketCalculation

class TestRocket(unittest.TestCase):
    @classmethod
    def setupClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self) -> None:
        rocket_settings = {
            1: {
                "dry mass": {"value": 5000, "rect": ..., "type": "kg"},
                "propellant mass": {"value": 5000, "rect": ..., "type": "kg"},
                "cd": {"value": 0.5, "rect": ..., "type": ""}
            }
        }
        environment_settings = {
            "gravity": {"value": 9.81, "rect": ..., "type": 'm/s'},
            "air density": {"value": 1.221, "rect": ..., "type": 'p'},
            "wind velocity": {"value": 0, "rect": ..., "type": 'm/s'}
        }
        engine_settings = {
            1: {
                "engine identifier": {"value": "Default", "rect": ..., "type": ""},
                "thrust power": {"value": 30000, "rect": ..., "type": "N"},
                "ISP": {"value": 300, "rect": ..., "type": "s"},
                "thrust vector angle": {"value": 15, "rect": ..., "type": "°"},
                "number engines": {"value": 1, "rect": ..., "type": ""}
            }
        }
        mission_settings = {
            "apogee": {"value": 0, "rect": ..., "type": "m"},
            "target": {"value": "Test", "rect": ..., "type": ""},
            "launch planet": {"value": "Earth", "rect": ..., "type": ""},
            "initial flight angle": {"value": 0, "rect": ..., "type": "°"},
            "launch altitude": {"value": 0, "rect": ..., "type": "m"}
        }

        self.size_object = (10, 80)
        self.rocket = RocketCalculation(
            rocket_settings, engine_settings, environment_settings, mission_settings, (0, 0), self.size_object
        )


    def test_center_of_mass(self) -> None:
        center_of_mass = self.rocket.get_center_of_mass
        self.assertEqual(center_of_mass, pygame.Vector2(5, 40))

    def test_relative_velocity(self) -> None:
        self.rocket.velocity = pygame.Vector2(100, 0)
        wind_speed = 60
        wind_angle = 45
        self.rocket.wind_velocity = pygame.Vector2(
            wind_speed * math.sin(math.radians(wind_angle)),
            wind_speed * math.cos(math.radians(wind_angle))
        )
        relative_velocity = self.rocket.get_relative_velocity
        self.assertAlmostEqual(relative_velocity.x, 57.57, places=2)
        self.assertAlmostEqual(relative_velocity.y, -42.42, places=1)

    def test_lever_arm(self):
        self.rocket.size = pygame.Vector2(20, 100)
        position_force_applied = pygame.Vector2(self.rocket.size.x/2, self.rocket.size.y)        
        distance = self.rocket.calculate_lever_arm(position_force_applied)
        self.assertEqual(distance, pygame.Vector2(0, 50))

    def test_torque_generated_from_thrust(self) -> None:
        self.rocket.size = pygame.Vector2(20, 100)
        self.rocket.current_thrust_power = 30000
        self.rocket.gimbal_angle = 0
        self.torque_0_angle = self.rocket.get_torque_from_thrust
        self.rocket.gimbal_angle = 5
        self.torque_5_angle = self.rocket.get_torque_from_thrust

        self.assertEqual(self.torque_0_angle, 0)
        self.assertAlmostEqual(self.torque_5_angle, 130733.6, places=1)

    def test_lever_arm_horizontal_wind(self) -> None:
        self.rocket.size = pygame.Vector2(20, 100)
        self.rocket.wind_angle = 45
        self.rocket.rocket_angle = 0
        self.assertAlmostEqual(self.rocket.get_lever_arm_horizontal_wind, 35.36, places=1)

    def test_lever_arm_vertical_wind(self):
        self.rocket.size = pygame.Vector2(20, 100)
        self.rocket.wind_angle = 45
        self.rocket.rocket_angle = 0
        self.assertAlmostEqual(self.rocket.get_lever_arm_vertical_wind, 7.07, places=1)

    def test_torque_generated_by_wind(self) -> None:
        self.rocket.size = pygame.Vector2(20, 100)
        self.rocket.rocket_angle = 0
        self.rocket.wind_angle = 45
        self.rocket.velocity = (0, 50)
        self.rocket.drag_coeff = 0.5

        self.rocket.wind_velocity = pygame.Vector2(
            0 * math.sin(math.radians(self.rocket.wind_angle)),
            0 * math.cos(math.radians(self.rocket.wind_angle))
        )
        self.assertEqual(self.rocket.get_torque_from_wind, 0)

        self.rocket.wind_velocity = pygame.Vector2(
            10 * math.sin(math.radians(self.rocket.wind_angle)),
            10 * math.cos(math.radians(self.rocket.wind_angle))
        )
        # torque 1 = 433,037.5
        # torque 2 = 2,165,514.51
        self.assertAlmostEqual(self.rocket.get_torque_from_wind, 2,598,552.01, places=1)



if __name__ == "__main__":
    unittest.main()


# center of mass
# center of pressure
# tests
# parameters functions
# stand rocket