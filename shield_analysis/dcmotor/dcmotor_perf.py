import sys
sys.path.append("../")

from DDPG import *
from main import *
import os.path
from Environment import Environment
from shield import Shield
import argparse

def dcmotor (learning_method, number_of_rollouts, simulation_steps, learning_eposides, critic_structure, actor_structure, train_dir,\
            nn_test=False, retrain_shield=False, shield_test=False, test_episodes=100):
  A = np.matrix([[0.98965,1.4747e-08],
    [7.4506e-09,0]
    ])

  B = np.matrix([[128],
    [0]
    ])

  #intial state space
  s_min = np.array([[-1.0],[-1.0]])
  s_max = np.array([[ 1.0],[ 1.0]])

  #sample an initial condition for system
  x0 = np.matrix([
                    [random.uniform(s_min[0, 0], s_max[0, 0])], 
                    [random.uniform(s_min[1, 0], s_max[1, 0])],
                  ])
  print ("Sampled initial state is:\n {}".format(x0))  

  Q = np.matrix("1 0 ; 0 1")
  R = np.matrix(".0005")

  x_min = np.array([[-1.5],[-1.5]])
  x_max = np.array([[ 1.5],[ 1.5]])
  u_min = np.array([[-1.]])
  u_max = np.array([[ 1.]])

  env = Environment(A, B, u_min, u_max, s_min, s_max, x_min, x_max, Q, R)

  args = { 'actor_lr': 0.000001,
           'critic_lr': 0.00001,
           'actor_structure': actor_structure,
           'critic_structure': critic_structure, 
           'buffer_size': 1000000,
           'gamma': 0.99,
           'max_episode_len': 100,
           'max_episodes': learning_eposides,
           'minibatch_size': 64,
           'random_seed': 6553,
           'tau': 0.005,
           'model_path': train_dir+"model.chkp",
           'enable_test': nn_test, 
           'test_episodes': test_episodes,
           'test_episodes_len': 5000}
  actor = DDPG(env, args)

  #################### Shield #################
  model_path = os.path.split(args['model_path'])[0]+'/'
  linear_func_model_name = 'K.model'
  model_path = model_path+linear_func_model_name+'.npy'

  shield = Shield(env, actor, model_path, force_learning=retrain_shield)
  shield.train_shield(learning_method, number_of_rollouts, simulation_steps, explore_mag = 0.0004, step_size = 0.0005)
  if shield_test:
    shield.test_shield(test_episodes, 5000, mode="single")

  ################# Metrics ######################
  # actor_boundary(env, actor, 2000, 1000)
  # shield.shield_boundary(2000, 1000)
  terminal_err = 1e-2
  sample_steps = 2000
  sample_ep = 1000
  print "---\nterminal error: {}\nsample_ep: {}\nsample_steps: {}\n---".format(terminal_err, sample_ep, sample_steps)
  # dist_nn_lf = metrics.distance_between_linear_function_and_neural_network(env, actor, shield.K, terminal_err, sample_ep, sample_steps)
  # print "dist_nn_lf: ", dist_nn_lf
  nn_perf = metrics.neural_network_performance(env, actor, terminal_err, sample_ep, sample_steps)
  print "nn_perf", nn_perf
  shield_perf = metrics.linear_function_performance(env, shield.K_list[0], terminal_err, sample_ep, sample_steps)
  print "shield_perf", shield_perf

  actor.sess.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Running Options')
  parser.add_argument('--nn_test', action="store_true", dest="nn_test")
  parser.add_argument('--retrain_shield', action="store_true", dest="retrain_shield")
  parser.add_argument('--shield_test', action="store_true", dest="shield_test")
  parser.add_argument('--test_episodes', action="store", dest="test_episodes", type=int)
  parser_res = parser.parse_args()
  nn_test = parser_res.nn_test
  retrain_shield = parser_res.retrain_shield
  shield_test = parser_res.shield_test
  test_episodes = parser_res.test_episodes if parser_res.test_episodes is not None else 100
  
  dcmotor("random_search", 100, 200, 0, [240,200], [280,240,200], "../ddpg_chkp/dcmotor/240200280240200/", nn_test=nn_test, retrain_shield=retrain_shield, shield_test=shield_test, test_episodes=test_episodes)