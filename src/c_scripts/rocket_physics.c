#include <math.h>
#include <stdio.h>

#define M_PI 3.14159265358979323846


void update_acceleration(double mass, double main_thrust, double drag_coeff, double gravity, double angle, double h_v, double v_v, double *h_a, double *v_a) {
    // convert angles to radians
    double radians = angle * (M_PI/180.0);

    // split thrust
    double thrust_x = main_thrust * cos(radians);
    double thrust_y = main_thrust * sin(radians);

    double drag_force_horizontally = drag_coeff * h_v * fabs(h_v);
    double drag_force_vertically = drag_coeff * v_v * fabs(v_v);

    // update horizontal acceleration
    *h_a = (thrust_x - drag_force_horizontally) / mass;
    *v_a = ((thrust_y - drag_force_vertically) / mass) - gravity;
}


void update_velocity(double h_a, double v_a, double dt, double initial_horizontal_vel, double initial_vertical_vel, double *h_v, double *v_v) {
    // convert angle to radians    
    *h_v += h_a * dt;
    *v_v += v_a * dt;
}


void calculate_torque(double lateral_thrust_force, double radius_thrust, double *torque) {
    *torque = lateral_thrust_force * radius_thrust;
}


void update_angular_acceleration(double torque, double inertia, double *angular_acceleration) {
    *angular_acceleration = torque / inertia;
}


void update_angular_velocity(double angular_acceleration, double time_thrust, double *angular_velocity) {
    *angular_velocity += angular_acceleration * time_thrust;
} 