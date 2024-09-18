#include <math.h>
#include <stdio.h>

#define M_PI 3.14159265358979323846


int sign(double velocity) {
    if (velocity >= 0) {
        return 1;
    } else {
        return -1;
    }
}


void update_acceleration(
    double gravity,
    double drag_coeff,
    double air_density,
    double cross_sectional_area,
    double mass,
    double angle,
    double main_thrust_power,
    double h_v, 
    double v_v, 
    double *h_a, 
    double *v_a
    ) {

    double radians = angle * (M_PI/180.0);

    // split thrust
    double thrust_x = main_thrust_power * cos(radians);
    double thrust_y = main_thrust_power * sin(radians);

    double drag_force_h = 0.5 *  drag_coeff * air_density * cross_sectional_area * (h_v * h_v);
    double drag_force_y = 0.5 * drag_coeff * air_density * cross_sectional_area * (v_v * v_v);

    *h_a = (thrust_x - (drag_force_h * sign(h_v))) / mass;
    *v_a = ((thrust_y - drag_force_y) / mass) - gravity;
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


void calculate_inertia(double width, double height, double mass, double *inertia) {
    *inertia = 0.83 * mass * ((width * width) + (height * height));
}