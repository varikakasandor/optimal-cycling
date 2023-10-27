import random
import matplotlib.pyplot as plt

MAX_SPEED = 8
START_SPEED = MAX_SPEED
MAX_SPEED_CHANGE = 1
START_DIST_TO_LIGHT = 100
DIST_FROM_LIGHT_TO_GOAL = 100
START_MAX_TIME_TILL_GREEN = 30

DISQUALIFICATION_PENALTY = 1e20

NUM_SIMULATIONS = START_MAX_TIME_TILL_GREEN + 1
SAVE = True


def time_to_finish_green(dist_to_light, speed):
    time_till_max_speed = (MAX_SPEED - speed) / MAX_SPEED_CHANGE
    dist_to_max_speed = time_till_max_speed * (speed + MAX_SPEED) / 2
    time_from_max_speed = (DIST_FROM_LIGHT_TO_GOAL + dist_to_light - dist_to_max_speed) / MAX_SPEED
    total_time_to_finish = time_till_max_speed + time_from_max_speed
    return total_time_to_finish


def rec(dist_to_light, speed, max_time_till_green, dp_time, dp_action):
    if dist_to_light < 0:
        return DISQUALIFICATION_PENALTY
    if dp_time[dist_to_light][speed][max_time_till_green] is None:
        if dist_to_light == 0:
            if speed > 0:
                dp_time[dist_to_light][speed][max_time_till_green] = DISQUALIFICATION_PENALTY
            else:
                dp_time[dist_to_light][speed][max_time_till_green] = max_time_till_green / 2 + time_to_finish_green(0,
                                                                                                                    0)
        else:
            dp_time[dist_to_light][speed][max_time_till_green] = (1 / (max_time_till_green + 1)) * time_to_finish_green(
                dist_to_light, speed)
            if max_time_till_green > 0:
                best_time, best_action = None, None
                for speed_change in range(-min(MAX_SPEED_CHANGE, speed), min(MAX_SPEED_CHANGE, MAX_SPEED - speed) + 1):
                    tmp = rec(dist_to_light - speed, speed + speed_change, max_time_till_green - 1, dp_time, dp_action)
                    if best_time is None or tmp < best_time:
                        best_time = tmp
                        best_action = speed_change
                dp_time[dist_to_light][speed][max_time_till_green] += (max_time_till_green / (
                        max_time_till_green + 1)) * best_time
                dp_action[dist_to_light][speed][max_time_till_green] = best_action
    return dp_time[dist_to_light][speed][max_time_till_green]


if __name__ == '__main__':
    dp_time = [[[None for _ in range(START_MAX_TIME_TILL_GREEN + 1)] for _ in range(MAX_SPEED + 1)] for _ in
               range(START_DIST_TO_LIGHT + 1)]
    dp_action = [[[None for _ in range(START_MAX_TIME_TILL_GREEN + 1)] for _ in range(MAX_SPEED + 1)] for _ in
                 range(START_DIST_TO_LIGHT + 1)]
    best_expected_finish_time = rec(START_DIST_TO_LIGHT, START_SPEED, START_MAX_TIME_TILL_GREEN, dp_time, dp_action)

    simulation_times = list(range(NUM_SIMULATIONS)) if NUM_SIMULATIONS == START_MAX_TIME_TILL_GREEN + 1 else \
        [random.randint(0, START_MAX_TIME_TILL_GREEN + 1) for _ in range(NUM_SIMULATIONS)]
    for start_time_till_green in simulation_times:
        all_speeds = []
        time_light_crossed = None

        dist_to_light = START_DIST_TO_LIGHT
        speed = START_SPEED
        known_max_time_till_green = START_MAX_TIME_TILL_GREEN
        curr_time_till_green = start_time_till_green

        all_speeds.append(speed)

        while dist_to_light > -DIST_FROM_LIGHT_TO_GOAL:
            # print(dist_to_light, speed, curr_time_till_green)
            if time_light_crossed is None and dist_to_light < 0:
                time_light_crossed = len(all_speeds) - 1
            if curr_time_till_green == 0:
                dist_to_light -= speed
                speed = min(MAX_SPEED, speed + MAX_SPEED_CHANGE)
            elif dist_to_light == 0:
                assert speed == 0
                curr_time_till_green -= 1
            else:
                speed_change = dp_action[dist_to_light][speed][known_max_time_till_green]
                dist_to_light -= speed
                speed += speed_change
                known_max_time_till_green -= 1
                curr_time_till_green -= 1
            all_speeds.append(speed)

        tmp, = plt.plot(all_speeds, label=str(start_time_till_green))
        plt.axvline(time_light_crossed, linestyle='--', color=tmp.get_color())

    plt.xlabel("time")
    plt.ylabel("speed")
    config_dict = {
        "start_speed": START_SPEED,
        "max_speed": MAX_SPEED,
        "max_speed_change": MAX_SPEED_CHANGE,
        "dist_from_light_to_goal": DIST_FROM_LIGHT_TO_GOAL,
        "start_dist_to_light": START_DIST_TO_LIGHT,
        "upper_bound_time_till_green": START_MAX_TIME_TILL_GREEN
    }
    legend = plt.legend(title='start_time_till_green', labelspacing=0.01 * 30 / len(simulation_times))
    for label in legend.get_texts():
        label.set_fontsize(5)
    legend.get_title().set_fontsize(5)
    legend.get_frame().set_linewidth(0.0)

    plt.title(', '.join([f'{key} = {value}' for key, value in config_dict.items()]), fontsize=5)
    if SAVE:
        plt.savefig(f"simulation_{'_'.join([str(value) for value in config_dict.values()])}.pdf")
