from graphviz import Digraph

h = Digraph()

h.node('Start', 'Start')
h.node('Player A Wins', 'Player A Wins')
h.node('Player B Wins', 'Player B Wins')
h.node('Restart', 'Restart')

h.edges([('Start', '0,0')])

for i in range(0, 11):
    for j in range(0, 11):
        h.node(f"{i},{j}", f"{i},{j}")
        h.edges([(f"{i},{j}", f"{i+1},{j}"), (f"{i},{j}", f"{i},{j+1}")])
        if i == 10:
            if j == 10:
                h.edge(f"{i+1},{j}", 'Restart')
            else:
                h.edge(f"{i+1},{j}", 'Player A Wins')
        if j == 10:
            if i == 10:
                h.edge(f"{i },{j+1}", 'Restart')
            else:
                h.edge(f"{i},{j+1}", 'Player B Wins')

h.render('game_chain.gv', view=True, format='png')