from gym import Wrapper
import numpy
import retro

import config


class EnvWithMemory(Wrapper):

    def __init__(self, env):
        super(EnvWithMemory, self).__init__(env)
        self.reset_history()

    def reset(self):
        return self.env.reset()

    def reset_history(self):
        self.current_iteration = 0
        self.actions = []
        self.rewards = []
        self.times = []
        self.actions.append([])
        self.rewards.append(0.0)
        self.times.append(0)

    def init_iteration(self):
        self.current_iteration += 1
        self.actions.append([])
        self.rewards.append(0.0)
        self.times.append(0)

    def best_iteration(self):
        max_reward = max(self.rewards)
        for iteration, reward in enumerate(self.rewards):
            if reward == max_reward:
                return iteration, reward, self.actions[iteration], self.times[iteration]

    def step(self, action):
        self.actions[self.current_iteration].append(
            list(action).copy() if type(action) is numpy.ndarray else action.copy()
        )
        observation, reward, done, info = self.env.step(action)
        self.rewards[self.current_iteration] += reward
        self.times[self.current_iteration] += 1
        return observation, reward, done, info

    @property
    def current_time(self):
        return self.times[self.current_iteration]

    @property
    def current_reward(self):
        return self.rewards[self.current_iteration]


# Simple agent that on the first iteration applies a simple AI (see agent_non_rl.py), and afterwards reuses it,
# applying an Epsilon Greedy algorithm to decide at each step if to follow the best previous iteration, or to experiment
# when experimenting just randomly chooses an alternate path
class EpsilonGreedyAgent():

    # Specific config for this agent

    # % of exploration
    EPSILON = 0.005

    # If true, will ignore normal epsilon and calculate time-based, favoring more exploration at first
    USE_DECAYING_EPSILON = True

    def __init__(self):
        self.best_iteration = 0
        self.best_reward = 0.0
        self.best_actions = []
        self.best_time = 0

    def run(self):
        self.env = EnvWithMemory(retro.make(game=config.GAME, state=config.STATE, info="./data.json",
                                            scenario=config.SCENARIO, record=config.RECORD, players=config.PLAYERS,
                                            inttype=retro.data.Integrations.CONTRIB))
        first_iteration = True

        try:
            while True:
                observation = self.env.reset()
                if first_iteration:
                    first_iteration = False
                else:
                    self.env.init_iteration()
                info = None
                while True:
                    observation, reward, done, info = self.move_step(info)
                    self.env.render()
                    if done:
                        self.env.render()
                        try:
                            if config.VERBOSITY > 0 and config.WAIT_BETWEEN_ITERATIONS and config.NUM_ITERATIONS > 1:
                                    input("press enter to continue")
                        except EOFError:
                            self.exit_agent()
                        # To test the learning, at least run twice to run exploration vs exploitation
                        if self.env.current_iteration < config.NUM_ITERATIONS - 1:
                            self.best_iteration, self.best_reward, self.best_actions, self.best_time = \
                                self.env.best_iteration()
                            print("Iteration:{}, reward:{}, time:{}. Best iteration:{}, reward:{}, time:{}".format(
                                self.env.current_iteration, self.env.current_reward, self.env.current_time,
                                self.best_iteration, self.best_reward, self.best_time))
                            break
                        else:
                            self.exit_agent()
        except KeyboardInterrupt:
            self.exit_agent()

    def exit_agent(self):
        print("-----")
        print("Total iterations: {}".format(self.env.current_iteration))
        print("Best iteration: {}".format(self.best_iteration))
        print("Num actions: {}".format(len(self.best_actions)))
        print("Time: {}".format(self.best_time))
        print("Total reward: {}".format(self.best_reward))

        exit(0)

    def move_step(self, last_info):
        if self.env.current_iteration > 0:
            return self._epsilon_greedy_movement(last_info)
        else:
            return self._random_movement()

    def _epsilon_value(self):
        if self.USE_DECAYING_EPSILON:
            # with 1 it is too much "explorative", becomes practically random
            return 0.1 / (self.env.current_time + 1)
        else:
            return self.EPSILON

    def _epsilon_greedy_movement(self, last_info):
        probability = numpy.random.random()
        if probability < self._epsilon_value():
            return self._random_movement()
        else:
            if self.env.current_time < self.best_time:
                action = self.best_actions[self.env.current_time]
            else:
                # We reached end of previous list of actions
                return self._random_movement()

        observation, rewards, done, info = self.env.step(action)

        return observation, rewards, done, info

    def _random_movement(self):
        # ["B", null, "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT", "A"]
        action = [0, 0, 0, 0, numpy.random.randint(0, 2), numpy.random.randint(0, 2), numpy.random.randint(0, 2),
                  numpy.random.randint(0, 2), numpy.random.randint(0, 2)]
        observation, rewards, done, info = self.env.step(action)

        return observation, rewards, done, info


if __name__ == "__main__":
    agent = EpsilonGreedyAgent()
    agent.run()
