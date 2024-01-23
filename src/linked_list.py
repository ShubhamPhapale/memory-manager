class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, item):
        new_node = Node(item)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def remove(self, item):
        current = self.head
        previous = None

        while current:
            if current.data == item:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                return True  # Item removed
            previous = current
            current = current.next

        return False  # Item not found

    # ... (implement other linked list methods as needed)
    
