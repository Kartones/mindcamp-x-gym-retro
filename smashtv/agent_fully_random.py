import retro

import config


# Agent for testing purposes, just moves randomly without any learning or reusing the rewards
def main():
    env = retro.make(game=config.GAME, state=config.STATE, info='./data.json', scenario=config.SCENARIO,
                     record=config.RECORD, players=config.PLAYERS, inttype=retro.data.Integrations.CONTRIB)

    try:
        iterations = 0
        while True:
            observation = env.reset()
            t = 0
            iterations += 1
            total_rewards = [0] * config.PLAYERS
            info = None
            while True:
                observation, rewards, done, info, t = move_step(env, t)
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


def move_step(environment, timestep):
    action = environment.action_space.sample()
    observation, rewards, done, info = environment.step(action)

    timestep += 1
    if timestep % config.MODULO_STEPS_TO_LOG_INFO == 0:
                    if config.VERBOSITY > 1:
                        info_data = ', '.join(['{}={}'.format(k, v) for k, v in info.items()])
                        print("t={} Info: {} Actions: {}".format(timestep, info_data, action))

    return observation, rewards, done, info, timestep


if __name__ == '__main__':
    main()
