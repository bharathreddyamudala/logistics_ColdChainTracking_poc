from typing import List, TypeVar
from enum import Enum
from functools import reduce

class BitSet:
    def __init__(self):
        # Initialize an empty list to store the indices of set bits
        self.bits = []

    def get(self, index):
        # Check if the specified index is in the list of set bits
        return index in self.bits

    def set(self, index):
         # Set the bit at the specified index by adding it to the list
        self.bits.append(index)

    def clear(self, index):
        # Clear the bit at the specified index if it exists in the list
        if index in self.bits:
            self.bits.remove(index)

class ValueGetter(Enum):
    def get_encoding_value(self):
        pass

T = TypeVar('T', bound=ValueGetter)

class TypedBitSet:
    def __init__(self, source_enum: type, values: List, bs: BitSet = None):
         # Initialize a BitSet to store the set values
        self.m_data = BitSet()
         # Store the enumeration type
        self.m_source_enum = source_enum
        # Store the list of values from the enumeration
        self.m_values = values
        # If an initial BitSet is provided, merge its bits with the current BitSet
        if(bs != None):
            self.m_data.bits = list(set(self.m_data.bits) | set(bs.bits))
           
    
    
    
    def is_set(self, val: T):
        """
        Checks if a value is set in the TypedBitSet.

        Args:
            val (T): Value from the enumeration.

        Returns:
            bool: True if the value is set, False otherwise.
        """
        return self.m_data.get(val.get_encoding_value())

    def set(self, val: T):
        """
        Sets a value in the TypedBitSet.

        Args:
            val (T): Value from the enumeration.
        """
        self.m_data.set(val.get_encoding_value())

    def clear(self, val: T):
        """
        Clears a value in the TypedBitSet.

        Args:
            val (T): Value from the enumeration.
        """
        self.m_data.clear(val.get_encoding_value())

    def values(self):
        """
        Returns the set of values currently set in the TypedBitSet.

        Returns:
            set: Set of values.
        """
        return reduce(lambda acc, e: acc | {e} if self.is_set(e) else acc, self.m_values, set())

    def length(self):
        """
        Returns the length of the TypedBitSet.

        Returns:
            int: Length of the TypedBitSet.
        """
        max_val = max([e.get_encoding_value() for e in self.m_values], default=-1)
        return max_val + 1

    def to_bit_set(self):
        """
        Returns the underlying BitSet.

        Returns:
            BitSet: Underlying BitSet.
        """
        return self.m_data

    def to_json_value(self):
        """
        Returns the values in JSON format.

        Returns:
            list: List of values in JSON format.
        """
        return [e.name for e in self.values()]

    def __eq__(self, other):
        """
        Overrides the equality comparison.

        Args:
            other (TypedBitSet): Another TypedBitSet instance.

        Returns:
            bool: True if both TypedBitSet instances are equal, False otherwise.
        """
        if isinstance(other, TypedBitSet):
            return self.m_data.bits == other.m_data.bits
        return False

    def __hash__(self):
        """
        Overrides the hash function.

        Returns:
            int: Hash value of the TypedBitSet.
        """
        return hash(tuple(self.m_data.bits))

    def __str__(self):
        """
        Overrides the string representation.

        Returns:
            str: String representation of the TypedBitSet.
        """
        value_names = [e.name for e in self.values()]
        return f"[{', '.join(value_names)}]"

