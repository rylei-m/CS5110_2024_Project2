'''
Author : Adil Moujahid
Email : adil.mouja@gmail.com
Description: Simulations of Schelling's seggregation model

You will need to set up pycharm to import matplotlib.
'''

import matplotlib.pyplot as plt
import itertools
import random
import copy


class Schelling:
    def __init__(self, width, height, empty_ratio, similarity_threshold, n_iterations, colors=2):
        self.agents = None
        self.width = width
        self.height = height
        self.colors = colors
        self.empty_ratio = empty_ratio

        if isinstance(similarity_threshold, dict):
            self.similarity_thresholds = similarity_threshold
        else:
            self.similarity_thresholds = {i: similarity_threshold for i in range(1, colors + 1)}
        self.n_iterations = n_iterations

    def populate(self):
        self.empty_houses = []
        self.agents = {}
        print("Populate ",  self.width ,  self.height)
        self.all_houses = list(itertools.product(range(self.width), range(self.height)))
        print(self.all_houses)
        random.shuffle(self.all_houses)

        self.n_empty = int(self.empty_ratio * len(self.all_houses))
        self.empty_houses = self.all_houses[:self.n_empty]

        self.remaining_houses = self.all_houses[self.n_empty:]
        houses_by_color = [self.remaining_houses[i::self.colors] for i in range(self.colors)]
        print("Houses by color ", houses_by_color[0])
        for i in range(self.colors):
            dict2 = dict(zip(houses_by_color[i], [i + 1] * len(houses_by_color[i])))
            self.agents = {**self.agents, **dict2}
        print("dictionary",self.agents)

    def is_unsatisfied(self, x, y):

        myColor = self.agents[(x, y)]
        count_similar = 0
        count_different = 0

        if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
            if self.agents[(x - 1, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if y > 0 and (x, y - 1) not in self.empty_houses:
            if self.agents[(x, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
            if self.agents[(x + 1, y - 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and (x - 1, y) not in self.empty_houses:
            if self.agents[(x - 1, y)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
            if self.agents[(x + 1, y)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
            if self.agents[(x - 1, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
            if self.agents[(x, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
            if self.agents[(x + 1, y + 1)] == myColor:
                count_similar += 1
            else:
                count_different += 1

        if (count_similar + count_different) == 0:
            return False
        else:
            return float(count_similar) / (count_similar + count_different) < self.similarity_thresholds[myColor]

    def move_locations(self, neighborhood_radius=1):
        total_distance = 0
        n_swaps = 0

        for _ in range(self.n_iterations):
            n_changes = 0
            for agent in list(self.agents.keys()):
                if self.is_unsatisfied(agent[0], agent[1]):
                    new_location = self.find_new_location(agent, neighborhood_radius)
                    if new_location:
                        self.move_agent(agent, new_location)
                        n_changes += 1
                    else:
                        new_location = random.choice(self.empty_houses)
                        self.move_agent(agent, new_location)
                        n_changes += 1
            if n_changes == 0:
                break
        for iteration in range(self.n_iterations):
            unsatisfied_agents = [(agent, self.is_unsatisfied(agent[0], agent[1])) for agent in self.agents if self.is_unsatisfied(agent[0], agent[1])]
            random.shuffle(unsatisfied_agents)

            for agent, unsatisfied in unsatisfied_agents:
                swapped = False
                if unsatisfied:
                    for potential_partner, unsatisfied_partner in unsatisfied_agents:
                        if agent != potential_partner and unsatisfied_partner and self.can_swap(agent, potential_partner):
                            self.swap_agents(agent, potential_partner)
                            n_swaps += 1
                            swapped = True
                            break

                if not swapped and self.is_unsatisfied(agent[0], agent[1]):
                    agent_color = self.agents[agent]
                    empty_house = random.choice(self.empty_houses)
                    self.agents[empty_house] = agent_color
                    del self.agents[agent]
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)

            if n_swaps == 0 and all(not unsatisfied for _, unsatisfied in unsatisfied_agents):
                print(f"Stopping early after {iteration + 1} iterations due to all agents being satisfied.")
                break

        print(f"Completed iterations with {n_swaps} swaps.")

    def find_new_location(self, current_location, radius):
        x, y = current_location
        neighborhood = [
            (x + dx, y + dy)
            for dx in range(-radius, radius + 1)
            for dy in range(-radius, radius + 1)
            if 0 <= x + dx < self.width and 0 <= y + dy < self.height and (dx != 0 or dy != 0)
        ]
        random.shuffle(neighborhood)
        for new_location in neighborhood:
            if new_location in self.empty_houses:
                return new_location
        return None

    def move_agent(self, old_location, new_location):
        self.agents[new_location] = self.agents[old_location]
        del self.agents[old_location]
        self.empty_houses.remove(new_location)
        self.empty_houses.append(old_location)

    def can_swap(self, agent_a_pos, agent_b_pos):
        if agent_a_pos not in self.agents or agent_b_pos not in self.agents:
            return False

        agent_a_color = self.agents[agent_a_pos]
        agent_b_color = self.agents[agent_b_pos]
        self.agents[agent_a_pos], self.agents[agent_b_pos] = agent_b_color, agent_a_color

        satisfied_a = not self.is_unsatisfied(*agent_a_pos)
        satisfied_b = not self.is_unsatisfied(*agent_b_pos)

        self.agents[agent_a_pos], self.agents[agent_b_pos] = agent_a_color, agent_b_color

        return satisfied_a and satisfied_b
    
    def swap_agents(self, agent_a_pos, agent_b_pos):
        if agent_a_pos in self.agents and agent_b_pos in self.agents:
            self.agents[agent_a_pos], self.agents[agent_b_pos] = self.agents[agent_b_pos], self.agents[agent_a_pos]
        else:
            print(f"Attempted to swap non-existing agents at positions {agent_a_pos} and {agent_b_pos}.")
    
    def assign_wealth(self):
        for agent in self.agents:
            self.agents[agent]['wealth'] = random.randint(1, 100)

    def evaluate_desirability(self, location):
        return random.randint(1, 100)

    def move_based_on_economics(self):
        print("Attempting to move agents based on economics...")
        for agent, properties in list(self.agents.items()):
            print(f"Checking agent at {agent} with wealth {properties['wealth']}")
            if self.is_unsatisfied(agent[0], agent[1]):
                possible_moves = self.get_possible_moves(agent)
                possible_moves = sorted(possible_moves, key=lambda x: self.evaluate_desirability(x), reverse=True)
                for new_location in possible_moves:
                    if self.agents[agent]['wealth'] >= self.evaluate_desirability(new_location):
                        print(f"Agent {agent} with wealth {self.agents[agent]['wealth']} moving to {new_location} with desirability {self.evaluate_desirability(new_location)}")
                        self.move_agent(agent, new_location)
                        break

    def get_possible_moves(self, agent):
        return [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) in self.empty_houses]
    
    # def move_to_empty(self, x, y):
    #     color = self.agents[(x, y)]
    #     empty_house = random.choice(self.empty_houses)
    #     self.updated_agents[empty_house] = color
    #     del self.updated_agents[(x, y)]
    #     self.empty_houses.remove(empty_house)
    #     self.empty_houses.append((x, y))

    def plot(self, title, file_name):
        fig, ax = plt.subplots()
        agent_colors = {1: 'b', 2: 'r', 3: 'g', 4: 'c', 5: 'm', 6: 'y', 7: 'k'}
        marker_size = 150/self.width
        for agent in self.agents:
            ax.scatter(agent[0] + 0.5, agent[1] + 0.5,s=marker_size, color=agent_colors[self.agents[agent]])

        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, self.width])
        ax.set_ylim([0, self.height])
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(file_name)

    def calculate_similarity(self):
        similarity = []
        for agent in self.agents:
            count_similar = 0
            count_different = 0
            x = agent[0]
            y = agent[1]
            color = self.agents[(x, y)]
            if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
                if self.agents[(x - 1, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if y > 0 and (x, y - 1) not in self.empty_houses:
                if self.agents[(x, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
                if self.agents[(x + 1, y - 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and (x - 1, y) not in self.empty_houses:
                if self.agents[(x - 1, y)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
                if self.agents[(x + 1, y)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
                if self.agents[(x - 1, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
                if self.agents[(x, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
                if self.agents[(x + 1, y + 1)] == color:
                    count_similar += 1
                else:
                    count_different += 1
            try:
                similarity.append(float(count_similar) / (count_similar + count_different))
            except:
                similarity.append(1)
        return sum(similarity) / len(similarity)

    def calculate_similarity_for_each_type(self):
        similarity_scores = {color: [] for color in range(1, self.colors + 1)}
        
        for agent, color in self.agents.items():
            count_similar, count_different = 0, 0
            total_neighbors = count_similar + count_different
            if total_neighbors != 0:
                similarity = float(count_similar) / total_neighbors
                similarity_scores[color].append(similarity)
            else:
                similarity_scores[color].append(1)
        average_similarity = {color: sum(scores) / len(scores) if scores else 1 for color, scores in similarity_scores.items()}
        return average_similarity
    
    def print_satisfaction_percentages(self):
        average_similarity = self.calculate_similarity_for_each_type()
        for color, similarities in average_similarity.items():
            if not isinstance(similarities, list):
                similarities = [similarities]
            threshold = self.similarity_thresholds[color]
            satisfied_agents_count = sum(1 for s in similarities if s >= threshold)
            if similarities:
                satisfaction_percentage = satisfied_agents_count / len(similarities) * 100
            else:
                satisfaction_percentage = 0
            print(f"Agent Type {color}: {satisfaction_percentage:.2f}% meet or exceed the similarity threshold.")
        
def main():

    thresholds_simulation_1 = {1: 0.6, 2: 0.5}
    
    thresholds_simulation_2 = {1: 0.6, 2: 0.4}

    schelling_0 = Schelling(5, 5, 0.3, 0.3, 200, 2)
    schelling_0.populate()

    schelling_1 = Schelling(50, 50, 0.3, thresholds_simulation_1, 200, 2)
    schelling_1.populate()

    schelling_2 = Schelling(50, 50, 0.3, thresholds_simulation_2, 200, 2)
    schelling_2.populate()

    schelling_3 = Schelling(50, 50, 0.3, 0.8, 200, 2)
    schelling_3.populate()

    schelling_1.plot('Schelling Model with 2 colors: Initial State', 'schelling_2_initial.png')

    schelling_0.move_locations()
    schelling_1.move_locations()
    schelling_2.move_locations()
    schelling_3.move_locations()
    schelling_0.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 30%',
                     'schelling_0_30_final.png')
    schelling_1.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 30%',
                     'schelling_30_final.png')
    schelling_2.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 50%',
                     'schelling_50_final.png')
    schelling_3.plot('Schelling Model with 2 colors: Final State with Happiness Threshold 80%',
                     'schelling_80_final.png')


    schelling_0.print_satisfaction_percentages()
    schelling_1.print_satisfaction_percentages()
    schelling_2.print_satisfaction_percentages()
    schelling_3.print_satisfaction_percentages()


    # #Second Simulation Measuring Seggregation
    # similarity_threshold_ratio = {}
    # for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
    #     schelling = Schelling(50, 50, 0.3, i, 500, 2)
    #     schelling.populate()
    #     schelling.update()
    #     similarity_threshold_ratio[i] = schelling.calculate_similarity()
    #
    # fig, ax = plt.subplots()
    # plt.plot(similarity_threshold_ratio.keys(), similarity_threshold_ratio.values(), 'ro')
    # ax.set_title('Similarity Threshold vs. Mean Similarity Ratio', fontsize=15, fontweight='bold')
    # ax.set_xlim([0, 1])
    # ax.set_ylim([0, 1.1])
    # ax.set_xlabel("Similarity Threshold")
    # ax.set_ylabel("Mean Similarity Ratio")
    # plt.savefig('schelling_segregation.png')


if __name__ == "__main__":
    main()