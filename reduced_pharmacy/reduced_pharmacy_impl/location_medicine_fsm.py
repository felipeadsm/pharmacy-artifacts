# coding=utf-8
from transitions import Machine

# When you need to generate FSM graphs, uncomment this line and comment the top line
# from transitions.extensions import GraphMachine as Machine


class LocationMedicineFSM:
    """
    Class responsible for controlling the states related to the location of the medicines

    """

    states = [
        {'name': 'Initial'},
        {'name': 'MoveToSection', 'on_enter': ['current_state', 'moving_to_section']},
        {'name': 'FindMarker', 'on_enter': ['current_state', 'finding_marker']},
        {'name': 'MoveToPosRef', 'on_enter': ['current_state', 'moving_to_pos_ref']},
        {'name': 'ConfirmMarker', 'on_enter': ['current_state', 'confirmation_marker']},
        {'name': 'Fail', 'on_enter': ['current_state', 'localiza_fail']},
        {'name': 'Finish', 'on_enter': ['current_state', 'localiza_finish']}
    ]

    # Lógica de zerar a variável no after dos success e dos fail adicionada
    transitions = [
        {'trigger': 'initializing',         'source': 'Initial',           'dest': 'MoveToSection'},

        {'trigger': 'move_to_section',      'source': 'MoveToSection',     'dest': 'FindMarker',       'conditions': ['validate_database'],  'after': ['reset_flags']},
        {'trigger': 'find_marker',          'source': 'FindMarker',        'dest': 'MoveToPosRef',     'conditions': ['found_marker'],       'after': ['reset_flags']},
        {'trigger': 'move_to_pos_ref',      'source': 'MoveToPosRef',      'dest': 'ConfirmMarker',    'conditions': ['validate_operation'], 'after': ['reset_flags']},
        {'trigger': 'confirm_marker',       'source': 'ConfirmMarker',     'dest': 'Finish',           'conditions': ['confirmed_marker'],   'after': ['reset_flags']},

        {'trigger': 'repeat_move_to_section',      'source': 'MoveToSection',     'dest': '=',         'unless': ['limit_end']},
        {'trigger': 'repeat_find_marker',          'source': 'FindMarker',        'dest': '=',         'unless': ['limit_end']},
        {'trigger': 'repeat_move_to_pos_ref',      'source': 'MoveToPosRef',      'dest': '=',         'unless': ['limit_end']},
        {'trigger': 'repeat_confirm_marker',       'source': 'ConfirmMarker',     'dest': '=',         'unless': ['limit_end']},

        {'trigger': 'fail_move_to_section', 'source': 'MoveToSection',     'dest': 'Fail',             'conditions': ['limit_end'], 'after': ['reset_flags']},
        {'trigger': 'fail_find_marker',     'source': 'FindMarker',        'dest': 'Fail',             'conditions': ['limit_end'], 'after': ['reset_flags']},
        {'trigger': 'fail_confirm_marker',  'source': 'ConfirmMarker',     'dest': 'Fail',             'conditions': ['limit_end'], 'after': ['reset_flags']},
        {'trigger': 'fail_move_to_pos_ref', 'source': 'MoveToPosRef',      'dest': 'Fail',             'conditions': ['limit_end'], 'after': ['reset_flags']},

        {'trigger': 'finish_with_fail',     'source': 'Fail',              'dest': 'Finish'},
    ]

    def __init__(self):
        """
        Constructor of the class

        Returns:
            The class object
        """
        # Flag correspondente ao fim do processo de localização do medicamento
        self.finished = False

        # Variáveis associada a contagem das tentativas de encontrar o marker
        self.attempts = 0
        self.limit_attempts = 2

        # # Inicialização da máquina de estado
        self.machine = Machine(model=self,
                               states=LocationMedicineFSM.states,
                               transitions=LocationMedicineFSM.transitions,
                               initial='Initial')

        # RoboChart variables
        self.move_to_section_var = None
        self.find_marker_var = None
        self.move_to_pos_ref_var = None
        self.confirm_marker_var = None

    # Methods related to what will be executed in the states
    def current_state(self):
        """
        Method to display the current state of the Localiza Machine

        Returns:
            None
        """
        print("LocationMedicineFSM;{}".format(self.state))

    def moving_to_section(self):
        """
        Method of robot movement to the quadrant for marker identification

        Returns:
            None
        """
        if self.move_to_section_var is False:
            self.attempts = self.attempts + 1
            return False

        return True

    def finding_marker(self):
        """
        Method to search for marker

        Returns:
            bool: True or False
        """
        if self.find_marker_var is False:
            self.attempts = self.attempts + 1
            return False

        return True


    def moving_to_pos_ref(self):
        """
        Method of robot movement to the reference position find_marker_var by marker

        Returns:
            None
        """
        if self.move_to_pos_ref_var is False:
            self.attempts = self.attempts + 1
            return False

        return True

    def confirmation_marker(self):
        """
        Method of marker confirmation

        Returns:
            bool: True or False
        """
        if self.confirm_marker_var is False:
            self.attempts = self.attempts + 1
            return False

        return True

    # Methods related to the existing conditions for transitions to occur
    def localiza_fail(self):
        """
        Method to update the value of the attempt variable

        Returns:
            None
        """
        self.attempts = 0

    def localiza_finish(self):
        """
        Method linked to the finish state of the Localiza Machine, returns that it has finished its activity

        Returns:
            bool: True
        """
        self.finished = True
        return self.finished

    def validate_operation(self):
        """
        Validation Method of the approximation performed in the previous method

        Returns:
            bool: True or False
        """

        return self.move_to_pos_ref_var

    def validate_database(self):
        """
        Method to validate operation with a database
        """

        return self.move_to_section_var

    def found_marker(self):
        """
        Method that returns whether the marker was find_marker_var or not

        Returns:
            bool: True or False
        """

        return self.find_marker_var

    def confirmed_marker(self):
        """
        Method that returns whether the marker was confirmed or not

        Returns:
            bool: True or False
        """

        return self.confirm_marker_var

    def limit_end(self):
        """
        Method to process whether the number of attempts has been reached

        Returns:
            bool: True or False
        """
        if self.attempts >= self.limit_attempts:
            return True
        else:
            return False

    def reset_flags(self):
        self.attempts = 0

    # Method for automatically executing available/possible transitions in each of the states
    def run(self):
        """
        Method for automatic execution of available/viable transitions in each of the states
        """
        available_transitions = self.machine.get_triggers(self.state)
        available_transitions = available_transitions[len(LocationMedicineFSM.states):]

        print("Transições disponíveis: {}".format(available_transitions))

        for current_transition in range(len(available_transitions)):
            method = getattr(self, available_transitions[current_transition])
            may_method = getattr(self, 'may_' + available_transitions[current_transition])
            if may_method():
                print("Transição executada: {}".format(available_transitions[current_transition]))
                method()

if __name__ == '__main__':
    # filter(lambda x: not (x.startswith('to_') or x.startswith('is_') or x.startswith('may_')), [method_name for method_name in dir(location_medicine_fsm) if callable(getattr(location_medicine_fsm, method_name))])
    location_medicine_fsm = LocationMedicineFSM()

    while location_medicine_fsm.state != 'Finish':
        location_medicine_fsm.run()

    print("Fim do processo de localização")

