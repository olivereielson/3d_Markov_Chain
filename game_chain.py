import numpy as np
from matplotlib import pyplot as plt, animation
import networkx as nx
from matplotlib.animation import FuncAnimation


class Game:

    def __init__(self, player1, player2, mental_effect, gameRange, mentalRange, draw_graph=False, P1_start=0,
                 P2_start=0):
        self.P1 = player1
        self.P2 = player2
        self.mental_effect = mental_effect
        self.draw_graph = draw_graph
        self.gameRange = gameRange
        self.mentalRange = mentalRange
        self.graph = {}
        self.P1_start = P1_start
        self.P2_start = P2_start

        self.nodes = []

        self.P1_win_relative = 0
        self.P2_win_relative = 0

        self.P1_win = 0
        self.P2_win = 0
        assert self.gameRange > 0, "Game range must be greater than 0"
        assert self.mentalRange > 0, "Mental range must be greater than 0"
        assert self.mental_effect > 0, "Mental effect for P1 must be greater than 0"
        assert self.P1 > 0, "P1 must be greater than 0"
        assert self.P2 > 0, "P2 must be greater than 0"
        assert self.P1 + self.P2 == 1, "P1 + P2 must be equal to 1"

    def create_graph(self):

        for m in range(self.mentalRange):
            self.graph[(-1, -1, self.mentalRange / 2), (self.P1_start, self.P2_start, m)] = (1 / self.mentalRange)

        for A in range(self.P1_start, self.gameRange):  # all of A's possible points
            for B in range(self.P2_start, self.gameRange):
                for z in range(self.mentalRange):  # all of the possible mental states
                    mental_modifier = self.mental_effect * ((z + 1) - ((1 + self.mentalRange) / 2))
                    prob_A = max(0, min(1, self.P1 + mental_modifier))
                    prob_B = max(0, min(1, self.P2 - mental_modifier))
                    assert prob_A >= 0, "Prob A is negative A = " + str(prob_A)
                    assert prob_B >= 0, "Prob B is negative B = " + str(prob_A)

                    total_jump_prob_A = 0
                    total_jump_prob_B = 0
                    for m in range(self.mentalRange):
                        total_jump_prob_A += 1 / (1 + abs(z - m))
                        total_jump_prob_B += 1 / (1 + abs(z - m))

                    for m in range(self.mentalRange):  # jumps to all the other mental states
                        jump_A = (prob_A * (1 / (1 + abs(z - m)))) / total_jump_prob_A
                        jump_B = (prob_B * (1 / (1 + abs(z - m)))) / total_jump_prob_B

                        if A == self.gameRange - 1:
                            self.graph[(A, B, z), (15, 0, self.mentalRange / 2)] = prob_A
                        else:
                            self.graph[(A, B, z), (A + 1, B, m)] = jump_A

                        if B == self.gameRange - 1:
                            self.graph[(A, B, z), (0, 15, self.mentalRange / 2)] = prob_B
                        else:
                            self.graph[(A, B, z), (A, B + 1, m)] = jump_B

        self.graph[(15, 0, self.mentalRange / 2), (-1, -1, self.mentalRange / 2)] = 1
        self.graph[(0, 15, self.mentalRange / 2), (-1, -1, self.mentalRange / 2)] = 1

    def createMatrix(self):
        self.nodes = list(set([x for y in self.graph.keys() for x in y]))
        matrix = np.zeros((len(self.nodes), len(self.nodes)))

        for key, value in self.graph.items():
            matrix[self.nodes.index(key[1])][self.nodes.index(key[0])] = value

        # check square
        assert matrix.shape[0] == matrix.shape[1], "Matrix is not square"
        # Check for non-Neg
        assert np.all(matrix >= 0), "Matrix has negative values"
        # Check for sum of cols (close enough)
        assert np.all(np.sum(matrix, axis=0) > 0.99), "Sum of cols is not 1"

        return matrix

    def calculate_eigenvector(self):
        matrix = self.createMatrix()
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        assert 0 == np.argmin(np.abs(eigenvalues - 1)), "no 1-eigenvector "

        eigenvector = np.real(eigenvectors[:, 0])
        normalized_eigenvector = eigenvector / np.sum(eigenvector)
        # get the index of the winning nodes
        IndexP1 = self.nodes.index((15, 0, self.mentalRange / 2))
        IndexP2 = self.nodes.index((0, 15, self.mentalRange / 2))

        self.P1_win_relative = normalized_eigenvector[IndexP1]
        self.P2_win_relative = normalized_eigenvector[IndexP2]

        self.P1_win = self.P1_win_relative / (self.P1_win_relative + self.P2_win_relative)
        self.P2_win = self.P2_win_relative / (self.P1_win_relative + self.P2_win_relative)

    def print_results(self):
        print("P1 wins relative: ", self.P1_win_relative)
        print("P2 wins relative: ", self.P2_win_relative)
        print("P1 wins: ", self.P1_win)
        print("P2 wins: ", self.P2_win)

    def draw_graph123(self, animate=False):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # turn off the backgrounds
        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        plt.tight_layout()
        ax.grid(False)
        ax.xaxis.line.set_visible(False)
        ax.yaxis.line.set_visible(False)
        ax.zaxis.line.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])

        ax.set_zlim(0, 5)

        for key, value in self.graph.items():

            if key[1][0] == 15 and key[1][1] == 0:
                ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'red', linewidth=value)
            elif key[1][0] == 0 and key[1][1] == 15:
                ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'blue',
                        linewidth=value, )
            elif key[0][0] == 15 and key[0][1] == 0:
                ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'pink', linewidth=value)
            elif key[0][0] == 0 and key[0][1] == 15:
                ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'pink', linewidth=value)
            elif key[0][0] == -10 and key[0][1] == -10:
                ax.plot([key[0][0] + 9, key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'orange',
                        linewidth=value)
            else:
                ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'green',
                        linewidth=value)

            ax.scatter(key[0][0], key[0][1], key[0][2], color='grey', alpha=0.2, s=2, )

        ax.text(15, 0, self.mentalRange / 2, "P1 Win", color='red')
        ax.text(0, 15, self.mentalRange / 2, "P2 Win", color='blue')
        ax.text(-1, -1, self.mentalRange / 2, "Start", color='black')
        ax.scatter(-1, -1, self.mentalRange / 2, color='black', )
        ax.scatter(0, 15, self.mentalRange / 2, color='black', )
        ax.scatter(15, 0, self.mentalRange / 2, color='black', )

        def update(frame):
            # Update the azimuthal angle and elevation to rotate the view
            ax.view_init(elev=10, azim=frame)
            print(f"Animating frame {frame}/{360}")
            return fig,

        if animate:
            anim = FuncAnimation(fig, update, frames=np.arange(0, 360, 2), interval=50, blit=True, )
            anim.save('game_chain.gif', dpi=80, writer='imagemagick', )
        else:
            plt.show()

    def generate_random_walk(self, start_index, num_steps=50):

        current_index = self.nodes.index(start_index)
        path = [current_index]
        for _ in range(num_steps):
            probabilities = self.createMatrix()[:, current_index]
            if np.sum(probabilities) == 0:
                break
            next_index = np.random.choice(len(probabilities), p=probabilities)
            path.append(next_index)
            current_index = next_index

        node_path = [self.nodes[i] for i in path]
        return node_path

    def animate_walk(self):
        start_node = (-1, -1, self.mentalRange / 2)  # Adjust as necessary for your graph
        path = self.generate_random_walk(start_node, num_steps=200)  # Generate the walk

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        ax.text(15, 0, self.mentalRange / 2, "P1 Win", color='red')
        ax.text(0, 15, self.mentalRange / 2, "P2 Win", color='blue')
        ax.text(-1, -1, self.mentalRange / 2, "Start", color='black')
        ax.scatter(-1, -1, self.mentalRange / 2, color='black', )
        ax.scatter(0, 15, self.mentalRange / 2, color='black', )
        ax.scatter(15, 0, self.mentalRange / 2, color='black', )

        plt.tight_layout()
        ax.grid(False)
        ax.xaxis.line.set_visible(False)
        ax.yaxis.line.set_visible(False)
        ax.zaxis.line.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])

        # Plot all graph connections lightly
        for key, value in self.graph.items():
            ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'grey', alpha=1)

        # Prepare to animate the walk

        def update(num):
            node = path[num]
            node_old = path[num - 1]

            if node_old[0] == -1 and node_old[1] == -1:
                for key, value in self.graph.items():
                    ax.plot([key[0][0], key[1][0]], [key[0][1], key[1][1]], [key[0][2], key[1][2]], 'grey', alpha=1)

            ax.scatter(node_old[0], node_old[1], node_old[2], color='grey')
            ax.plot([node_old[0], node[0]], [node_old[1], node[1]], [node_old[2], node[2]], 'red', linewidth=1)
            ax.scatter(node[0], node[1], node[2], color='red', s=5)
            ax.view_init(elev=-20, azim=num % 360)
            return fig,

        ani = FuncAnimation(fig, update, frames=len(path), blit=True, interval=200, repeat=False)
        ani.save('random_walk.gif', writer='imagemagick', fps=2)
        plt.show()

