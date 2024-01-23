from memory_block import MemoryBlock
from linked_list import LinkedList
from linked_list import Node

MEMORY_SIZE = 64 * 1024 * 1024  # 64 MB

allocated_blocks = LinkedList()
free_blocks = LinkedList()

most_recently_allocated_block = None  # Initially no blocks allocated

variables = {}

def initialize_memory():
    free_block = MemoryBlock(0, MEMORY_SIZE)
    free_blocks.head = Node(free_block)

def allocate(size):
    """Allocates a memory block of the given size.

    Args:
        size (int): The size of the block to allocate in bytes.

    Returns:
        int: The starting address of the allocated block, or -1 if allocation fails.
    """

    global most_recently_allocated_block
    
    current_block = free_blocks.head
    while current_block:
        if current_block.data.size >= size:
            # Found a suitable block
            allocated_block = MemoryBlock(current_block.data.start_address, size)
            allocated_block.reference_count = 1

            # Update free block if it's larger than the allocated size
            if current_block.data.size > size:
                current_block.data.start_address += size
                current_block.data.size -= size
            else:
                free_blocks.remove(current_block)

            allocated_blocks.append(allocated_block)
            # If allocation is successful, update most_recently_allocated_block
            if allocated_block:
                most_recently_allocated_block = allocated_block.start_address
            return allocated_block.start_address

        current_block = current_block.next

    # No suitable block found, try compaction
    compact_memory()

    # Retry allocation after compaction
    current_block = free_blocks.head
    while current_block:
        if current_block.data.size >= size:
            # Allocation successful after compaction
            # (allocation logic as described above)
            # If allocation is successful, update most_recently_allocated_block
            if allocated_block:
                most_recently_allocated_block = allocated_block.start_address
            return allocated_block.start_address

        current_block = current_block.next

    # Allocation failed even after compaction
    print("Error: Insufficient memory to allocate block of size", size)
    return -1
    
def merge_free_blocks():
    """Merges adjacent free blocks in the free_blocks linked list."""

    current = free_blocks.head
    while current and current.next:
        next_block = current.next

        # Check if blocks are adjacent
        if current.data.end_address == next_block.data.start_address:
            # Merge blocks
            new_block = MemoryBlock(
                start_address=current.data.start_address,
                size=current.data.size + next_block.data.size
            )

            # Remove individual blocks from the list
            free_blocks.remove(current.data)
            free_blocks.remove(next_block.data)

            # Add merged block to the list
            free_blocks.insert(new_block)

            # Update current pointer to remain in the same position
            current = free_blocks.find_node(new_block)  # Assuming you have a `find_node` function
        else:
            current = current.next   

def deallocate(variable_name):
    """Deallocates a memory block associated with the given variable name.

    Args:
        variable_name (str): The name of the variable to deallocate.
    """
    
    if variable_name in variables:
        address = variables[variable_name]  # Retrieve address from registry

        # Decrement reference count and potentially deallocate
        deallocated = False
        current_block = allocated_blocks.head  # Start with the head of the list

        while current_block:
            if current_block.data.start_address == address:
                current_block.data.reference_count -= 1
                if current_block.data.reference_count == 0:
                    # Truly deallocate the block
                    free_block = MemoryBlock(current_block.data.start_address, current_block.data.size)
                    free_blocks.append(free_block)
                    merge_free_blocks()
                    allocated_blocks.remove(current_block.data)  # Remove from allocated list
                    del variables[variable_name]  # Remove from variable registry
                    deallocated = True
                break

            current_block = current_block.next

        if not deallocated:
            print(f"Error: Cannot deallocate block associated with variable '{variable_name}'")

    else:
        print(f"Error: Variable '{variable_name}' not found")

def compact_memory():
    """Performs memory compaction to consolidate free space."""
    
    free_block_end = 0  # Initialize if not already set
    
    current_block = allocated_blocks.head
    previous_block = None
    free_block_start = None

    while current_block:
        if current_block.data.reference_count == 0:
            # Found a free block, update pointers and sizes
            if free_block_start is None:
                free_block_start = current_block.data.start_address
            current_block.data.start_address = free_block_start
            free_block_start += current_block.data.size
        else:
            # Non-free block, update previous pointer and free_block_start
            if free_block_start:
                free_block_end = free_block_start + (current_block.data.start_address - free_block_start)
                free_block = MemoryBlock(free_block_start, free_block_end - free_block_start)
                free_blocks.append(free_block)
                free_block_start = None
            previous_block = current_block

        current_block = current_block.next

    # Update pointers if any remaining free space at the end
    if free_block_start:
        free_block_end = free_block_start + (MEMORY_SIZE - free_block_start)
        free_block = MemoryBlock(free_block_start, free_block_end - free_block_start)
        free_blocks.append(free_block)

    # Adjust allocated blocks' addresses after compaction
    current_block = allocated_blocks.head
    compacted_address = free_block_end if free_block_end else 0
    while current_block:
        current_block.data.start_address = compacted_address
        compacted_address += current_block.data.size
        current_block = current_block.next

def process_input_file(filename):
    """Processes transactions from an input file.

    Args:
        filename (str): The path to the input file.
    """

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Skip blank lines and comments

            # Check for assignment or other commands
            if "=" in line:
                # Handle variable assignments and other commands containing "="
                command_and_arg = line.split(" = ", 1)  # Split at most once
                command = command_and_arg[0].strip()

                # If there's an argument, process it
                if len(command_and_arg) > 1:
                    arg = command_and_arg[1].strip()
                else:
                    arg = None

            else:
                try:
                    command, arg = line.split()  # Split for commands without "="
                except ValueError:
                    print(f"Error: Invalid transaction format in line: {line}")
                    continue

            if command == "allocate":
                try:
                    size = int(arg)
                    allocate(size)
                except ValueError:
                    print(f"Error: Invalid size value in line: {line}")

            elif command == "deallocate":
                try:
                    # Update the deallocate logic based on your implementation
                    deallocate(arg)
                except ValueError:
                    print(f"Error: Invalid address value in line: {line}")

            elif command == "print":
                try:
                    print_memory_state()
                except Exception as e:
                    print(f"Error: {e}")
                    
            # Handle variable assignments
            else:
                try:
                    variable_name, address = line.split(" = ")

                    # Check for `$` placeholder
                    if address == "$":
                        address = most_recently_allocated_block  # Use stored address
                    else:
                        address = int(address)  # Convert to numerical address if it's not a variable name

                    # Store the address in the variables dictionary
                    variables[variable_name] = address

                    # Increment reference count of the assigned block (using the address)
                    for block in allocated_blocks:
                        if block.start_address == address:
                            block.reference_count += 1
                            break

                except Exception as e:
                    print(f"Error processing variable assignment: {e}")

def print_memory_state():
    print("\nAllocated Blocks:")
    current = allocated_blocks.head  # Start with the head of the list
    while current:  # Iterate through the nodes
        print(f" - {current.data}")
        current = current.next

    print("\nFree Blocks:")
    current = free_blocks.head  # Start with the head of the list
    while current:  # Iterate through the nodes
        print(f" - {current.data}")
        current = current.next


    # Optionally, write output to another file if implemented
    # with open("memory_state.txt", "w") as f:
    #     f.write(f"Allocated Blocks:\n")
    #     for block in allocated_blocks:
    #         f.write(f" - {block}\n")
    #     f.write(f"\nFree Blocks:\n")
    #     for block in free_blocks:
    #         f.write(f" - {block}\n")

if __name__ == "__main__":
    initialize_memory()
    input_file = "transactions.txt"  # Replace with your input file name
    process_input_file(input_file)
    compact_memory()
    print("\nMemory state after compaction:")
    print_memory_state()
