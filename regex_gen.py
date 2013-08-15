#regex generator similar to frak found on https://github.com/noprompt/frak
import string, sys, argparse, time

TIMES_VISITED = 1
TRIE_NODE_OBJ = 0


class TrieNode():
	def __init__(self, node_string = "", parent=None): #for root, "" is ndoe string
		self.node_string = node_string
		self.last_letter = node_string[-1:]
		self.len = len(self.node_string)
		self.parent = parent
		self.terminal = False
		self.children = {} #dictionary of children is nodes = key, value = [trie_node() obj, times visited]

	def get_child(self, child_name):
		return self.children[child_name][TRIE_NODE_OBJ]
	def create_child(self, child_name):
		new_node = TrieNode(node_string = child_name,parent=self)
		self.children[child_name] = [new_node, 1]
		return new_node
	def up_visits_child(self, child_name):
		self.children[child_name][TIMES_VISITED] += 1
	def get_children(self):
		return [c[TRIE_NODE_OBJ] for c in sorted(self.children.values(), key = lambda x: -x[TIMES_VISITED])]
	def has_children(self):
		return len(self.children) > 0
	def children_are_siblingless(self):
		return len(self.children) == 1
	def children_are_childless(self):
		for child in self.get_children():
			if child.has_children():
				return False
		return True

	def is_terminal(self):
		return self.terminal
	def set_terminal(self, terminal):
		self.terminal = terminal

	def insert(self, *full):
		for a in full:
			if type(a) is list:
				for elem in a:
					self.put(elem)
			if type(a) is str:
				self.put(a)
	def put(self, full):
		if full == self.node_string: #stop on reaching element
			self.set_terminal(True)
		elif full.startswith(self.node_string):
			next = full[:self.len+1]
			if self.children.has_key(next):
				self.up_visits_child(next)
				nextNode = self.get_child(next)
				nextNode.put(full)
			else:
				new_node = self.create_child(next)
				new_node.put(full)

	def __str__(self):
		children = self.get_children()
		child_strings = ["\n" + ("\033[36m" if child.is_terminal() else "\x1b[0m") + "-"*(child.len-1) + str(child) for child in children]
		return self.last_letter + string.join(child_strings, "") + "\x1b[0m"
	def regex(self):
		regex_to_add = self.last_letter
		if self.has_children():
			if self.is_terminal():
				if self.children_are_siblingless():
					if self.children_are_childless():
						regex_to_add += ""
					else:
						regex_to_add += "("
				else:
					if self.children_are_childless():
						regex_to_add += "["
					else:
						regex_to_add += "(?:"
			if self.children_are_siblingless():
				regex_to_add += self.get_children()[0].regex()
			else:
				if self.children_are_childless():
					regex_to_add += "["
					regex_to_add += string.join([c.last_letter for c in self.get_children()], "")
					regex_to_add += "]"
				else:
					regex_to_add += "(?:"
					regex_to_add += string.join([c.regex() for c in self.get_children()], "|")
					regex_to_add += ")"
			if self.is_terminal():
				if self.children_are_siblingless():
					if self.children_are_childless():
						regex_to_add += "?"
					else:
						regex_to_add += ")?"
				else:
					if self.children_are_childless():
						regex_to_add += "]?"
					else:
						regex_to_add += ")?"
		
		return regex_to_add

parser = argparse.ArgumentParser(description = 'Generate a (relatively) short regex based on a list of words')
parser.add_argument('words', metavar = 'word', type = str, nargs = '*', help = 'words to be parsed in',default=[])
parser.add_argument('--in_file', '-i', metavar = 'input_file', type = str, nargs = '?', help = "input file, as lines of words", default=None)
args = parser.parse_args()

if __name__ == '__main__':
	now = time.time()
	root = TrieNode()
	i=0
	if args.in_file:
		f = open(args.in_file)
		for line in f:
			i+=1
			if i < 4000000:
				root.insert(line.strip())
	root.insert(args.words)
	print root.regex()
	print time.time() - now