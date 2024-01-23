class MemoryBlock:
    def __init__(self, start_address, size, reference_count=0):
        self.start_address = start_address
        self.size = size
        self.reference_count = reference_count
        self.end_address = start_address + size - 1  # Calculate end_address

    def __str__(self):
        return f"Block: start_address={self.start_address}, size={self.size}, reference_count={self.reference_count}"
