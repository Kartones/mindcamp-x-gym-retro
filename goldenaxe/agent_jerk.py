"""
Code adapted from from https://www.noob-programmer.com/openai-retro-contest/jerk-agent-algorithm/
"""
import random

import gym
import numpy as np
import retro

import config

# See below explanation, similar to decaying epsilon greedy
EXPLOIT_BIAS = 0.25
TOTAL_TIMESTEPS = int(1e6)


def main():
    env = retro.make(game=config.GAME, info=config.INFO, state=config.STATE, scenario=config.SCENARIO,
                     record=config.RECORD, players=config.PLAYERS, inttype=retro.data.Integrations.CONTRIB)
    env = TrackedEnv(env)
    new_sequence = True
    solutions = []
    while True:
        if new_sequence:
            # Except for first run, apply similar to a decaying epsilon greedy:
            # The exploit bias is fixed but the more the agent walks the less probable will try an exploration
            if (solutions and random.random() < EXPLOIT_BIAS + env.total_steps_ever / TOTAL_TIMESTEPS):
                print("calculating exploitation")
                solutions = sorted(solutions, key=lambda x: np.mean(x[0]))
                best_pair = solutions[-1]
                new_rew = exploit(env, best_pair[1])
                best_pair[0].append(new_rew)
                print('replayed best with reward %f' % new_rew)
                continue
            else:
                print("Env reset. Exploration")
                env.reset()
                new_sequence = False
        rew, new_sequence = move(env, 70)
        if not new_sequence and rew <= 0:
            # print('backtracking due to negative reward: %f' % rew)
            _, new_sequence = move(env, 30, left=True)
        if new_sequence:
            print("New Iteration. Reward: {}".format(env.total_reward))
            solutions.append(([max(env.reward_history)], env.best_sequence()))


def move(env, num_steps, left=False, attack_prob=3.0 / 10.0, attack_repeat=10):
    """
    Move right or left for a certain number of steps, attacking periodically.
    attack_repeat limits how many of num_steps can be about attacking
    """
    total_reward = 0.0
    done = False
    steps_taken = 0
    # Number of steps to spend attacking
    attacking_steps_left = 0

    while not done and steps_taken < num_steps:
        # A is jumping, B is attacking, C is special magic
        # ["B", null, "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT", "A", ...]
        action = np.zeros((12,), dtype=np.bool)
        # 6 == LEFT
        action[6] = left
        # 7 == RIGHT
        action[7] = not left
        if attacking_steps_left > 0:
            # 0 == B == attacking
            action[0] = True
            attacking_steps_left -= 1
        else:
            env.render()
            if random.random() < attack_prob:
                attacking_steps_left = attack_repeat - 1
                action[0] = True
        # No need to keep the observation (1st param), and not using the info (4th param)
        _, reward, done, info = env.step(action)
        total_reward += reward
        # print("info:", info)
        steps_taken += 1
        if done:
            break
    return total_reward, done


def exploit(env, sequence):
    """
    Replay an action sequence. Returns the final cumulative reward.
    """
    env.reset()
    done = False
    idx = 0
    while not done:
        env.render()
        if idx >= len(sequence):
            # Force breaking out
            done = True

            # pad with NOPs if needed. This only works for games with time limits (timeouts)
            # _, _, done, _ = env.step(np.zeros((12,), dtype='bool'))
        else:
            _, _, done, _ = env.step(sequence[idx])
        idx += 1
    return env.total_reward


class TrackedEnv(gym.Wrapper):
    """
    An environment that tracks the current trajectory and the total number of timesteps ever taken.
    """
    def __init__(self, env):
        super(TrackedEnv, self).__init__(env)
        self.action_history = []
        self.reward_history = []
        self.total_reward = 0
        self.total_steps_ever = 0

    def best_sequence(self):
        """
        Get the prefix of the trajectory with the best cumulative reward.
        """
        max_cumulative = max(self.reward_history)
        for i, rew in enumerate(self.reward_history):
            if rew == max_cumulative:
                return self.action_history[:i+1]
        raise RuntimeError('unreachable')

    def reset(self, **kwargs):
        self.action_history = []
        self.reward_history = []
        self.total_reward = 0
        return self.env.reset(**kwargs)

    def step(self, action):
        self.total_steps_ever += 1
        self.action_history.append(action.copy())
        obs, rew, done, info = self.env.step(action)
        self.total_reward += rew
        self.reward_history.append(self.total_reward)
        return obs, rew, done, info


if __name__ == '__main__':
    main()
