from random import randint

import retro

import config


# Simple agent that doesn't uses any RL, just tries to play its best by using a simple AI,
# just try to have the paddle always below the ball by tracking it's x coordinate
def main():
    env = retro.make(game=config.GAME, state=config.STATE, info='./data.json', scenario='./scenario.json',
                     record=config.RECORD, players=config.PLAYERS)

    try:
        iterations = 0
        while True:
            observation = env.reset()
            t = 0
            iterations += 1
            total_rewards = [0] * config.PLAYERS
            info = None
            while True:
                observation, rewards, done, info, t = move_step(env, t, info)
                env.render()
                if config.PLAYERS == 1:
                    rewards = [rewards]
                for num_player, reward in enumerate(rewards):
                    total_rewards[num_player] += reward
                    if config.VERBOSITY > 1:
                        if reward > 0:
                            print('t=%i Reward: +%g Current reward: %g' % (t, reward, total_rewards[num_player]))
                        elif reward < 0:
                            print('t=%i Penalty: -%g, Current reward: %g' % (t, reward, total_rewards[num_player]))
                if done:
                    env.render()
                    try:
                        if config.VERBOSITY > 0:
                            if config.PLAYERS > 1:
                                print("Iteration %i done: Time=%i, Reward=%r" % (iterations, t, total_rewards))
                            else:
                                print("Iteration %i done: Time=%i, Reward=%r" % (iterations, t, total_rewards[0]))
                            if config.WAIT_BETWEEN_ITERATIONS and config.MULTIPLE_ITERATIONS:
                                input("press enter to continue")
                        elif config.VERBOSITY == 0:
                            if config.WAIT_BETWEEN_ITERATIONS and config.MULTIPLE_ITERATIONS:
                                input("")
                    except EOFError:
                        exit(0)
                    if config.MULTIPLE_ITERATIONS:
                        break
                    else:
                        exit(0)
    except KeyboardInterrupt:
        exit(0)


def move_step(environment, timestep, last_info):
    # gb screen size is 160x144
    # left border is 8px
    # right border is 40px
    # play area is 112px (from pixel 8 to pixel 120)
    # but after debugging using integration GUI, ball counts from 16 to 123 and player paddle also goes from 16 to 120

    paddle_size = 24
    paddle_safe_margin = paddle_size/4

    if last_info:
        go_left = 1 if (last_info['player_x_start'] + paddle_safe_margin > last_info['ball_x']) else 0
        go_right = 1 if (last_info['player_x_end'] - paddle_safe_margin < last_info['ball_x']) else 0
    else:
        go_left = False
        go_right = False

    # Buttons for GameBoy games defined at gym-retro/retro/cores/gambatte.json
    # ["B", null, "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT", "A"]
    # Note: Ball only goes out when pressing A, and if kept pressed will always stay that way (thus the last random)
    action = [0, 0, 0, 0, 0, 0, go_left, go_right, randint(0, 1)]

    observation, rewards, done, info = environment.step(action)

    timestep += 1
    if timestep % config.MODULO_STEPS_TO_LOG_INFO == 0:
                    if config.VERBOSITY > 1:
                        info_data = ', '.join(['{}={}'.format(k, v) for k, v in info.items()])
                        print("t={} Info: {} Actions: {}".format(timestep, info_data, action))

    return observation, rewards, done, info, timestep


if __name__ == '__main__':
    main()
