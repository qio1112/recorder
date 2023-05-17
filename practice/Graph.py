from collections import deque


class Node:
    def __init__(self, value, other_obj):
        self.value = value
        self.other_objs = {other_obj}
        self.visited = False

    def add_obj(self, other_obj):
        self.other_objs.add(other_obj)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __str__(self):
        return f"Node({self.value}: {self.other_objs})"


class Edge:
    def __init__(self, fr: Node, to: Node):
        self.fr = fr
        self.to = to

    def __hash__(self):
        return hash((self.fr, self.to))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.fr == other.fr and self.to == other.to

    def __str__(self):
        return f"edge({str(self.fr)}->{str(self.to)})"


def get_adj_list(edges: set[Edge]):
    adj_list = {}
    for edge in edges:
        if edge.fr not in adj_list:
            adj_list[edge.fr] = set()
        adj_list[edge.fr].add(edge.to)
        if edge.to and edge.to not in adj_list:
            adj_list[edge.to] = set()
    return adj_list


def group_bfs(adj_list: dict[Node, set[Node]]):
    all_nodes = set(adj_list.keys())
    remaining = set(all_nodes)
    queue = deque()

    result = []

    while len(remaining) > 0:
        current_group = set()
        start = remaining.pop()
        start.visited = True
        queue.append(start)
        current_group.add(start)

        while len(queue) > 0:
            node = queue.popleft()
            adj_nodes = adj_list[node]
            for adj_n in adj_nodes:
                if not adj_n.visited:
                    adj_n.visited = True
                    queue.append(adj_n)
                    if adj_n in remaining:
                        remaining.remove(adj_n)
                    current_group.add(adj_n)

        result.append(current_group)

    return result


def group_tuples(tuples: list[any]):  # (a, b, info)
    edges = set()
    nodes = {}
    for t in tuples:
        if t[0] in nodes:
            fr = nodes[t[0]]
            fr.add_obj(t[2])
        else:
            fr = Node(t[0], t[2])
            nodes[t[0]] = fr
        if t[1]:
            if t[1] in nodes:
                to = nodes[t[1]]
                to.add_obj(t[2])
            else:
                to = Node(t[1], t[2])
                nodes[t[1]] = to
        else:
            to = fr
        edge1 = Edge(fr, to)
        edge2 = Edge(to, fr)
        if edge1 not in edges:
            edges.add(edge1)
        if edge2 not in edges:
            edges.add(edge2)

    adj_list = get_adj_list(edges)
    return group_bfs(adj_list)


if __name__ == "__main__":
    ts = [('e1', 'e2', '2000'), ('e2', None, '2000'), ('e3', 'e4', '2021'), ('e2', 'e3', '2023'), ('e5', None, '2021'),
          ('e6', 'e7', '2023'), ('e7', None, '2024'), ('e7', 'e5', '2000')]
    groups = group_tuples(ts)
    for group in groups:
        node_strs = [str(node) for node in group]
        print(f"{','.join(node_strs)}")

