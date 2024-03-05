from typing import List
from enum import Enum
from utils.TypeBitSet import TypedBitSet

# Define a base class for value getters
class ValueGetter:
    def get_encoding_value(self):
        pass
# Define an enumeration for different states of a smart lock
class SmartLockStateEnum(ValueGetter, Enum):
    UnlockedByMotor = (0*8+0, "Unlocked by motor", None)
    UnlockedByCylinder = (0*8+1, "Unlocked by cylinder", None)
    Locked = (0*8+2, "Locked", None)
    MechanicalJamming = (0*8+3, "Mechanical Jamming", None)
    CoverTampering = (0*8+4, "Cover Tampering", None)
    MagneticTampering = (0*8+5, "Magnetic Tampering", None)
    PinInPlace = (0*8+6, "Pin In Place", None)
    HandleInPlace = (0*8+7, "Handle in place", None)
    HighTemperature = (1*8+0, "High Temperature", None)
    LowTemperature = (1*8+1, "Low Temperature", None)
    HighVibration = (1*8+2, "High Vibration", None)
    UnlockingMotorTimeout = (1*8+3, "Unlocking Motor Timeout", None)
    LowBattery = (1*8+4, "Low Battery", None)
    LowLowBattery = (1*8+5, "Low Low Battery", None)
    NfcError = (1*8+6, "NFC Error", None)
    I2CError = (1*8+7, "I2C Error", None)
    NfcSuccessUnlocking = (2*8+0, "NFC Success Unlocking", None)
    NfcFailureUnlocking = (2*8+1, "NFC Failure Unlocking", None)
    BleSuccessUnlocking = (2*8+2, "BLE Success Unlocking", None)
    BleFailureUnlocking = (2*8+3, "BLE Failure Unlocking", None)

    def __init__(self, offset, display_name, description):
        self.m_offset = offset
        self.m_display_name = display_name
        self.m_description = description

    def get_encoding_value(self):
        return self.m_offset

    def get_display_name(self):
        return self.m_display_name

    def get_description(self):
        return self.m_description
    
# Define states of the smart lock using the enumeration
class SmartLockState(TypedBitSet):
    def __init__(self, inputs= None):
        """
        Initializes a SmartLockState instance.

        Args:
            inputs (BitSet, optional): Optional initial BitSet to set the initial state. Defaults to None.
        """
        if inputs is None:
            # If no inputs are provided, initialize with all states from SmartLockStateEnum
            super().__init__(SmartLockStateEnum, list(SmartLockStateEnum))
        else:
            # Otherwise, initialize with the provided inputs
            super().__init__(SmartLockStateEnum, list(SmartLockStateEnum), inputs)

    def __eq__(self, other):
        """
        Overrides the equality comparison.

        Args:
            other (SmartLockState): Another SmartLockState instance.

        Returns:
            bool: True if both instances are equal, False otherwise.
        """
        if isinstance(other, SmartLockState):
            return self.m_data.bits == other.m_data.bits
        return False

    def __hash__(self):
        """
        Overrides the hash function.

        Returns:
            int: Hash value of the SmartLockState.
        """
        return hash(tuple(self.m_data.bits))

    def __str__(self):
        """
        Overrides the string representation.

        Returns:
            str: String representation of the SmartLockState.
        """
        value_names = [value.name for value in self.values()]
        return f"[{', '.join(value_names)}]"

    def get_encoding_value(self):
        """
        Placeholder method for getting the encoding value.

        Returns:
            None
        """
        pass

    def get_display_name(self):
        """
        Placeholder method for getting the display name.

        Returns:
            None
        """
        pass

    def get_description(self):
        """
        Placeholder method for getting the description.

        Returns:
            None
        """
        pass
